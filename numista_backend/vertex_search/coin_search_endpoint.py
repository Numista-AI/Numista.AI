"""
coin_search_endpoint.py
Vertex AI Search endpoint — registered on the FastAPI app in main.py.

This module is imported at the bottom of main.py via:
    from vertex_search.coin_search_endpoint import register_coin_search
    register_coin_search(app)
"""

from __future__ import annotations
import os
from fastapi import FastAPI, HTTPException

_SEARCH_PROJECT_NUMBER = "568985927038"
_SEARCH_LOCATION       = "global"
_SEARCH_ENGINE_ID      = "numista-coin-search"
_search_client         = None   # lazy-init


def _get_search_client():
    global _search_client
    if _search_client is None:
        from google.cloud import discoveryengine_v1 as de
        _search_client = de.SearchServiceClient()
    return _search_client


def _extract_struct(struct_data) -> dict:
    """Convert a protobuf Struct to a plain Python dict."""
    out = {}
    if not struct_data:
        return out
    try:
        for key, value in struct_data.items():
            kind = value.WhichOneof("kind")
            if kind == "string_value":
                out[key] = value.string_value
            elif kind == "number_value":
                out[key] = value.number_value
            elif kind == "bool_value":
                out[key] = value.bool_value
            else:
                out[key] = str(value)
    except Exception:
        pass
    return out


def register_coin_search(app: FastAPI) -> None:
    """Attach /api/coin_search to the given FastAPI app."""

    @app.get("/api/coin_search")
    async def coin_search(
        q: str,
        page_size: int = 10,
        offset: int = 0,
    ):
        """
        Semantic search over the Numista coin reference library.
        Open endpoint — no auth required (reference data is public).

        Query examples:
          ?q=Morgan+dollar+Carson+City
          ?q=Walking+Liberty+half+dollar+1940s
          ?q=first+year+Sacagawea+golden+dollar

        Returns ranked results with AI-generated summary snippet.
        """
        if not q or not q.strip():
            raise HTTPException(status_code=400, detail="Query 'q' is required")

        q = q.strip()
        page_size = max(1, min(int(page_size), 25))

        try:
            from google.cloud import discoveryengine_v1 as de

            client = _get_search_client()
            serving_config = (
                f"projects/{_SEARCH_PROJECT_NUMBER}"
                f"/locations/{_SEARCH_LOCATION}"
                f"/collections/default_collection"
                f"/engines/{_SEARCH_ENGINE_ID}"
                f"/servingConfigs/default_config"
            )

            request = de.SearchRequest(
                serving_config=serving_config,
                query=q,
                page_size=page_size,
                offset=offset,
                query_expansion_spec=de.SearchRequest.QueryExpansionSpec(
                    condition=de.SearchRequest.QueryExpansionSpec.Condition.AUTO,
                ),
                spell_correction_spec=de.SearchRequest.SpellCorrectionSpec(
                    mode=de.SearchRequest.SpellCorrectionSpec.Mode.AUTO,
                ),
                content_search_spec=de.SearchRequest.ContentSearchSpec(
                    snippet_spec=de.SearchRequest.ContentSearchSpec.SnippetSpec(
                        return_snippet=True,
                        max_snippet_count=2,
                    ),
                    summary_spec=de.SearchRequest.ContentSearchSpec.SummarySpec(
                        summary_result_count=3,
                        include_citations=False,
                        ignore_adversarial_query=True,
                        ignore_non_summary_seeking_query=True,
                    ),
                ),
            )

            response = client.search(request=request)

            results = []
            for hit in response.results:
                doc = hit.document
                sd  = _extract_struct(doc.struct_data)

                snippet = ""
                try:
                    if hit.chunk_info and hit.chunk_info.content:
                        snippet = hit.chunk_info.content
                except Exception:
                    pass

                results.append({
                    "id":             doc.id,
                    "program_name":   sd.get("program_name", ""),
                    "coin_year":      sd.get("coin_year", ""),
                    "coin_name":      sd.get("coin_name", ""),
                    "denomination":   sd.get("denomination", ""),
                    "category":       sd.get("category", ""),
                    "mint_marks":     sd.get("mint_marks", ""),
                    "metal":          sd.get("metal", ""),
                    "designer":       sd.get("designer", ""),
                    "notes":          sd.get("notes", ""),
                    "image_url":      sd.get("image_url", ""),
                    "content":        sd.get("content", ""),
                    "snippet":        snippet,
                })

            summary = ""
            try:
                if response.summary:
                    summary = response.summary.summary_text or ""
            except Exception:
                pass

            total = getattr(response, "total_size", len(results))
            print(f"[coin_search] q={q!r} -> {len(results)} results")

            return {
                "query":   q,
                "total":   total,
                "offset":  offset,
                "results": results,
                "summary": summary,
            }

        except Exception as e:
            err = str(e)
            print(f"[coin_search] ERROR: {err}")
            if "NOT_FOUND" in err or "does not exist" in err.lower():
                return {
                    "query":   q, "total": 0, "offset": offset,
                    "results": [], "summary": "",
                    "error": "Search index is warming up. Please try again shortly.",
                }
            raise HTTPException(status_code=500, detail=f"Search error: {err}")
