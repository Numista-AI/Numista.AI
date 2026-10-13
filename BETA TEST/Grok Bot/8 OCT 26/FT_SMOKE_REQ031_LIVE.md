# FT Smoke: REQ_031 Sign-in Lockdown, LIVE (12 Oct 2026, ~7:40 PM ET)

Deploy: PR #256, commit 463150c1, live 7:23 PM ET. The header reads **Numista.AI v4.403**.
Account: Grok Bot (Testing), grokbot@numista.ai only. I never typed a PIN. The only data changes were two throwaway coins, and both are deleted. Dashboard Total Coins was **313** at the start and **313** at the end. The 2026 Morgan (qty 2) was not touched.

## BLUF
All four checks PASS on the screens. The scanned coin went into grokbot's own account, so the wrong-account risk did not happen. There's one open question for Code Reviewer and AG: when signed out, the browser blocks you before any data call is made, so I couldn't see the server refuse anything. A direct unauthenticated POST to `/api/identify_group_photo` returned **422** (missing fields), not **401**. That suggests the scan endpoint may not check sign-in before it reads the request. That needs a code check.

| # | Check | Result | What I saw |
|---|---|---|---|
| 1 | Sign-in works | PASS | The vault loaded as grokbot. It stayed signed in through 2 reloads, with no redirect to /login and no errors. |
| 2a | Add or edit when signed in | PASS | I asked Morgan to "Add one 1972-D Lincoln cent… $0.10, FT test box" and it saved (313 → 314). I edited Personal Notes to "REQ031 edit test", and the change survived a reload. |
| 2b | Refused when signed out | PASS (UI) / OPEN (server) | In incognito, `numista.ai` showed Sign In (Email + 6-digit PIN). `?route=My+Collection` and `?route=Catalog` also showed Sign In. No add, edit or chat controls were visible. Only the page shell and fonts loaded, with **no API calls**, so no 401/403 was seen. `/coins`, `/dashboard` and `/review` show the app's 404 page ("Page not found."). Those aren't real routes, so this is just information. |
| 2c | Server-side check (curl, no sign-in) | OPEN | GET `/api/identify_group_photo` returned 405. POST returned **422**, not 401. Other guessed `/api/*` paths returned 404, so I didn't find the real coin write endpoints. |
| 3 | Scan shows up in grokbot's account | PASS (with note) | I scanned PICA0017.jpg and Morgan read it as 1964-D 1 Cent. The only option offered was "Save separately", which saves directly to Coins (314 → 315, under Recently Added). Review Hub said "All Caught Up!" because this path skips Review Hub. **No wrong-account filing**: the coin landed in grokbot's Coins. |
| 4 | Normal use doesn't hit the per-user caps | PASS | I asked 5 Morgan questions in a row and reloaded Coins, Dashboard and Review Hub twice each. There was no 429 and no "too many requests", "limit" or "quota" message. The 5th reply was slow, and the tester re-sent it a few times; still no cap message. |
| 5 | Cleanup | PASS | Deleted the 1972-D cent and the 1964-D cent, both confirmed ("Coin deleted."). Undo All was not used. The total is back to 313. |

## Findings to route
1. **OPEN, check server auth:** an unauthenticated POST to `/api/identify_group_photo` returns 422 (validation) instead of 401. Please confirm that every write and scan API rejects calls with no sign-in, before validation runs. The UI lock alone can't prove that.
2. **Review Hub path:** scanning one coin only offers "Save separately" and never goes through Review Hub. To test Review Hub routing properly, we'd need a scan that is sent to review on purpose, such as an invoice scan.
3. **Pre-existing:** the Ask Morgan greeting says "312 coins", while the Dashboard says 313. Morgan's own answer said 313 plus 3 sets.

Screenshots: shots\ 01–09.
