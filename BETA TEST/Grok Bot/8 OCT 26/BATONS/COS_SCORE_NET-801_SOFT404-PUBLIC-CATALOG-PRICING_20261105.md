# GB CoS SCORE — NET-801 / PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING

- **Scorer:** Grok Bot Chief of Staff (GB CoS scorer executor)
- **Date / Time:** 2026-11-05 ~2:55 PM ET (America/New_York)
- **Targets:** `docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING.md`, `RADIO NET/ARGON_REVIEW_PLAN_SOFT404-PUBLIC-CATALOG-PRICING.md` (Argon 96)
- **Mode:** SCORE ONLY — read-only repo checks + read-only live HTTP probes
- **CoS Score:** **78 / 100 (`FAIL`)**
- **SAG Score (grok-4.7 via xAI API, key never printed):** **52 / 100 (`FAIL`)**
- **Eric YES gate:** **BLOCKED** for execution. The public-catalog **Option A/B/C pick is still Eric's decision**, but it should be asked on a corrected v1.1, not this text. Revise baton **NET-807** filed to AG CoS v4.

---

## 1. Verified this turn

| Plan claim | Reality (5 Nov ~2:35 PM ET) | Severity |
|---|---|---|
| §2.1 "`/catalog` \| 404 Not Found \| 1,664 bytes" | Live `https://numista-vault.web.app/catalog` → **200** (12,261 B SPA); `/catalog/foo` → 200; `/nonexistent-probe-404` → 404 at **3,379 B** | must-fix (stale premise) |
| §2.2 Defect A "omits `/catalog`" | True on `p7-v8.9`, but **`dev` firebase.json already has `/catalog` and `/catalog/**`**, and `dev` has `lib/screens/catalog/catalog_browse_screen.dart` (NET-747/768) under NET-777/803. Option A would duplicate/conflict | must-fix |
| login_screen.dart 338/340/466/566/692 | Verified verbatim (`'5,142'`, `'AI+'`, `_footerLink('Pricing', …)`, `'Forgot your PIN?'`) | OK |
| §4.2 meta "Browse 5,142 verified US and World reference coins" | Catalog master = **3,202** (2,965 coins / 181 notes / 56 medals). "World" breaks US-only | must-fix |
| §5 "`99.4%` Attribution Accuracy"; /about "numismatic advisory board"; /features "Sheldon grading" | No source anywhere in repo — invented public claims | must-fix |
| §6.1 "Execute existing unit tests `test/route_test.dart test/auth_gate_test.dart`" | **Neither file exists** | must-fix |
| §4.4 footer fix | Still `InkWell`; no real anchor/`Link` widget → middle-click / new-tab still broken | must-fix |
| §4.3 AuthGate | Reads `FirebaseAuth.instance.currentUser` synchronously before web auth restore (first-frame null race) | must-fix |
| Option table "Option C … Standard plan cycle" | Any public-catalog option needs Eric's typed YES | fix |
| Public card fields | No statement of values shown: must be CDN CPG retail only, no wholesale (Eric 5 Nov option B ties X posts to the public catalog's CPG retail page) | must-fix |
| Rollback / preview gate / $ cap | None stated | must-fix |
| Locks | Plan-only, `origin/main` 9f04550a, Stripe OFF, zero Firestore writes, Eric YES gate on public catalog — all stated (L8, L321–323) | PASS |
| PII | None in plan | PASS |

**CoS breakdown:** locks & plan-only (15) = 15; accuracy/citations (25) = 14 (stale 404, missing tests, ignores dev); founder rules — US-only, nothing invented, CPG-only (25) = 15; Eric decision gate (15) = 13 (Option C mislabeled); rollback/tests/launch fit (20) = 11 (no rollback; JS-only titles don't help Meta's crawler on `numista.ai`; anchor not real). **Total 78 FAIL.**

## 2. Must-fixes for v1.1 (CoS + SAG merged)

1. Re-probe live and strike the `/catalog` 404 premise; rebase the plan on `dev`'s existing catalog screen + rewrites and coordinate with NET-777 v1.4 (no duplicate screen).
2. Replace `5,142` with the cited 3,202 (or a cited newer count) everywhere, and reconcile the front-door badge; remove "World".
3. Delete `99.4%`, "advisory board", "Sheldon grading", "100% Private & Secure", "Passport Protocol" unless each is cited.
4. State public card fields: CDN CPG retail only, no wholesale, no user value/ownership; AI images only in `ai_replica_images`; no hotlinks/outbound links.
5. Real link widget for footer/Pricing (anchor semantics); fix AuthGate to await auth restore.
6. Static per-route `<title>`/OG for non-JS crawlers on the actual ad landing (`numista.ai`).
7. Rollback + preview channel + $0 cap line; mark the two test files "to be created".
8. Re-present Options A/B/C with all three requiring Eric's typed YES.

## 3. SAG Result (independent; grok-4.7)

```
## SAG_SCORE: 52/100 FAIL
## MUST_FIX (ordered, blocking before Eric YES; or 'NONE blocking')
1. Strike the live `/catalog` 404 premise. CoS fact 1: `https://numista-vault.web.app/catalog` and `/catalog/foo` are HTTP 200 (12,261-byte SPA); `/nonexistent-probe-404` is 404 at 3,379 bytes, not 1,664. Plan §2.1 is stale. Do not sell a live 404 fix.
2. Do not duplicate `dev`. Fact 2: `dev` already rewrites `/catalog` and `/catalog/**` and has `catalog_browse_screen.dart` (NET-747/768), under separate failfix NET-777 v1.3 / NET-803. Option A and §4.1–4.2 ignore that and would conflict. Make the blueprint conditional on Eric’s choice and on that existing screen.
3. US-only and no overclaim. Fact 4: catalog master is 3,202 (2,965 coins, 181 notes, 56 medals). Delete baked `5,142`, “verified US and World”, and “5,000+ organic landing pages” from titles, meta, and Option A. Cite the 3,202 source. Reconcile the front-door `5,142` badge; do not spread it.
4. Delete unsourced public claims (fact 5): `99.4% Attribution Accuracy`, “numismatic advisory board”, and “Sheldon grading”. Nothing invented; every public string needs a cited source.
5. Every public-catalog option, including C, needs Eric’s explicit typed YES. Plan table wrongly calls C a “standard plan cycle”. State card fields: no wholesale on any public surface; CDN CPG retail only; no user collection value or ownership (fact 9).
6. Image rules before any catalog cards: catalog-first; AI images only in labeled `ai_replica_images`, never primary/card/index; no hotlinked or outbound images or links. Plan promises obverse/reverse and “high-resolution imagery” with no source or rule.
7. Pricing fix does not fix the defect it names. Fact 7: §4.4 still uses `InkWell`, not a real anchor, so middle-click / open-in-new-tab still fails. Require a real link widget.
8. AuthGate: fact 8 — do not read `FirebaseAuth.instance.currentUser` synchronously before web auth restore (first frame can be null). Public-route precedence must not depend on that race.
9. Launch fit: 26 Nov Meta ads land on `https://numista.ai/`, not only `numista-vault.web.app`. JS `document.title` / `pushState` does not set the static HTML Meta’s non-JS crawler reads. Plan must cover preview-channel static title/OG for that landing, or it does not fix soft-404s for the ad.
10. Add rollback, a preview-channel gate before live, a hard $ cap (state $0 if no new spend), and real tests. Fact 6: `test/route_test.dart` and `test/auth_gate_test.dart` do not exist; do not call them existing. Fact 10: no rollback section.
## NON_BLOCKING
- PIN/password label swap and “lateral transfer” jargon cites match fact 3; keep them out of the YES path. Do not ship “Passport Protocol” or “100% Private & Secure” without a source.
- Footer `Semantics` work can wait; do not invent legal disclaimer text.
- Argon’s 96/100 is not ground truth. S404-1..3 overlap these blocks; Argon audited `p7-v8.9` code, not the later live probe.
- `curl -I` cannot prove titles or soft-404 clearance; any later test must assert body title on the preview host.
- Locks in the plan text (plan-only, `origin/main` @ `9f04550a`, Stripe OFF, no Firestore writes) are stated and are not the failure.
## PII_FINDINGS
No AJ. No user name, address, ownership, or user collection value in the plan text. Auth use is a boolean `currentUser != null` only. Unspecified public card prices are a policy gap (MUST_FIX 5), not a shown PII leak.
## 3_SENTENCE_PLAIN_ENGLISH (for founder Eric, plain words)
Do not type YES on this plan. It chases a catalog error that is already gone on the live site, would rebuild a catalog that already exists on dev, and would put the wrong coin count, world coins, and made-up claims on pages your ads will send people to. It also never says what prices or pictures may show, the pricing-button fix still is not a real link, and there is no rollback or real test.
## RATIONALE (brief)
CoS facts override the plan and Argon’s pass. Branch-level AuthGate order and InkWell diagnosis match quoted code, and lock language is present, so this is not a zero. It still fails the gate: false live 404, conflict with `dev`/NET-777/803, US-only and 3,202 vs “US and World” / 5,142, unsourced marketing, no wholesale/CPG rule, anchor fix that does not add an anchor, auth first-frame race, JS-only titles against a `numista.ai` Meta launch, missing rollback, and tests named that do not exist. That is well under 95.
```

## 4. Three-Sentence Plain English (CoS, for Eric)

This plan was written against an older picture: the live /catalog page already loads today, and the dev branch already has a public catalog screen that this plan would build a second time. It would also put "5,142 US and World coins" and a made-up "99.4% accuracy" figure on pages your Thanksgiving ads will send people to, when our catalog has 3,202 US entries. I sent it back to AG for v1.1; you'll still get to choose Option A, B or C, but on a corrected version — please don't pick one from this draft.

## 5. Next Actions (no execute)

1. **AG CoS v4:** take **BATON_NET-807** → `PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING_v1.1.md`. Then Argon → GB CoS → SAG → Eric typed pick (A/B/C) + YES.
2. Priority after NET-804 (catalog v1.4); 801 v1.1 should land in the same review pass so Eric decides the public catalog once.
3. Locks unchanged.
