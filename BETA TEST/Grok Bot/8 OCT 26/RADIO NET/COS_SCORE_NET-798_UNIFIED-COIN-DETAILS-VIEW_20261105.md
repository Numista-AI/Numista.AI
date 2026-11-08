# GB CoS SCORE — NET-798 / PLAN_UNIFIED-COIN-DETAILS-VIEW (+ EGM review)

- **Scorer:** Grok Bot Chief of Staff (GB CoS scorer executor)
- **Date / Time:** 2026-11-05 ~2:50 PM ET (America/New_York)
- **Targets:** `docs/PLAN_UNIFIED-COIN-DETAILS-VIEW.md`, `docs/EGM_REVIEW_PLAN_UNIFIED-COIN-DETAILS-VIEW.md` (EGM 98), `RADIO NET/ARGON_REVIEW_PLAN_UNIFIED-COIN-DETAILS-VIEW.md` (Argon 97)
- **Mode:** SCORE ONLY — read-only repo checks
- **CoS Score:** **86 / 100 (`FAIL`)**
- **SAG Score (grok-4.7 via xAI API, key never printed):** **61 / 100 (`FAIL`)**
- **Eric YES gate:** **BLOCKED.** Revise baton **NET-806** filed to AG CoS v4.

---

## 1. Eric's two requirements — both are in the plan

- **Values stay showing until Close while stepping Previous/Next:** L144–146 "Once `"Show values"` is tapped, values remain visible as the user steps through `Previous coin` / `Next coin`. Values revert to hidden immediately upon modal `Close`." Also L227. **MET.**
- **Unchecked Congress.gov laws shown, labeled:** L192 "query Congress.gov statutory index … Rendered with prominent disclaimer: `From Congress.gov, not yet checked by us`." Catalog legislation wins (L191). **MET.**
- Build window 10–16 Nov (L229). Contrast table recomputed by CoS: all 7 ratios correct (17.48, 18.88, 12.63, 8.14, 9.32, 12.08, 1.1).

## 2. Verified against the repo (p7-v8.9, read-only)

| Plan claim | Reality | Severity |
|---|---|---|
| L148 "requires PIN entry (`StorageLocationPinService`)" | **No such class** in `lib/` (no PIN service at all; only `PinBoxRow` UI in `login_screen.dart:1432`) | must-fix (invented dependency) |
| L243 Step 3 call sites 3042, 2736, 2758 | 2736 ✔; card tap inspector call is **3044** (3043 is `setState(() => _selectedCoinId = effectiveId);`); `CoinDetailScreen.show` is at **2761 and 2773** (2758 is `if (parentDoc == null) return;`); extra `_showCoinInspectorDialog(parentDoc.id, …)` at **3122** not listed | must-fix |
| L911–913 quote (white title) | 911 is `crossAxisAlignment`, 913 `SizedBox`; root cause itself is real: `_kDark` (line 59) = `0xFFF4F4F2` in light mode | fix quote |
| L23 "invoked … from … Public Catalog" | No signed-out/public mode defined — must hide purchase/cost/invoice/retailer/storage/PIN/Edit/Delete/Verify/Wishlist | must-fix |
| L142 "Estimated Market Value" | Value source not named; must be CDN CPG retail; no wholesale; AI value labeled, not preferred | must-fix |
| L193 "Read on Congress.gov" link; L157 Verify → PCGS/NGC lookup | Outbound links. Eric (4 Nov): "I don't like linking to other pages." Argon also flagged. Needs Eric's explicit call: plain-text citation in-app, or an approved Congress.gov exception | Eric decision |
| L247 Step 5 deletes legacy views same build | No feature flag, no preview channel, no rollback, ~10 days before 26 Nov ads | must-fix |
| Edit / Wishlist / Delete / research-request log | These are Firestore writes; need a separate YES (SAG) | must-fix (one line) |
| Tests | Step 4 widget tests planned (good); add guest hide-list, CPG-only, flag-off, all call sites | add |

**CoS breakdown:** Founder decisions & UX spec (25) = 25; accuracy/citations (20) = 13 (invented PIN service, wrong call-site lines, missed 3122); privacy/PII & public-surface safety (20) = 15; values/CPG/no-wholesale (10) = 7; rollback/tests/launch fit (15) = 9; locks & plan-only (10) = 10; outbound/US-only (−3) → **86 FAIL**.

## 3. Must-fixes for v1.1 (CoS + SAG merged)

1. Drop `StorageLocationPinService` as if real; keep storage hidden until a PIN design is specified (separate YES).
2. Correct Step 3: 2736, 3044, 2761, 2773, **3122**; re-quote verbatim.
3. Add a **public/guest mode** hide-list (no purchase, cost, invoice, retailer, storage, PIN, ownership actions) — or remove "Public Catalog" from the launcher list for now.
4. Name the value source: **CDN CPG retail** only; no wholesale; AI value labeled; Live eBay not a public price.
5. Feature flag + preview channel + rollback; do **not** delete legacy views in the same build; code-freeze date before 26 Nov.
6. Split Firestore-writing actions (Edit/Wishlist/Delete/research log) to a separate YES; state $0 / capped Congress.gov calls, fail-closed.
7. Ask Eric (via this score): Congress.gov and PCGS/NGC links — plain-text in-app, or approved exception?
8. One line: US-only scope for the Laws lookup.

## 4. SAG Result (independent; grok-4.7)

