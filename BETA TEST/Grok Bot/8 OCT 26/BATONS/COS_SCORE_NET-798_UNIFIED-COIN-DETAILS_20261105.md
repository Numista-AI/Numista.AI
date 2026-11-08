# GB CoS SCORE — NET-798 / Unified Coin Details View (+ EGM)

- **Scorer:** Grok Bot Chief of Staff (GB CoS scorer executor)
- **Date / Time:** 2026-11-05 ~2:20 PM ET (America/New_York)
- **Targets:** `PLAN_UNIFIED-COIN-DETAILS-VIEW.md`, `EGM_REVIEW_PLAN_UNIFIED-COIN-DETAILS-VIEW.md` (EGM 98), `ARGON_REVIEW_PLAN_UNIFIED-COIN-DETAILS-VIEW.md` (Argon 97)
- **Mode:** SCORE ONLY
- **CoS Score:** **97 / 100 (`PASS`)**
- **EGM:** 98 APPROVED FOR BUILD | **Argon:** 97
- **SAG Score (this turn, grok-4.7 via xAI API):** **74 / 100 (`FAIL`)**
- **Eric YES gate:** **BLOCKED** by SAG FAIL (74). CoS PASS alone does not authorize YES.

---

## 1. CoS Checklist

| Check | Result | Notes |
| :--- | :---: | :--- |
| Plan-only; main `@ 9f04550a`; Stripe OFF | PASS | Explicit |
| Firestore separate YES | PASS | Zero Firestore writes |
| No AJ / user PII | PASS | None in plan |
| No hotlinked images | PASS | Photos from collection/catalog assets; Congress.gov is text/link question (UCD-3) |
| AI replicas not primary | PASS | Empty state = silhouette + “Add a photo”, not AI primary |
| Eric Locked #2 Show values persist Prev/Next until Close | PASS | §3.4 / §7 |
| Eric Locked #3 Congress.gov labeled “not yet checked by us”; catalog wins | PASS | §5 / §7 |
| Mutual privacy: values XOR storage (PIN) | PASS | §3.4 |
| Tests | PASS | Widget tests for privacy gate + persistence + tab wrap |
| Rollback / preview / $cap | PARTIAL | UI-only; low $; should still name p7-gate / preview before live and deprecation rollback of dual views |
| Thanksgiving Meta ad #1 fit | PASS | Sprint 10–16 Nov UX polish supports conversion; not blocking soft-404/catalog public work |

**Breakdown:** Spec/Eric locked decisions (30)=30; Unification + citations (20)=19 (−1 UCD-1 both virtual-child branches); Privacy gate + a11y AAA (25)=25; EGM gate done (15)=14; Preview/$cap explicitness (10)=9. **Total 97.**

### Carry-forward (non-blocking)

1. **UCD-1:** Redirect both `isVirtualChild` and `else` `CoinDetailScreen.show` branches.
2. **UCD-2:** Keep `_selectedCoinId` sync when replacing inspector.
3. **UCD-3 (needs Eric at YES):** Confirm whether Laws tab `"Read on Congress.gov"` is an approved statutory exception to the site-wide no-outbound-links rule, or plain-text Act/PL only.

---

## 2. Two-Sentence Plain English (for Eric)

This plan replaces the two different coin detail screens (Cards vs Table) with one shared view: big readable titles, Front/Back photos, Ask Morgan, and six simpler tabs. Your rules are built in — once you tap “Show values,” they stay on while you step Previous/Next until Close; storage stays PIN-gated and never shares the screen with dollar amounts; and any Congress.gov law we have not checked is labeled “not yet checked by us.”

---

## 3. SAG Result (independent; grok-4.7; key never printed)

```
# SAG SCORE NET-798 (xAI API, grok-4.7, 2026-11-05 ET)

## SAG_SCORE: 74/100 FAIL
## MUST_FIX (blocking before Eric YES; or NONE blocking)
1. UCD-3 is blocking. Delete every Congress.gov hotlink, including both “Read on Congress.gov” buttons in the diagram and §5.3. Laws stay in-app text only: act name, year, public-law number, plain-English summary. Catalog wins. If catalog law is empty, unchecked Congress.gov text may show only with the exact footer “From Congress.gov, not yet checked by us”. No URL, no external browser. Lock #3 does not allow leaving the app.
2. Public values: CDN CPG retail only. Never wholesale. Never AI-primary. Do not carry `aiValue` forward as Est. Value or Estimated Market Value. Live eBay is not the primary value. No invented prices. User purchase price stays behind Show values.
3. Hard $cap, fail closed, on any Congress.gov query, Morgan research request, and eBay live check. No uncapped calls.
4. Rollback before cutover. Do not delete `_showCoinInspectorDialog` or `CoinDetailScreen` in the same step as first ship. Keep the old path callable until preview passes.
5. Preview-before-live on a non-prod build before any live deploy. `origin/main` stays `9f04550a`. Stripe stays OFF. This plan authorizes zero Firestore writes. A research-request log is a separate Firestore change and is not approved here.
6. Nothing invented. Strike or cite real Global Search and Public Catalog launch sites; §8 only wires collection. Do not treat “View Parent Set” (`isVirtualChild`) as coin details. Fix the card-tap citation: the live call sets `_selectedCoinId` before the inspector. Account for both `CoinDetailScreen.show` branches, not one line.
7. Images: user or catalog photos only. `ai_replica_images` never primary. No photo means coin outline plus “Add a photo”, not a replica.
8. Tests must cover the privacy gate, Show values across Previous/Next until Close, catalog-wins, the exact Congress label, zero outbound links, retail-only non-AI value, and the virtual-child path.
## NON_BLOCKING
- Thanksgiving Meta ads stay priority #1. The 10–16 Nov details work must not displace that track.
- Re-measure contrast on a real device in preview. The ratio table is a design target, not a lab cert.
- Public Law 116-330 is an example only. Do not hardcode it for every 2026 coin.
- Morgan preload stays limited to year, mint, denomination, variety, and grade. Never send purchase price, storage, invoice, or user identity.
- EGM 98 and Argon 97 are not clearance. They treated the outbound link as a nit.
## PII_FINDINGS
No customer PII and no AJ in the plan. No emails, phones, or real storage addresses. Argon’s review embeds local `c:/Users/ericd/...` paths; do not copy those into shared or public docs. Storage stays PIN-gated and off-screen while values are showing.
## 2_SENTENCE_PLAIN_ENGLISH (for Eric)
The plan does follow your three locks: build 10–16 Nov, keep values showing while you step Previous/Next until Close, and let catalog law beat unchecked Congress.gov text. I am not ready for a YES until the Congress.gov web link is removed, prices are locked to retail guide data instead of AI or wholesale, and a dollar cap, rollback, and preview-before-live are written in.
## RATIONALE (brief)
Privacy split, tab cut, and the three locked decisions are actually in the plan, and the doc stays plan-only with main and Stripe locked. It still fails because it authorizes an outbound Congress.gov hotlink, inherits AI estimated value, and omits the dollar cap, rollback, preview-before-live, image rule, and accurate entry-point citations. Those are blocking plan edits, not build permission.
```


## 4. Next Actions

SAG → Eric typed YES after SAG ≥95. No deploy. Locks unchanged.
