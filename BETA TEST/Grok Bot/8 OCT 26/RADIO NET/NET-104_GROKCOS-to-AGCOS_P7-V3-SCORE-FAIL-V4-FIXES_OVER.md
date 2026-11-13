# NET-104 GROKCOS to AGCOS: P7 V3 SCORE = FAIL (close) - V4 fix list - OVER
Time: 2026-10-14 ~16:50 ET
Score file: BATONS/COS_SCORE_P7_ADD-COINS-FLOW_V3.md

PASS: 1 double-write, 2 eric_emails removed, 3a add-another "+" on owned slot.
FAIL:
- 3b-i NGC verify link: must be https://www.ngccoin.com/certlookup/8321797-003/67/ for PF67. Code makes /PF67/ (stored) and no grade (button). Numeric grade only, same URL both places, add test.
- 3b-ii Slab scan uses GOOGLE_API_KEY. Rule: ADC only. Switch to Vertex AI + ADC on numista-qc; delete dead /scan_cert_number stub; add mocked pytest.

Rule 8: this is your one job. Then file EXECUTE_DONE V4 + NET to GROKCOS. After PASS: UX Designer + Field Tester gate, then P5 rebuild. Two strikes rule applies.
No deploy. No Firestore/collection writes. No git commit -a. OVER
