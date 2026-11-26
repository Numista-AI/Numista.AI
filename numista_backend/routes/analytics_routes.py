"""
routes/analytics_routes.py
--------------------------
Phase 1 Morgan Analytics Co-Pilot endpoint (`POST /api/analytics/morgan`).
Zero LLM arithmetic: Morgan translates user questions into deterministic
tool calls over an in-request `vault_snapshot` (single Firestore read/turn).
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from routes.deps import (
    db,
    get_current_user,
    genai_client,
    genai_types,
    MODEL_FLASH,
    check_and_increment_dual_rate_cap,
)
from services.analytics_tools import (
    build_vault_snapshot,
    find_duplicates,
    query_vault_aggregate,
    simulate_spot_prices,
)

logger = logging.getLogger("numista_backend.analytics_routes")

analytics_router = APIRouter(tags=["Analytics & Morgan Analytics"])

ANALYTICS_FREE_MONTHLY_CAP = 10
ANALYTICS_GLOBAL_DAILY_CAP = 5000


class MorganAnalyticsRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=600)
    advanced_mode: bool = False
    sim_gold: float = 2650.0
    sim_silver: float = 31.5
    sim_platinum: float = 960.0
    sim_palladium: float = 1020.0
    history: List[Dict[str, str]] = Field(default_factory=list)


class MorganAnalyticsResponse(BaseModel):
    reply: str
    table: Optional[List[Dict[str, Any]]] = None
    action_coin_ids: List[str] = Field(default_factory=list)
    action_label: Optional[str] = None
    suggested_followups: List[str] = Field(default_factory=list)
    tools_used: List[str] = Field(default_factory=list)
    fallback_used: bool = False


def _load_vault_snapshot(uid: str, advanced_mode: bool) -> List[Dict[str, Any]]:
    """Single-read vault fetch per Morgan Analytics turn."""
    docs_iter = db.collection("users").document(uid).collection("coins").stream()
    raw_docs = [(doc.id, doc.to_dict() or {}) for doc in docs_iter if (doc.to_dict() or {}).get("status") != "sold"]  # R3
    return build_vault_snapshot(raw_docs, advanced_mode=advanced_mode)


def _execute_tool_call(
    tool_name: str,
    args: Dict[str, Any],
    vault_snapshot: List[Dict[str, Any]],
    req: MorganAnalyticsRequest,
) -> Dict[str, Any]:
    if tool_name == "query_vault_aggregate":
        return query_vault_aggregate(
            vault_snapshot,
            filters=args.get("filters"),
            group_by=args.get("group_by", "none"),
            metrics=args.get("metrics"),
        )
    if tool_name == "simulate_spot_prices":
        return simulate_spot_prices(
            vault_snapshot,
            gold=float(args.get("gold", req.sim_gold)),
            silver=float(args.get("silver", req.sim_silver)),
            platinum=float(args.get("platinum", req.sim_platinum)),
            palladium=float(args.get("palladium", req.sim_palladium)),
            filters=args.get("filters"),
        )
    if tool_name == "find_duplicates":
        return find_duplicates(
            vault_snapshot,
            include_sets=bool(args.get("include_sets", False)),
            min_unit_value=float(args.get("min_unit_value", 0.0)),
        )
    return {"error": f"Unknown tool: {tool_name}"}


def _deterministic_fallback(
    req: MorganAnalyticsRequest, vault_snapshot: List[Dict[str, Any]]
) -> MorganAnalyticsResponse:
    """Graceful deterministic fallback if Gemini is unavailable or times out."""
    q = req.query.lower()
    if "duplicate" in q:
        res = find_duplicates(vault_snapshot)
        groups = res["duplicate_groups"][:10]
        coin_ids = [cid for g in groups for cid in g["coin_ids"]]
        return MorganAnalyticsResponse(
            reply=(
                f"I found {len(res['duplicate_groups'])} duplicate group(s) with "
                f"${res['total_recoverable_value']:,.2f} in recoverable value."
            ),
            table=groups,
            action_coin_ids=coin_ids,
            action_label=f"View {len(coin_ids)} duplicates in My Collection" if coin_ids else None,
            suggested_followups=[
                "What is my total silver melt value if silver hits $50?",
                "Break down my collection by metal",
            ],
            tools_used=["find_duplicates"],
            fallback_used=True,
        )

    if any(w in q for w in ["spot", "silver", "gold", "melt", "what if", "$"]):
        res = simulate_spot_prices(
            vault_snapshot,
            gold=req.sim_gold,
            silver=req.sim_silver,
            platinum=req.sim_platinum,
            palladium=req.sim_palladium,
        )
        return MorganAnalyticsResponse(
            reply=(
                f"At Gold ${req.sim_gold:,.2f}/oz and Silver ${req.sim_silver:,.2f}/oz, "
                f"your simulated vault value is ${res['simulated_total']:,.2f} "
                f"({res['delta_pct']:+.2f}% vs. baseline ${res['baseline_total']:,.2f}). "
                f"Bullion share: {res['bullion_share_pct']:.1f}%, Numismatic share: {res['numismatic_share_pct']:.1f}%."
            ),
            suggested_followups=[
                "Show my loose duplicates",
                "Break down my collection by grading service",
            ],
            tools_used=["simulate_spot_prices"],
            fallback_used=True,
        )

    agg = query_vault_aggregate(vault_snapshot, group_by="program_series")
    cov = agg["coverage"]
    top_groups = agg["groups"][:8]
    return MorganAnalyticsResponse(
        reply=(
            f"Your vault has {cov['total']} coin(s) ({cov['priced']}/{cov['total']} priced, "
            f"{cov['with_cost']}/{cov['total']} with cost basis). Here is the breakdown by series:"
        ),
        table=top_groups,
        action_coin_ids=agg["matching_coin_ids"][:50],
        suggested_followups=[
            "What if silver hits $50 and gold hits $3,500?",
            "Find my loose duplicates",
        ],
        tools_used=["query_vault_aggregate"],
        fallback_used=True,
    )


@analytics_router.post("/api/analytics/morgan", response_model=MorganAnalyticsResponse)
async def api_morgan_analytics(
    req: MorganAnalyticsRequest,
    user: Dict[str, Any] = Depends(get_current_user),
):
    uid = user.get("uid")
    if not uid:
        raise HTTPException(status_code=401, detail="Authentication required.")

    # Enforce starter quota for free users (Pro / Founding bypass handled via user claims/tier)
    is_pro = bool(
        user.get("is_pro")
        or user.get("founding_member")
        or str(user.get("tier") or "").lower() in {"pro", "founding", "admin"}
    )
    if not is_pro:
        allowed, remaining = check_and_increment_dual_rate_cap(
            uid=uid,
            feature_key="morgan_analytics",
            user_limit=ANALYTICS_FREE_MONTHLY_CAP,
            global_limit=ANALYTICS_GLOBAL_DAILY_CAP,
        )
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Monthly starter quota reached for Morgan Analytics. Upgrade to Pro for unlimited queries.",
            )

    vault_snapshot = _load_vault_snapshot(uid, advanced_mode=req.advanced_mode)

    if genai_client is None or genai_types is None:
        return _deterministic_fallback(req, vault_snapshot)

    tool_declarations = genai_types.Tool(
        function_declarations=[
            genai_types.FunctionDeclaration(
                name="query_vault_aggregate",
                description="Filter and group the user's coin vault to compute counts, total_value, net_liq, melt_value, and cost_basis.",
                parameters={
                    "type": "object",
                    "properties": {
                        "filters": {"type": "object"},
                        "group_by": {
                            "type": "string",
                            "enum": [
                                "none",
                                "metal",
                                "denomination",
                                "program_series",
                                "grading_service",
                                "retailer",
                                "storage_location",
                            ],
                        },
                    },
                },
            ),
            genai_types.FunctionDeclaration(
                name="simulate_spot_prices",
                description="Simulate total collection value at hypothetical Gold, Silver, Platinum, and Palladium spot prices.",
                parameters={
                    "type": "object",
                    "properties": {
                        "gold": {"type": "number"},
                        "silver": {"type": "number"},
                        "platinum": {"type": "number"},
                        "palladium": {"type": "number"},
                        "filters": {"type": "object"},
                    },
                    "required": ["gold", "silver"],
                },
            ),
            genai_types.FunctionDeclaration(
                name="find_duplicates",
                description="Find canonical duplicate coin groups and calculate recoverable value.",
                parameters={
                    "type": "object",
                    "properties": {
                        "include_sets": {"type": "boolean"},
                        "min_unit_value": {"type": "number"},
                    },
                },
            ),
        ]
    )

    system_instruction = (
        "You are Morgan Analytics, Numista.AI's quantitative collection analyst. "
        "NEVER perform arithmetic in your head—ALWAYS call one of the provided deterministic tools "
        "to compute numbers from the user's vault. Always cite data coverage (e.g. X/Y priced) if relevant. "
        f"Active simulator baseline: Gold=${req.sim_gold}/oz, Silver=${req.sim_silver}/oz."
    )

    tools_used: List[str] = []
    last_table: Optional[List[Dict[str, Any]]] = None
    action_ids: List[str] = []

    try:
        contents: List[Any] = [req.query]
        config = genai_types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[tool_declarations],
            temperature=0.1,
        )

        response = await asyncio.wait_for(
            asyncio.to_thread(
                genai_client.models.generate_content,
                model=MODEL_FLASH,
                contents=contents,
                config=config,
            ),
            timeout=15.0,
        )

        # Single tool-round execution
        fn_calls = getattr(response, "function_calls", None) or []
        if fn_calls:
            tool_responses = []
            for fc in fn_calls[:3]:
                t_name = fc.name
                t_args = dict(fc.args or {})
                tools_used.append(t_name)
                result = _execute_tool_call(t_name, t_args, vault_snapshot, req)

                if isinstance(result.get("groups"), list):
                    last_table = result["groups"][:10]
                elif isinstance(result.get("duplicate_groups"), list):
                    last_table = result["duplicate_groups"][:10]
                    action_ids = [
                        cid for g in last_table for cid in g.get("coin_ids", [])
                    ]
                if not action_ids and isinstance(result.get("matching_coin_ids"), list):
                    action_ids = result["matching_coin_ids"][:50]

                tool_responses.append(
                    genai_types.Part.from_function_response(
                        name=t_name,
                        response=result,
                    )
                )

            contents.append(response.candidates[0].content)
            contents.append(genai_types.Content(role="tool", parts=tool_responses))

            final_resp = await asyncio.wait_for(
                asyncio.to_thread(
                    genai_client.models.generate_content,
                    model=MODEL_FLASH,
                    contents=contents,
                    config=genai_types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.2,
                    ),
                ),
                timeout=15.0,
            )
            reply_text = (getattr(final_resp, "text", None) or "").strip()
        else:
            reply_text = (getattr(response, "text", None) or "").strip()

        if not reply_text:
            return _deterministic_fallback(req, vault_snapshot)

        return MorganAnalyticsResponse(
            reply=reply_text,
            table=last_table,
            action_coin_ids=action_ids,
            action_label=(
                f"View {len(action_ids)} matching coins in My Collection"
                if action_ids
                else None
            ),
            suggested_followups=[
                "What if silver hits $50 and gold hits $3,500?",
                "Show my loose duplicates",
            ],
            tools_used=tools_used,
            fallback_used=False,
        )
    except Exception as exc:
        logger.warning(f"Morgan Analytics LLM error, using deterministic fallback: {exc}")
        return _deterministic_fallback(req, vault_snapshot)
