# FOR AG CoS: Gemini independent review - 5 UX fixes vs "Morgan does everything"
Written by Grok Bot (the Grok half of the review cycle), 8 Oct 2026, about 10 AM ET.
Folder: C:\Users\ericd\Documents\MyVertexProject\BETA TEST\Grok Bot\8 OCT 26\

## ORDER TO ANTIGRAVITY CoS
Have Gemini 3.8 do an independent review of this file and write its answer to:
**GEMINI38_REVIEW_UX_VS_MORGAN_2026-10-08.md** in this same 8 OCT 26 folder.

## RULES (hard)
1. PLAN / REVIEW ONLY. No code changes, no commits, no deploy, no Firestore or collection writes. Dev branch only.
2. Gemini must open the code itself and quote the exact file:line it actually opened. Code baseline: branch `dev`, commit `e5f5760c` (8 Oct 2026 7:18 AM ET). The cited files had no uncommitted edits when Grok read them.
3. Canned or generic agreement will be REJECTED. "I agree with Grok" with no file:line proof does not count. Every AGREE needs a reason, every DISAGREE needs evidence.
4. Never print secrets or .env values. Key NAMES only.
5. Gemini's review is advisory. CoS scores it. Nothing ships without Eric's typed YES.

---

## 1. Eric's idea (as relayed by Chief of Staff)
> "Make Morgan the single interface for ALL transactions - adding coins, checking off checklists, editing, transfers, reports, selling with Certificate of Transfer codes, and so on - unless the user checks a box to opt out and use the normal menus. I don't know if Morgan is up to it yet."

Customers are mostly older collectors (60+). Eric's standing rules: no collection values or PII exposed (the only PII is email); PIN sign-in; AI changes to FACTS need Eric/admin approval.

## 2. The UX Designer's 5 fixes (mockups are in this folder: fix1..fix5 PNG)
1. **Checklist** (fix1-checklist.png): one big row per coin with its full name; big P / D / S tap buttons; replace "System of Record completion by 0.00%" with "7 of 19 collected, 12 to go". Today the boxes are about 10px and names are cut off.
2. **Bigger, darker text** (fix2-text-size.png): 18px+ text, full-width buttons. Today text is 9-11px light grey and buttons are about 25px.
3. **PIN sign-in** (fix3-pin.png): six big PIN boxes, number keypad, clear "Show PIN" button, big "Forgot your PIN?". Today the PIN dots show as garbled symbols.
4. **Menu** (fix4-menu.png): about 25 items cut to 6 - Home, My Coins, Add a Coin, Coin Programs, Help & Ask Morgan, More... (the rest under More).
5. **Add a coin** (fix5-add-coin.png): 3 choices - Take a photo, Type it in, Upload a list - plus "More ways", replacing 8 small tabs and engineer wording.

---

