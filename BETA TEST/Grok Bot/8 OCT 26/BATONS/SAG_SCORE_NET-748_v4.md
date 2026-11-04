# SAG SCORE NET-748 CoS v4 (xAI API, grok-4.7, 2026-11-04 ET)

The plan is not executable as written. Live-rules separation is real, but two plan-text defects would make a literal execute fail its own tests or bind a project-wide rules deploy to implicit CLI state. Argon’s 98 is not usable evidence.

Reviewer credibility: Argon’s “verbatim” plan and source quotes do not match this plan (rules are `allow get` / `allow list, write: if false`, not `allow read` / `allow write`; test 20 is not the text Argon placed at “line 348”). GB CoS’s later read is the credible source check: rules file and the MF call-site lines match, and `inventory_gallery.dart` exists at `numista_mobile/lib/inventory_gallery.dart` with the cited image lines. Argon’s “skip it, file does not exist” instruction is false. CoS 95 is directionally right on gates and line numbers, and wrong to pass over the case-folding break below.

Safety gates: Plan-only header is clear. Preview is `firebase hosting:channel:deploy p7-gate` only. Step 1b is correctly marked REACHES LIVE and not covered by a p7-gate YES. Seeding the 11 docs is correctly out of scope and needs its own YES. Main lock and Stripe OFF are stated. That gate structure is acceptable only if the live command is pinned (Must-fix 2).

Scope: v4’s delta list is the three Argon MFs plus carried v3 body, which matches the quoted 4 Nov decision. No new feature scope in v4. I cannot re-diff v3; “nothing else changed” is an assertion, not something this packet proves.

Internal consistency: MF-v3-1 paths, `allow get` (not list), and the 10-line diff rule match the pre-check. MF-v3-2 wiring at the three call sites is specified, with a STOP if title-only `extractSku` cannot infer. MF-v3-3 join (not `??`) and dropping the proof token are specified. Section 5.2 still tells the implementer to edit `inventory_gallery.dart`; the header only flags Argon’s non-existence note and does not itself say to skip the file.

MUST-FIXES:
1. Case-fold every new matcher, or the plan’s own tests fail. Section 3.2 lowercases only `cond`, then runs case-sensitive `silver`/`american`/`gold` regexes on `'$prog $theme $title $cond'`. Section 3.4 uses case-sensitive `cleanTitle.contains('declaration of independence'|'polly cooper'|…)` and case-sensitive `RegExp`s. Tests 2, 3, 6, 10, and 13 pass title-case strings (“American Silver Eagle”, “Declaration of Independence Quarter”, “Polly Cooper”). Dart `RegExp` and `contains` are case-sensitive. Before execute, lowercase `prog`/`theme`/`title` (and `cleanTitle`/`cleanDenom`/`cleanMint`) before those checks, or set `caseSensitive: false`, and make mint checks (`'P'`/`'D'`) case-insensitive too.
2. Step 1b’s live command is not bound to the reviewed target. The bare `firebase deploy --only firestore:rules` does not set `--project studio-9101802118-8c9a8`, cwd, or “deploy the same `numista_mobile/firestore.rules` that was diffed.” A pre-diff YES does not stop the CLI from using another alias or `firebase.json`. Pin project, cwd, and rules path in the command that Eric’s LIVE YES authorizes. Add a local rules compile/emulator check before that YES. Rollback stays “redeploy the saved snapshot.”

ADVISORIES:
- Do not follow Argon’s skip of `inventory_gallery.dart`. CoS found the file; section 5.2 lines 131 and 347 still apply. Add one explicit sentence so the header flag cannot be read as “skip.”
- Test 20 can legally STOP the attempt and forbids new title rules. Before execute, cite existing `extractSku` branches that already return 26XE/26XL/26XH/26XF/26SQRP/set SKUs from title+year only. If none exist, narrow test 20 and rely on `resolveFromMap` at the three call sites. Do not invent title rules in this attempt.
- Test 3’s “`combined` contains reverse proof” is not observable if both Ungraded and Ungraded+Reverse Proof return 26EA. Assert a visible behavior, or drop that clause.
- Section 9 constructor checks (`CoinImageResult`, `CanonicalMintAssetPair`) stay mandatory. Argon’s `source`-only constructor quote is not evidence; analyze must be 0 errors before any preview deploy.
- Re-read half-block line 336 before editing. v4 says those MF line refs were Argon’s and were not re-read; Argon’s quotes are already shown to be reconstructed.
- `item_type: 'roll'` stays a placeholder until the existing `_addSkuToCollection` literal is grepped. Names for 26XH/26XF/26GC/26RG/26RH/23RG/23RH must be copied, not paraphrased. Curl-200 remains a preview gate; `gcloud ls` is not public-read proof.

SAG SCORE: 88/100 - REVISE