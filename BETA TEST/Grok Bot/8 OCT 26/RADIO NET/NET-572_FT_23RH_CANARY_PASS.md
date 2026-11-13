# NET-572 FT — 23RH canary OVERALL PASS
**Filed:** 2026-10-26 ~7:27 PM ET by Field Tester  
**Preview:** https://numista-vault--p7-gate-8avtpz22.web.app  
**Revs:** Hosting a628e317ea5b632a · Run 00494-rew (p7gate) · commit 4eb93476  
**Account:** grokbot@numista.ai only · Live/main OFF

## BLUF
**OVERALL PASS.** All 3 locked acceptance items passed on p7gate.

| Item | Result | Notes |
|---|---|---|
| 1 Save / Save & Commit — no error toast | PASS | Edit→Save: "Changes saved to Review Queue." Edit→Save & Commit: "Added 1 coin." No error toast. Hub 4→3 pending. |
| 2 Fee 9.95 on Hub + reopened Edit | PASS | Set Fee 9.95 in Edit→Save. Hub Fee $9.95. Reopened Edit Fee 9.95 / header "Fee: $9.95". |
| 3 Hub Date = Edit purchase date | PASS | Edit Purchase Date 2026-10-21 = Hub Date 2026-10-21. |

## Notes
- Upload API host: `p7gate---numista-backend-qntvrqvxma-uc.a.run.app` (PASS). Bare-backend GET `/api/user/ui_variant` seen on Hub load only — not upload.
- Re-uploaded Silver_Proof_Set_2023_23RH.pdf once (no prior pending 23RH). Import: USM25343756 / 23RH / $254.95 / date 2026-10-21. Import auto Fee $9.95 this time; still set 9.95 manually in Edit.
- Collection dashboard still showed 351 after commit (toast "Added 1 coin") — count may be stale or merged into existing 23RH; not a FAIL under locked items.
- Leftover dup.csv / dup_v81815f.csv Hub rows untouched.
- One accidental Delete Item? dialog opened then cancelled; nothing deleted.

## Shots (`shots_mint_all/`)
- `80_net572_hub_before_edit.png`
- `80_net572_save_hub_fee_date.png`
- `80_net572_save_and_commit.png`
- `81_82_net572_edit_fee_date.png`

OVER.
