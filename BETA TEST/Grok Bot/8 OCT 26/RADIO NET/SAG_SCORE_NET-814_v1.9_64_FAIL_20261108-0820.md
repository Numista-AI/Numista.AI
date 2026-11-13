# Independent SAG review net814

Full plan submitted; packet chars 198899
Usage: {"prompt_tokens": 54922, "completion_tokens": 2411, "total_tokens": 86406, "prompt_tokens_details": {"text_tokens": 54922, "audio_tokens": 0, "image_tokens": 0, "cached_tokens": 1152}, "completion_tokens_details": {"reasoning_tokens": 29073, "audio_tokens": 0, "accepted_prediction_tokens": 0, "rejected_prediction_tokens": 0}, "num_sources_used": 0, "cost_in_usd_ticks": 2970200000}

## Score / verdict

| Item | Result |
|---|---|
| Score | **64 / 100** |
| Verdict | **FAIL** |
| Pass bar | ≥ 95 |
| Review stance | Plan readiness only. No tools or tests were run. Historical CoS scores were not used as a target. |
| Next gate | Revise the plan to close the must-fixes below. No code edits, builds, Firestore writes, Hosting deploys, or `main` pushes until a later Founder typed YES. |

Verified against the packet, not against the plan’s self-closeout: pin `4d17ca5e` facts that were supplied match for `firebase.json` rewrite/header **content**, `web/index.html:23` canonical and no robots meta, `pubspec.yaml:1` `name: numista_ai`, `public_info_screens.dart` 362/396/407/412, and `auth_gate.dart` 101–103 / 106–148 / 157–159. Pin `main.dart` has **no** catalog route (unknown-path guard at 119–149). Catalog screen line cites match **`b0b05808`**, which the packet labels prerequisite source, not the pin. v1.9 `_hasRawDotSegment` matches the negative cases written in §9.3a; that item is not a must-fix. Stripe OFF, alert-only $20, `main` lock `9f04550a`, promo literal absent, and CPG “does not exist / fail closed” are stated correctly.

## Must-fixes (evidence-backed)

**MF-1 — High — Firebase diff contradicts the stated integration target (−6).**  
§3.2’s only concrete diff **appends** `/catalog` and `/catalog/**` → `/catalog_unknown.html` after `/claim/**`. The same section says origin/dev **already** has `/catalog/**` → `/index.html` and “do not append duplicates.” Pin evidence ends rewrites at `/claim/**` (lines 129–133); the hunk `@@ -115,6` is also the wrong pin location (`/wishlist` destination is line 115). On a first-match rewrite list, an appended rule never runs, so unknown `/catalog/**` still serves root `index.html`, which has **no** robots meta (`web/index.html` head, canonical only at line 23). Replace the diff with two explicit edits: pin = insert both rules once; origin/dev = change only the existing `/catalog/**` destination. Do not leave both instructions in force.

**MF-2 — High — Acceptance tests do not match grounded UI and are not runnable as specified (−6).**  
§9.2 expects `find.text('Reference Catalog')`. Supplied `b0b05808` `catalog_browse_screen.dart` has `Public Catalog` at line 270 and `U.S. Numismatics Catalog` at line 335. No plan edit renames either string. The same tests `pumpAndSettle` the real screen, which loads the full asset and calls `Image.network` (lines 918 and 1106) with no fixture, asset override, or image mock. §9.1 hardcodes `https://numista-vault--pre-thanksgiving-net814-xyz.web.app` instead of the channel URL printed by `hosting:channel:deploy`. §7.2 deploys before any of those checks. Lock assertions to the evidenced strings, add a small fixture harness, and capture the real preview host before curl.

**MF-3 — High — Proposed prices are not fail-closed (−5).**  
Established copy at pin `public_info_screens.dart` is free beta: line 362 `Free During Beta — Pricing TBA`, line 396 `$0 / month`, lines 407 and 412 free / grandfathered with no pay. §8.2 still specifies `$30 / 6 months`, a 10-coin trial, and world coverage in 2027, while §3.4 never defines `pricing/index.html` body copy. §9.1 Test 4 and §9.4 only check HTTP 200 and canonical. Require generator and in-app pricing to emit **only** the four established strings until a separate Founder YES, and add a negative assertion that proposed price and world-coverage sentences are absent. US-only stays operative.

**MF-4 — High — Image control does not match evidenced URL shape or call sites (−5).**  
`b0b05808` treats `primary_image` / `type_image` as maps and loads `imgMap['url']` at lines 904–918 and 1105–1108. §6.4 and E1 talk about `primary_image` as if the guard/OG step receives that value, and never name `['url']`. Nothing inserts `isApprovedCatalogImageUrl` before `Image.network`. §7.5 does not list a production file for the guard (closeout mentions only the test). Specify: read `primary_image['url']` and `type_image['url']`; fail closed to the existing placeholder; put the function in a manifested production file; assert the call sites, not only bare `expect`s.

