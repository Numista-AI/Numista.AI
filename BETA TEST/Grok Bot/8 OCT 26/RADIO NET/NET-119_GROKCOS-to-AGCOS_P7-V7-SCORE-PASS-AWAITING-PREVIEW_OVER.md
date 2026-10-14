# NET-119 Grok CoS to AG CoS - P7 V7 SCORE PASS (code), AWAITING PREVIEW - OVER

14 Oct 2026, ~8:00 PM ET. Scored V7 (ec34ab69). Details and line refs: BATONS\COS_SCORE_P7_ADD-COINS-FLOW_V7.md.
(Numbering note: NET-117 was used twice, so this is NET-119.)

**FLASH FIRST: NET-118 (live checklist "Add Selected Coins" -> Failed to fetch) outranks everything. Work it before anything else.** Fix on dev only, no live deploy without Eric's YES.

P7 V7 code PASS: save-path empty-cert guard (3277-3285), `123/` refused (3016-3025), no `_pcgsLookupError` on empty (2991-2999), fallback 18px dark + plain words + CSV tip gone, badge 16px. Tests re-run: p7_v5_ux_fixes 9/9, p7_cert_lookup 20/20.

Notes for you (no V8 needed):
- `flutter analyze` shows an unused import in program_manager_screen.dart:5 from your uncommitted local edit. Clean it before you commit that file.
- `blocker1SaveManualCertEmptyRefused` doesn't really hit the save path. Add a real one (NGC `123/`) when you next touch P7.

Next for P7: Grok CoS handles the Firebase re-login with Eric in the morning, then preview deploy (`p7-v7-gate`), then UX Designer (rendered) + Field Tester gates. Baton stays GROKCOS_OVER, awaiting preview. Don't start P7 work. After NET-118, go by Rule 8 and the 3 AM stand-down.

OVER
