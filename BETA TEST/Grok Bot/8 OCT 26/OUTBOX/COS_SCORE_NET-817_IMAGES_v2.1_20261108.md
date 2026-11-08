# GB CoS score — NET-817 Images v2.1 (NET-780c)

**94/100 — FAIL. PASS requires 95+.**

Plan: `docs/FAILFIX_PLAN_NET-780c_IMAGES_v2.1.md`
Bytes: 67704; SHA-256: `f2a42702d0995f9b0e8571e8c201ad59012918a9cccd4cbad053700d7228cdb7`. Matches the reviewed EDS baton hash.

Prepared 2026-11-08 08:09 AM EST (America/New_York). Delta-focused static/document review against the preceding full-plan CoS reviews and, for NET-817, the complete independent SAG response at `/workspace/sag817/SAG_API_RESPONSE_20261108-072843.md`. Writer self-scores are not evidence. Proposed snippets are not shipped code. No application build, Dart/Flutter execution, deploy, Firestore/GCS access, push, or implementation edit was performed. Scratch `git apply --check` checks only patch applicability, not application correctness.

Source evidence retained from this round's `git show` citation audit and preceding full-plan reviews: pin `4d17ca5ef1f73c0e5f5c9dca3a96f00ab9a15235`; observed local `origin/dev` `bde8b402d34675a39f2b3b4e872cb46f71a5b32a`; locked main `9f04550a45fa4da082ba8948c2d89a521a90fa45`. Local remote-tracking refs are not a fresh network fetch. Plan line numbers below refer to the exact reviewed file.

## Closeout of SAG MF-SAG-I1..I7
- **I1 CLOSED as a design.** 679-701 uses one selection function: confirmed uploads choose the preferred side and fail closed only for that side; otherwise unowned fields are absent, then owned canonical/direct/reference. The proposed tests include canonical + unowned field and owned reverse + unowned obverse.
- **I2 CLOSED.** 325-330 now quotes the actual two-field read and _buildCoinImage, not invented shipped alias reads. Round evidence verified _F.imageObverse/imageReverse values at my_collection_screen.dart 76-77. Alias expansion is proposed new helper behavior.
- **I3 PARTIAL / STILL OPEN.** Encoded traversal/backslash, userinfo and path-segment checks improve the guard. Literal raw dot segments are not rejected before URI normalization (below).
- **I4 CLOSED.** 712-720 removes the invented shipped five-second timeout; reference call shape remains explicit.
- **I5 CLOSED as a lifecycle design.** 669-675 checks selection signature as well as semantic request key; photo clearing/changing can initialize reference fetching. No widget execution claimed.
- **I6 CLOSED as procedure.** Guarded non-main rollback and reverse Images-before-Cards order are specified.
- **I7 CLOSED as planned coverage.** The balabaskar reference prefix now has an actual guard assertion, not merely a comment.

## Remaining must-fix — MF-SAG-I3 raw-dot rejection
At 365-368, the absolute URL prechecks reject backslash and encoded dot/backslash patterns but do not check literal `.`/`..` segments. `Uri.tryParse` runs at 381; only then do 386-387 inspect decoded pathSegments. Dart's default Uri implementation normalizes paths first. Thus `https://storage.googleapis.com/us_mint_coin_images/a/../x.jpg` is normalized to an allowed bucket path and accepted rather than rejected as required. A traversal from one allowed bucket to another can similarly normalize to another allowed root.

Reject raw path dot segments **before** parsing/normalization, retain decoded/normalized checks, and add in-allowlist normalization cases. Existing tests that traverse to an unapproved root can pass merely because the resulting root is unapproved; they do not prove raw rejection. This finding does not claim the example escapes the final bucket allowlist or proves a private-image disclosure. Official Dart reference: https://api.dart.dev/dart-core/Uri/normalizePath.html (default implementation always normalizes). No Dart/Flutter execution performed.

## Source grounding / no invented shipped behavior
Round `git show` evidence retained: my_collection_screen.dart 6360-6365,6369-6383,6399-6406,6409-6417; firebase.json CSP 276; build_image_index.py 44-46,53-103,301-303; currency emitter 38-42,267; promoted-photo emitter 35-37,130 and destination 196. The new selection/guard/lifecycle code is a proposal, not claimed shipped behavior.

## Score
**94/100:** six points withheld for incomplete closure of SAG's explicit raw-dot rejection requirement and the corresponding false broad security closeout. I1/I2/I4/I5/I6/I7 are substantively closed as plan changes. No fresh SAG advancement while I3 remains open.

## Privacy, gates, and filing
- Count-only exact private-promotion scan: **six current plans: 0; handoff tree: 0**. Handoff scope: 2,852 text files recursively under `BETA TEST/Grok Bot/8 OCT 26`, including RADIO NET, For SAG, BATONS, INBOX and OUTBOX. The historical literal was derived internally from the previously cited historical document and never printed. No claim that repository history was erased.
- PLAN ONLY. Main locked, US-only, Stripe sandbox/OFF, alerts only and never caps. No AJ/private collector values or promotion token reproduced.
- PASS is plan readiness only: CoS >=95 -> independent SAG reading the complete current plan >=95 -> Eric's explicit typed YES. Firestore writes and deployments each retain separate YES gates. No beta retest before Field Tester evidence closes every open item.
- DONE on a review baton means review completed, not approval. This executor prepared score files on the box only: repository filing and baton renames require a sanctioned repository-editing executor; CloudAgent was absent from this executor's available tool catalog. No repository write, commit, or rename is claimed here.