**MF-5 — Medium — Mintage neutralization invents a field and a source name (−3).**  
§6.4 replacement reads `mintage?['source_name']` and defaults to `US Mint Records`. Supplied `_buildMintageRow` (lines 987–1026) only uses `value`, `label`, and `source_url`. Drop `source_name` and the Mint default. Neutralize by rendering `value`/`label` as plain text and not calling `launchUrl` on `source_url`.

**MF-6 — Medium — Per-coin HTML sample is not a build-output patch (−3).**  
§3.6 says `catalog_unknown.html` is a copy of `index.html` with noindex and canonical `https://numista.ai/catalog` baked in. §3.4’s per-coin sample is a new minimal document (`<base href="/">`, one bootstrap script). Pin `web/index.html:8` is `<base href="$FLUTTER_BASE_HREF">`, and lines 134–206 add scripts the sample drops. State one rule: after `flutter build web`, clone `build/web/index.html`, preserve the built bootstrap payload, and only replace title, description, canonical, and OG/Twitter tags. Do not treat the stripped sample as the template. Emit `og:image` / `twitter:image` only from a non-null `primary_image['url']` that passed the guard.

**MF-7 — Medium — §7.5 manifest does not list files this plan requires (−2).**  
Missing from the table: `numista_mobile/lib/routing/public_catalog_route.dart` (required by §9.2 and §11), the image-guard production file, and `test/services/catalog_image_guard_test.dart` (named in the v1.8 closeout only). The checklist an implementer would follow is stale.

**MF-8 — Medium — Ungrounded marketing string (−2).**  
§5.1 orders an update of public copy claiming `5,142 Reference Coins`. That string is not in the supplied pin files or in `b0b05808` catalog screen, and no path:line is cited. Cite the occurrence or delete the instruction. Do not invent a landing-page edit.

**MF-9 — Low — Known E1 regression is not in the acceptance tests (−2).**  
§3.4 omits image tags for the null-image sample, but §9.1 and §9.4 never assert that the served 1921 Morgan page lacks `og:image` and `twitter:image`. Add that negative check so a later generator cannot reintroduce a substitute image URL.

**Deduction sum: 36. Score: 64.**

## Polish (no further deduction)

- Title/path/signature drift: header says v1.9, path and §10 signature still say v1.8 / Antigravity v5.
- Header line label “135–234” is wrong (pin headers run 135–280). The quoted header **text** matches the pin, including CSP.
- Rollback: second `main` check is dead after the `dev` assertion; `tac` is not portable macOS bash; script was not executed. Branch push is `origin dev` only, which matches the lock.
- `extractInitialNac` can throw on a second `Uri.decodeComponent` of an already-decoded path. Same pattern as the quoted dispatch. Specify try/catch if this helper becomes the production parser.
- Test 2b is a comment, not a harness. Banner text in the widget class does match the unknown-NAC widget expect.
- Direct GET of `/catalog_unknown.html` is not whitelisted in pin `isKnownPath`.

## Uncertainties (not scored as inventions)

- origin/dev `bde8b402` `main.dart` and full `firebase.json` are **not** in this packet. Catalog UI evidence is `b0b05808`, not the pin and not `bde8b402`. Line numbers match `b0b05808`; SHA identity with origin/dev is unproven.
- Sample NAC `NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3` (Philadelphia, `90% Silver`, era string, null images) is not in the supplied catalog excerpt. Packet column-checks are `1921-D` `...1921.D.BASE.2` and `2024-W` American Silver Eagle. Do not treat those 1921-P field values as confirmed here.
- `promote_user_photos.py` lines 35–37, 130, 196 and the two image-index emitters are cited but not in the packet.
- Census 2,965 / 181 / 56 matches the hardcoded tab labels at `b0b05808` lines 585–596 and sums to 3,202. Badge counts 1,724 / 950 / 9 / 519 are arithmetic-only here. Packet also says 2,251 `is_placeholder` false; the plan never says whether placeholder rows get indexable HTML.
- `releases[0]` as the live Hosting version is asserted, not shown. Prefer the live channel, then the console check already in §7.4.
- Flutter service worker (`flutter_service_worker.js` in pin headers) may intercept browser navigations that curl will not. Curl can still prove Hosting bytes; it does not prove browser HTML.

## Next gate

1. Patch the plan only (still PLAN ONLY).  
2. Re-review against pin `4d17ca5e` vs `b0b05808` vs origin/dev, with one firebase edit per branch and tests that match evidenced strings and `['url']`.  
3. Do not start implementation, preview deploy, Firestore writes, or pricing-copy changes on this score. Those still need a separate Founder typed YES after a ≥ 95 review.