```
## SAG_SCORE: 61/100 FAIL
## MUST_FIX (ordered, blocking before Eric YES; or 'NONE blocking')
1. Public Catalog is named as a launcher (plan line 23; facts798 #6) with no signed-out mode. Before any YES, specify that guests never see purchase, cost, invoice #, retailer, storage, PIN, Edit, Delete, Verify, Wishlist, or ownership. Private Show-values must not ride onto numista.ai or the 26 Nov ad.
2. Name the only public/product value source: CDN CPG retail. No wholesale. Do not prefer AI Value. Legacy inspector still shows `data[_F.aiValue]` as Est. Value (Argon quote, my_collection_screen.dart:3850). Drop Live eBay as a value tile unless it is proven not to be a price source on any surface.
3. Remove outbound links and hotlinked images. Plan line 193 allows `https://www.congress.gov/bill/...`; line 157 allows PCGS/NGC external lookup. Standing rule forbids outbound links. Laws stay in-app: act name, year, summary, and the unchecked label. Photos must be first-party; AI images only inside labeled `ai_replica_images`, never primary, card, or index.
4. `StorageLocationPinService` does not exist in lib/ (facts798 #3). Stop treating it as real. Storage stays hidden until a real PIN design is specified and separately approved. Do not ship a reveal path that calls a class that is not in the repo.
5. Step 3 is incomplete and the quotes are wrong (facts798 #1–2). Redirect all of: table cell 2736; card tap 3044 (keep the real 3043 `setState` for `_selectedCoinId`); both `CoinDetailScreen.show` sites at 2761 and 2773 (2758 is `if (parentDoc == null) return;`, not the show call); and `_showCoinInspectorDialog` at 3122. Until 3122 moves, values and storage can still share one screen (Argon quotes 3850–3852 and 3990–3996).
6. Add rollback. No feature flag, no preview channel, no code-freeze before the 26 Nov 2026 Meta launch (facts798 #9). Do not delete `_showCoinInspectorDialog` or `CoinDetailScreen` in the same 10–16 Nov build. Flag-off must restore the old screens. Tests must cover every call site, guest hide-list, CDN-only value, and flag-off.
7. Edit, Wishlist, Delete, and the Ask Morgan “research request” log are Firestore writes. This YES cannot cover them or any rules change. Split those to a separate typed YES. This document stays plan-only: no deploy, no merge, `origin/main` stays `9f04550a`, Stripe stays OFF.
8. Put a hard dollar cap on any Congress.gov (or other) call, with fail-closed behavior, or state zero new paid calls. No cap is stated now.
9. Replace the false verbatim blocks before Eric reads them: plan 3043 is not the inspector call; 911/913 are not the white title (facts798 #1–2). Contrast math itself is fine (facts798 #4). EGM’s “exact match” claim is not ground truth.
10. State US-only scope on the launcher: coins, notes, and currency of current and former US states, territories, and possessions only. Congress.gov fallback must not run for anything outside that set.
## NON_BLOCKING
Founder Decision #2 and #3 are actually in the plan: values stay up across Previous/Next until Close; unchecked Congress.gov text is labeled “From Congress.gov, not yet checked by us”; catalog legislation wins (facts798 #5). Contrast ratios match the CoS recompute. Tab wrap, ≥52px targets, and “Morgan must not invent laws” are specified. Wishlist failure handling can wait until the separate write YES. Do not treat EGM 98 or Argon 97 as clearance; both missed the missing PIN class and scored a public-surface gap as non-blocking.
## PII_FINDINGS
No AJ name, street address, or real person’s collection record appears in the plan, EGM review, Argon review, or facts798. The breach is structural. Public Catalog launch with no guest hide-list can show purchase price, retailer, invoice, storage (address-like), and ownership actions. Storage reveal depends on a PIN service that is not in the repo, so the gate is not real yet. Call site 3122 still opens the inspector that co-displays cost, Est. Value, and storage. In-session Show-values until Close is what Eric locked for the owner’s own collection; it is not allowed on a public or ad surface.
## 3_SENTENCE_PLAIN_ENGLISH (for founder Eric, plain words)
Do not type YES yet. The plan does keep values on screen while you step Previous and Next until Close, and it does show unchecked Congress.gov laws with the “not yet checked by us” label, but it also invents a PIN service, leaves an old screen that still shows value and storage together, and would open this same view on the public catalog without saying what strangers must not see. It also allows links off-site, never names CDN retail as the only public price, and deletes the old screens in the same sprint with no rollback before the Thanksgiving ad.
## RATIONALE
CoS facts override EGM and Argon. The two founder locks are present and the contrast numbers check out, which is why this is not a low score, but standing rules fail in the plan text: invented class, bad citations, missing call site 3122, no guest hide-list, no CDN-only value rule, outbound Congress.gov and cert links, no rollback before 26 Nov, Firestore writes bundled into one YES, and no hard dollar cap. That is not a 95 gate.
```

## 5. Three-Sentence Plain English (CoS, for Eric)

Your two asks are in the plan: values stay up as you step Previous/Next until you press Close, and Congress.gov laws we haven't checked are shown with a "not yet checked by us" label. But it relies on a PIN service that doesn't exist yet, misses one place in the code that still shows value and storage together, and would open this same screen on the public catalog without saying what strangers must not see. It also deletes the old screens in the same sprint with no undo before Thanksgiving, so it goes back to AG for v1.1; one question for you later is whether the Laws tab may link out to Congress.gov or should show the citation as plain text.

## 6. Next Actions (no execute)

1. **AG CoS v4:** take **BATON_NET-806** → `PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.1.md` clearing §3 (EGM not re-run unless scope grows). Then Argon → GB CoS → SAG → Eric.
2. Priority after NET-804 and NET-805.
3. Locks unchanged.
