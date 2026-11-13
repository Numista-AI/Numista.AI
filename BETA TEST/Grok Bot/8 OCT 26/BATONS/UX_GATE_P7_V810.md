# UX Gate: P7 V8.10 (commit 747f7051)
Preview: https://numista-vault--p7-v810-gate-1w44jzb8.web.app
Gated 16 Oct 2026 by UX Designer, using the signed-out demo only. There was no sign-in and nothing was saved.
Main gate: 1025px and 1280px.

## VERDICT: FAIL

The build is closer: 3 of the 7 V8.9 blockers are fixed.

## Fixed (PASS)
- **Checklist buttons:** Print is 48px, Download PDF is 48px, and Add Selected is 52px.
- **Mint column:** long text wraps onto 3 lines and nothing is cut off.
- **Pound sign:** "£2 Silver" shows correctly on the Britannia detail screen, the dashboard and the table. I found no collection CSV or PDF export in the demo, so the exports are still unverified. The only PDF I could download, the checklist, has no £ in it.
- **Table view:** the demo session is kept at 1025 and 1280.
- **Network:** no /api/news/feed calls and no CORS errors.

## Still failing (blockers)
1. **Number keypad.** Year, Cost and Qty are `type="text"` with NO `inputmode` attribute, on Type it in and on Manual Entry, at both widths. This is unchanged from V8.9. Fix: set `inputmode` on each field directly: numeric for Year and Qty, decimal for Cost.
2. **The My Collection "All" tab still crashes** ("Something went wrong loading this screen") at both widths. The console shows: `Bad state: Stream has already been listened to.` Likely fix: a single-subscription stream is being listened to twice, so use a broadcast stream or build a fresh stream for each listener.
3. **Snackbar covers the caption at 1025.** It covers the end of "Sign in to save selected coins…". At 1280 it covers the right end of the button. Fix: anchor it above the action bar, or show it at the top.

## Other console errors to check
- `[cloud_firestore/permission-denied]` from the Normalizer in the demo.
- "No signed-in Firebase user" from HttpAuthClient.
- Repeated "Another exception was thrown: Instance of 'minified:mc<void>'".

## Nice-to-have (open since V8.9)
- The Coins filter still includes paper notes (Federal Reserve Notes, a Silver Certificate, a Confederate note).
- The donut chart's "Premium" label is still clipped and reads "remium".

## Evidence
17 PNGs are in /workspace/numista-ux/p7v810/ on my computer. The key ones are copied alongside this file.