## 3. Morgan today - code inventory (facts from code, Grok read every line cited)
Backend = `numista_backend\`, App = `numista_mobile\lib\` (Flutter). Line numbers are at commit e5f5760c.

### 3a. There are TWO Morgan chat backends
- **`POST /api/deep_dive`** - the one the app's Morgan chat actually calls. `main.py:2715-2998`. The app calls it at `screens\ai_chat_screen.dart:398-410`.
- **`POST /api/ai/chat`** - a second, simpler Morgan in `routes\ai_routes.py:76-163` (mounted at `main.py:76,97`). Text-only, no tools. Grok found no app screen calling it. The feedback drawer calls `/api/ai/chat/stream` (`services\morgan_feedback_session.dart:299-300`), but Grok found NO `chat/stream` route anywhere in the backend Python. Possible dead call - please verify.

### 3b. Model / provider
- Google Gemini on Vertex AI, same Google Cloud project as the app (`main.py:227-230`).
- `/api/deep_dive` uses `PRIMARY_MODEL` = `GEMINI_FLASH_MODEL` (`main.py:223`), default "gemini-3.8-flash" (`config\__init__.py:24`).
- `/api/ai/chat` uses `DEFAULT_CHAT_MODEL` then `FALLBACK_CHAT_MODEL` (`ai_routes.py:46-71`; `config\__init__.py:33-34`, fallback default "gemini-3.5-flash-lite" at `:26`). Temperature 0.3 (`ai_routes.py:63`).

### 3c. System prompt
- deep_dive: "You are Morgan, the friendly AI numismatic guide owl..." `main.py:2893-2912`. It includes the user's full inventory, coin knowledge base, vector RAG chunks and last 8 chat turns (`main.py:2899`, `2822-2827`).
- ai/chat: "You are Morgan, an expert AI numismatic assistant..." `ai_routes.py:88`, plus collector profile (`:91-96`), knowledge context (`:99-103`), portfolio value and profit/loss (`:105-116`).
- Shared knowledge block `services\morgan_knowledge.py:21-29` hard-codes transfer instructions ("NEVER state that users cannot transfer coins", 3-step Lateral Transfer with 6-digit Claim PIN).

### 3d. Can Morgan DO things, or only answer? -> It can do 3 things today
Tools declared to Gemini at `main.py:2914-2965`:
| Tool | What it does | Code |
|---|---|---|
| `add_coin_to_collection` | Creates a new coin document | declared `2915-2935`, runs `execute_add_coin` `2303-2534`, write at `2510` |
| `update_coin_in_collection` | Changes Storage, Condition, Cost, Personal Notes only | declared `2936-2950`, runs `2579-2637`, write at `2633` |
| `undo_add_coin` | **Hard-deletes** a coin document | declared `2951-2961`, runs `2640-2655`, delete at `2651` |
- Tool calls are executed at `main.py:2975-2984`, then a second model call writes the reply (`2986-2992`).
- `batch_add_coins` exists (`2537-2576`) but is NOT given to Morgan as a tool.
- **Morgan has NO tool for:** checking off a checklist slot, deleting an older coin on purpose, transfers, selling / Certificate of Transfer codes, reports / appraisal PDF, sets. For transfers it only explains steps (`morgan_knowledge.py:23-27`).

### 3e. Does it read the user's own collection? -> Yes, all of it
- deep_dive loads every coin doc for the signed-in owner (`main.py:2756-2758`), up to 2,000 full items (`scan_service\collection_inventory.py:19`), and puts it in the prompt as JSON (`main.py:2790`, `2899`).
- That JSON includes each coin's AI estimated value and cost (`collection_inventory.py:60,105,156,175`). /api/ai/chat adds portfolio value and profit/loss (`ai_routes.py:110-116`). So collection values ARE sent to the model on every chat turn. They stay inside Google Cloud and are not shown to other users, but this should be checked against Eric's "no values exposed" rule and Privacy Mode (REQ_026).

### 3f. Is there a confirm-before-write step? -> NO for typed chat. YES for group photos.
- The prompt tells the model to write immediately: "invoke add_coin_to_collection immediately with smart defaults" (`main.py:2909`), "NEVER... send them to another page" (`2908`). Tools run with no user tap (`2975-2984`).
- The app shows an "Added to Binder" card AFTER the write, with a small Undo button (`ai_chat_screen.dart:747-802`; text 10-13px).
- **Update with no coin_id picks a coin for you:** the one added in the last 10 minutes, else the most recently created coin (`main.py:2598-2621`). This can edit the wrong coin.
- **Undo can delete ANY coin the model names**, not just a recent one. The description says "recently added" (`2953`) but the code deletes whatever coin_id it gets (`2650-2651`). The model can see every coin_id in the inventory (`2790`). Hard delete, no soft delete, no trash.
- **Good pattern already exists (reuse this):** group photo ID is "proposal-only" and does not write (`main.py:5026-5027`); the app shows a proposal card with "Save as set" / "Save separately" (`ai_chat_screen.dart:1169-1230`), a cost-split preview with "Confirm & Save" (`1390-1554`, preview endpoint `main.py:5213`), then commits via `/api/commit_group_photo` with token check (`main.py:5307-5316`). "Undo All" asks first (`ai_chat_screen.dart:1053-1090`). Binder scan also has analyze then confirm steps (`main.py:3908`, `4606-4619`).

### 3g. Auth / IDOR scoping
- deep_dive verifies the Firebase token and takes the owner from the token, not the body (`main.py:2722-2735`, owner rule `2668-2682`). A body email that does not match is logged and ignored (`2737-2743`). Tools receive that owner key (`2980-2984`), so they only touch `users/{owner}/coins`. **Scoping is good.**
- /api/ai/chat uses `get_current_user` (`routes\deps.py:64-72`). But it keys Firestore by **uid** (`ai_routes.py:82,107,128`) while the coin collection is keyed by **email** (`main.py:2668-2682`). So its portfolio stats probably come back empty for normal users (not tested live). Its error message returns raw exception text (`ai_routes.py:71`). Client field `context_override` is pasted into the system prompt (`ai_routes.py:120-121`).
- `POST /api/v1/rag/query` has **no auth at all** and calls the model (`main.py:167-180`).
- Write endpoints a Morgan "do it for me" flow would want to reuse, and their auth today:
  - Token-checked: `/api/commit_group_photo` (`5316`), `/api/identify_group_photo` (`5038`), `/api/identify_coin_photo` (`5579`), `/api/transfer/initiate` (`10966-10978`), `/api/transfer/claim` (`10994-11005`), `/api/transfer/sell-direct` (`11044-11050`), `/api/transfer/undo-sale` (`11070-11076`), `/api/export/appraisal-pdf` (`11158-11168`), `/api/collection/clear` (`7935-7944`, needs typed "DELETE").
  - **No token check found in the function** (trusts `user_email` from the request body): `/api/checklist/add_coins` (`7783-7784`, body field `7774`, write path `7839`), `/api/review/commit` (`3000-3007`), `/api/confirm_binder_scan` (`4606-4607`), `/api/analyze_binder_scan` (`3908-3913`). These must be locked (REQ_031 API Lockdown is queued) before Morgan wraps them.

### 3h. Rate limits and cost controls
- The only limiter is a tracker that **only logs, never blocks** (`logging_config.py:113`, default 60/min at `:150`). It keys on a `user_email` query parameter (`main.py:122-129`); deep_dive sends email in the body, so Morgan calls are not counted at all.
- No per-user daily cap, no token budget, no max-message length found in deep_dive or ai/chat.
- Each chat turn that uses a tool = 2 model calls (`main.py:2967`, `2988`), each carrying the whole inventory (up to 2,000 items). Big collections = big prompts, slow and costly per action.
- Some words in a question ("buy", "released", "ordered", "is there"...) start a background web scraper thread per message (`main.py:2841-2879`). No cap.
- Greysheet price lookup during add has a 1-second timeout (`main.py:2411-2433`) - good.

### 3i. Logging / audit trail
- deep_dive logs a hashed owner and inventory counts, no raw email (`main.py:2807-2814`) - good.
- A successful tool call is NOT logged server-side. Added coins carry a provenance entry with the user's words and "recorded_by: Morgan AI Assistant" (`main.py:2394-2403`, `2506-2507`) - good start.
- Updates write no history (`2626-2633`). Deletes leave nothing (`2651`).
- Chat transcripts are saved by the APP (client side) to `users/{uid}/ai_chat_sessions` (`ai_chat_screen.dart:92-94`, `459-467`), not by the server, so they are not a tamper-proof audit record. Guests are not saved (`460`).

### 3j. REQ_024 (last 5-10 eBay SOLD sales shown in-app by Morgan)
- **Planned only, not built.** REQ_024 was PLAN ONLY (REGISTRY completed 29 Sep, `OUTBOX\DONE_024_Make_Every_Claim_True_PLAN.md:6,13-18`). REQ_024A (plan v1.1) is still queued in INBOX.
- Blocker: eBay Marketplace Insights (sold data) is restricted and the license bars using eBay data to feed AI without consent (`PROCESSED\REQ_024_PLAN_ONLY_Make_Every_Claim_True.md:22-24`).
- In code today: only an outside link to eBay sold search (`numista_mobile\lib\services\epn_service.dart:135-139`, `screens\my_collection_screen.dart:4373`) and an active-listings search `GET /api/ebay/search` (`main.py:10659-10669`). REQ_028 removed the "integration" claims from the front door (`OUTBOX\DONE_028_Front_Door_Truth.md:23-27`).

### 3k. What Morgan looks like in the app
- **Both a page and a pop-out.** Full page "AI Deepdive" (`screens\base_layout.dart:372-380`); on screens 800px+ it opens as a pop-out panel instead (`base_layout.dart:277-281`, `1004`; `widgets\morgan_chat_popout.dart:132`). Floating Morgan button (`base_layout.dart:585`) and sidebar button (`847`).
- **Startup greeter with "take me to" tiles already exists**: Home, My Collection, Chat with Morgan, Coin Programs, Receipt scan, Spreadsheet upload (`widgets\morgan_greeter.dart:129-189`), with an opt-out "Don't greet me on startup" (`services\morgan_prefs.dart:42-52`).
- Step-by-step guides exist (`widgets\morgan_guides.dart:18-287`).
- **Voice:** read-aloud works on web only (`services\tts_voice_service.dart:20`; app says "not available on mobile yet", `ai_chat_screen.dart:916-919`). **No speech-to-text** package in `pubspec.yaml`. Voice setting is a "Phase 4 placeholder" (`morgan_prefs.dart:54-62`).

### 3l. Morgan-related REQs in Grok CoS to Antigravity
(Folder found at `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\Grok CoS to Antigravity\`, not under OneDrive.)
- REQ_033 EXECUTE (queued): "6 wrong facts live in AI chat's reference library".
- REQ_034 / REQ_036 (queued plans): checklist fixes and smart slot matching; facts change only when Morgan (SME) AND Gemini/AG agree.
- REQ_035 (queued plan): AI Training Board disputes.
- REQ_032 (queued plan): Older User Onboarding - directly relevant to these UX fixes.
- REQ_031 P0 (queued): API Lockdown - must land before any AI write expansion.
- F1 fact verification: RERUN5 Batch 1 PARTIAL PASS, 23 of 48 accepted; hard hold, nothing live (`OUTBOX\GEMINI38_TODAY.md`, 7 Oct entry).
- **No REQ exists for "Morgan as the interface for transactions."**

---

## 4. Grok scores
Value = for 60+ users. Effort/risk = S / M / L.

| # | Idea | Value 60+ | Effort / risk | Depends on | Security / privacy | Order |
|---|---|---|---|---|---|---|
| 2 | Bigger darker text, full-width buttons | HIGH - every screen | M / low (layout overflow on small phones; many hard-coded 10-13px sizes, e.g. `ai_chat_screen.dart:776,787,793,802`) | Shared theme sizes first | None | **1** |
| 3 | PIN sign-in fix | HIGH - if they cannot sign in nothing else matters; garbled dots is a bug | S-M / low-med (auth screen) | REQ_025 lockout (done) must stay | Keep guess lockout. "Show PIN" off by default and auto-hides. "Forgot PIN" must not say whether an email has an account | **1 (tie)** |
| 1 | Checklist big rows, "7 of 19" | HIGH - checklists are the core hobby | M / med (34 programs) | REQ_034 + REQ_036 slot data and matching; counts must be right | Counts only, no values. Checklist add endpoint has no token check (`main.py:7783-7784`) - fix in REQ_031 | **2** |
| 4 | Menu 25 -> 6 | HIGH - fewer choices | M / med (users lose a feature they used) | Route map; Help & Ask Morgan entry | Admin items must be hidden by role on the server, not just by menu | **3** |
| 5 | Add a coin: 3 big choices | HIGH | M / low-med | REQ_022 photo-add bugs; existing photo/type/upload endpoints | Upload endpoints must be token-locked (binder scan has none, `main.py:3908,4606`) | **4** |
| 6 | **Morgan-first, default ON, for ALL transactions (Eric's idea as stated)** | Long-term HIGH, **today LOW or negative** (wrong writes erode trust fast with older users) | **L / HIGH** | Confirm-before-write, server audit log, soft delete + undo, rate/cost caps, REQ_031 lockdown, tools for checklist/transfer/sell/reports (none exist), accuracy gates (F1 23/48), speech-to-text | Writes with no confirm today; undo hard-deletes any coin; values sent to model; client-supplied chat history in prompt; no blocking rate limit | **Not now** |
| 6b | **Hybrid: Morgan front-and-center helper that PROPOSES, big Confirm card, on top of the simplified UI, opt-out box** | HIGH | M (phase 1 S-M) | Same as above but phased | Writes only through the same locked endpoints the menus use, after a tap | **5, phased** |

### Grok's honest view on Eric's idea
Eric is right about the direction: older collectors would rather say "I got a 2026 D dime" than hunt through 25 menu items. But **I disagree with making Morgan the default for all transactions now.** Reasons, from the code:
1. **Wrong writes are likely and silent.** Morgan adds without asking (`main.py:2909`), edits "the most recent coin" if it is unsure (`2618-2621`), and can hard-delete any coin (`2651`). A 70-year-old who says "take off the 1921 Morgan" could lose the wrong record and not notice.
2. **Facts are not yet trustworthy.** F1 is 23 of 48 on the very first batch; REQ_033 lists 6 wrong facts live in the chat library. Eric's own rule says AI changes to facts need approval. Morgan writing coin details (series, theme, variety via catalog resolution, `2328-2346`) is a fact-adjacent write.
3. **Most transactions have no Morgan tool at all** (checklist, transfer, sell / Certificate of Transfer codes, reports). Building and securing each is L effort.
4. **Cost and speed.** Two model calls per action, each with the whole collection. A simple tap-to-check P/D/S on the checklist is instant and free; through Morgan it is several seconds and paid.
5. **People who cannot put it into words** are exactly the people a big-button UI helps. Typed chat is hard for them; there is no voice input yet.
6. **Discoverability.** A chat box hides what the app can do. Six big buttons show it.
7. **Prompt injection.** The app sends chat history and a "collection_context" block that go straight into the prompt (`main.py:2804-2805`, `2822-2827`). Invoice/photo text could carry instructions. With write tools, that is a real risk.
8. **Audit and undo are thin.** No server log of tool calls, no history on edits, deletes are permanent.

### Failure modes and the fix for each (for the hybrid)
| Failure | Fix |
|---|---|
| Misreads request, writes wrong data | Morgan only PROPOSES. Big confirm card in plain words: "Add 1 coin: 2026-D Roosevelt Dime, in a cardboard holder. [YES, ADD IT] [NO, CHANGE IT]". Server rejects a write without a one-time confirm token tied to that card |
| Wrong facts | Morgan may only fill fields from the catalog record; any catalog/fact change goes to the admin review queue (Eric's rule) |
| Edits/deletes the wrong coin | Never guess the target; show the coin's photo and name on the card. Delete = move to Trash for 30 days, never hard delete |
| Cost / latency | Send a short summary, not the whole collection; look up only matching coins. Daily per-user cap that BLOCKS. Remove the keyword-triggered scraper from chat |
| Cannot articulate | Morgan offers 3-4 big suggestion buttons ("Add a coin", "Check off a coin", "What is my coin worth?") and "Take me there" |
| Accessibility | Add speech-to-text (hold-to-talk) and read-back on mobile; 18px+ text on cards |
| Audit / undo | Server-side action log per user (who, what, before/after, which chat message, model name). Undo button on every confirmation for 30 days |
| Prompt injection | Do not paste client-supplied history/context as instructions; treat file text as data; tools only callable after a human tap; writes go through the same token-locked endpoints as the menus |
| Discoverability | Keep the 6-item menu visible. Morgan is a helper, not a replacement |
| Values / PII | Do not send values or cost to the model unless the user asks a value question; honor Privacy Mode |

### Recommended path
- **Now (UX sprint):** Fix 2 (text/buttons) + Fix 3 (PIN), then Fix 1 (checklist, after REQ_034/036 data), Fix 4 (menu), Fix 5 (add coin). Fold into REQ_032 Older User Onboarding.
- **Gate 0 before ANY Morgan expansion:** REQ_031 API Lockdown done (incl. checklist/add_coins, review/commit, binder scan, rag/query); a blocking per-user rate/cost cap on deep_dive; server action log; soft delete. Also turn OFF Morgan's write-without-confirm today (`main.py:2909` instruction + `2975-2984`) - that is a current risk, not a future one.
- **Phase 1 - Read-only Q&A + "Take me to":** Morgan answers and navigates ("Take me to my Kennedy halves checklist") using the existing greeter tiles and guides. No writes. Opt-out box. Add speech-to-text.
- **Phase 2 - Morgan drafts, user taps Confirm, with Undo:** start with Add Coin and Check Off a Slot only, reusing the group-photo proposal/confirm pattern. Then Edit. Transfers/Selling LAST and always with the existing PIN/claim screens, never from chat alone.
- **Phase 3 - Morgan-first default ON:** only after measured gates pass: F1 fact verification fully passed and REQ_033 fixed; 30 days of Phase 2 with under 1% undo/correction rate on Morgan-drafted actions; cost per action within budget; Eric types YES. Opt-out checkbox stays forever.

---

## 5. Questions Gemini MUST answer (in GEMINI38_REVIEW_UX_VS_MORGAN_2026-10-08.md)
1. For EACH of the 7 rows in the score table (fixes 1-5, Morgan-first, Hybrid): AGREE or DISAGREE with Value, Effort/risk and Order, with your own reason. If you disagree, give your score.
2. AGREE or DISAGREE with the phased plan (Gate 0, Phase 1, 2, 3) and the Phase 3 gates. Would you change the order of tools in Phase 2?
3. **Verify every file:line claim in section 3** by opening the file. For each, write CONFIRMED (quote the line) or WRONG (give the correct line). In particular verify:
   a. `main.py:2909` and `2975-2984` - writes happen with no confirm.
   b. `main.py:2618-2621` - update falls back to the most recent coin.
   c. `main.py:2640-2652` - undo hard-deletes any coin_id.
   d. `main.py:7783-7784`, `3000-3007`, `3908`, `4606` - no token check in those write endpoints. If there is auth elsewhere (middleware, Cloud Run IAM, gateway), show where.
   e. `logging_config.py:113` - rate tracker never blocks.
   f. No backend route exists for `/api/ai/chat/stream` (called at `morgan_feedback_session.dart:300`).
   g. `ai_routes.py:82,107` keys by uid vs `main.py:2668-2682` keys by email.
4. List anything Grok MISSED: other Morgan endpoints, other AI write paths (e.g. invoice parsing, import, AI Trainer), any existing confirm or audit code.
5. Flag the security risks of AI-performed writes in THIS codebase: prompt injection paths (chat_history, collection_context, Personal Notes, invoice/photo text), IDOR, cost abuse, value leakage to the model, deletes.
6. Is sending ai_estimated_value / cost / portfolio value to the model on every turn consistent with Eric's "no collection values exposed" rule and Privacy Mode (REQ_026)? Recommend.
7. For 60+ users specifically: is voice input a must-have before Phase 2? Yes/no and why.

## 6. Output format for Gemini
- File: `GEMINI38_REVIEW_UX_VS_MORGAN_2026-10-08.md`, this folder.
- Top: model name, start and finish time (ET), list of files you opened.
- Section per question above, numbered the same.
- Plain English. Short sentences. No marketing words.
- Reminder: generic or canned agreement will be rejected by CoS.
