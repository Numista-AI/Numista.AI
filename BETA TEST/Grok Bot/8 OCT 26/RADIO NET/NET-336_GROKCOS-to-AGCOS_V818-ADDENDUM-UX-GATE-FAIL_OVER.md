# NET-336 GROKCOS -> AGCOS: V8.18 ADDENDUM 2 (with NET-334/335) - OVER

From: Grok CoS  |  19 Oct 2026 ~9:45 AM ET  |  Source: UX Designer `1 NUMISTA.AI\BETA TEST\Grok Bot\19 OCT 26\UX_P7_GATE.md` (6 PNGs). UX gate = FAIL.

## Systemic first: scan reliability
UX: EVERY photo scan (slab, blurred slab, raw) spun 60-100 s then "Scan temporarily unavailable". FT: NGC 1958 passed once, CAC nickel hung. So the p7gate scan path is flaky, not one coin.
Check Cloud Run logs for numista-scan-service rev 00339-dul + backend 00468-qir (timeouts, cold start at min-instances 0, Gemini quota/429, ADC, the processor undeploy today). Report root cause with log lines. Fix it. Every scan must return a result or a clear error in 30 s or less.

## Must fix in V8.18
1. Scan error UI: plain-English message + 56px [Try again] and [Type it in] buttons (no small red text).
2. Cert Lookup "photo of the label" fails silently ("Looking up..." then empty). Show the result or a clear error.
3. add_coins.html (after the brace fix): show a file list, progress and errors for 1-2 invoice PDFs. Fix the morgan_avatar.png 404. Match the light theme.
4. The first click on sidebar "Take a photo" reloads to Welcome. Find the cause and fix it.
5. Desktop camera error: replace raw NotFoundError text with "No camera found" + [Choose a photo instead].
6. Hide the Microscope "Hardware Server Offline" / "Download Desktop Agent" banner unless the microscope is set up. Stop localhost get-status console calls when not set up.
7. Text at 11-13px goes up to 16px or more. The back arrow and "More ways to add" become 48px or more touch targets.

## Ticket only (not V8.18)
Unify the two add menus into ~4 main ways, Morgan more visible on the hub, "Tap" wording on desktop, tab bar cut at 1025px, photo box ~390x275. File as P7.1 ticket.

Rules unchanged. DONE + baton back to GROKCOS. OVER
