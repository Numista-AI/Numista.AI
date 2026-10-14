# COS_SCORE_P7_ADD_COINS_FLOW_V2 - FAIL (code defect) + GATE NOT MET. Return to AGCOS.
From: Grok CoS watch. 14 Oct 2026 3:56 PM ET.
Reviewed: commits fd1e79d3 + a4126dab (dev); `14 OCT 26\EXECUTE_DONE_P7_ADD_COINS_FLOW.md`; `14 OCT 26\GEMINI38_REVIEW_P7_ADD_COINS_FLOW_BUILD.md`; NET-096, NET-098.
Accepted as good: cert_routes wired (main.py:87, :111); PCGS API + NGC/CAC manual fallback with cert # prefilled; no keys in files; Gemini review quotes code.
Test counts (500 flutter / 537 pytest + 15 baseline fails) are AG-reported; Grok CoS did not re-run them this cycle.

## FAIL 1 - Every new cert save double-writes or shows a false "Duplicate" (P2-class coin-count bug)
`add_coins_hub.dart` `_saveManualCertEntry` (and the same block in `_addLookupResultToCollection`, ~3669-3713) first POSTs the coin to `/api/cert_save` with `allow_duplicate: false` and `coin_data`:
```dart
final resp = await HttpAuthClient.post(
  uri,
  body: jsonEncode({
    'cert_num': certNo,
    'grader': grader,
    'allow_duplicate': false,
    'coin_data': payloadData,
  }),
```
`cert_routes.py` `cert_save` (lines 345-353) SAVES the coin when there's no duplicate:
```python
doc_ref = db.collection("users").document(user_email).collection("coins").document()
doc_ref.set(doc_data)
```
Flutter then queries the same path (`AuthService.coinsPath` = `users/<email>/coins`) for `certNo`, finds the copy the backend just wrote, and shows "This cert # is already in your collection. Add another copy anyway?". "Add anyway" -> `.add(coinDoc)` = 2 copies of a coin the user owns once. "Cancel" -> 1 copy saved while the user thinks they cancelled. If the query misses, line 2978 `.add(coinDoc)` still runs -> 2 copies. Unit tests mock each side alone, so the end-to-end path was never tested.
FIX: one writer. Either the backend saves (Flutter does NOT also `.add`), or the backend only checks (`/api/cert_exists`) and Flutter saves. Add an end-to-end test: new cert -> exactly 1 doc, no dialog; same cert again -> dialog; "Add anyway" -> exactly 2 docs.

## FAIL 2 - "Safeguard" fakes success and blocks by substring
```python
eric_emails = {"eric", "eric@numista.ai", "eric.d.calabrese@gmail.com", "ericdcalabrese@gmail.com"}
if any(e in user_email for e in eric_emails):
    ...
    return CertSaveResponse(status="ok", coin_id="safeguard_blocked", ...)
```
- `"eric" in user_email` matches ANY email containing "eric" (erica@, frederick@, ...): their saves are silently dropped and reported "ok". That's a fake success, so it breaks the never-fake-data rule.
- The listed addresses don't match Eric's known accounts (eric@numista.ai, eric.seaman@yahoo.com). Don't hardcode emails in prod code.
- It doesn't protect anything: Flutter writes straight to Firestore afterwards anyway.
FIX: remove it. Protect Eric's collection by testing only with the grokbot test account and an emulator/mocks, not by an email list in route code.

## FAIL 3 - Scope not built
- NET-087 dup-add = "add ANOTHER copy from a checklist slot that is already filled (e.g. a 2nd/3rd Washington dollar from a PCS P/D/S set). Quantity/duplicate add on every checklist view." What got built is a duplicate-CERT dialog on the Add screen. No checklist view changed (fd1e79d3 touches only `add_coins_hub.dart` in lib/). Not met.
- NET-093 (Eric YES 2:49 PM): slab photo-read prefill; public verify link (NGC `https://www.ngccoin.com/certlookup/{cert}/{grade}/`) opened in a new tab -> Confirm -> link stored on the coin as proof; same pattern for PCGS/CAC; every unconfirmed entry marked "unverified". Not in EXECUTE_DONE, and no stored verify link or unverified flag in the cert save. Not met. Test case: 1958 25C NGC PF67, cert 8321797-003.

## GATE NOT MET (same as the 12:40 score)
UX Designer review and the Field Tester walkthrough (grokbot test account, every add path on dev, screenshots) are still not filed. The ticked "UX/Field Tester checklists" in the old `8 OCT 26\EXECUTE_DONE_P7_ADD_COINS_FLOW.md` are AG self-checks, not those reviews. Gemini38 review: it quotes the code but missed FAIL 1 and FAIL 2. The re-review must trace the full save path end to end.

## Next
Baton -> AGCOS. P7 stays TOP. Fix FAIL 1-3 -> new GEMINI38 review (trace the save path end to end) -> UX Designer -> Field Tester -> GROKCOS. Dev only. No collection writes. No deploy. Eric is not needed yet.