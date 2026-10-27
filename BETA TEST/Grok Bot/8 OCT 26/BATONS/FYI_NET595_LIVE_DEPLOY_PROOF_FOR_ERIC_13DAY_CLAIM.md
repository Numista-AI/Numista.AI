# FYI | NET-595 live deploy proof for Eric ("13 days" claim)

- **DTG:** 2026-10-27 ~11:22 AM ET
- **For:** CoS → Eric
- **Point:** Live landed **today** ~10:52 AM ET (not 13 days ago).

## Proof
| Item | Value |
|------|-------|
| Hosting site | `numista-vault` (project `studio-9101802118-8c9a8`) |
| Custom domain | https://numista.ai |
| Release time | **Tue, 27 Oct 2026 14:52:14 GMT** (= **10:52 AM ET**) |
| ETag | `c815127b48fa94c8c927b378317af9d30d50bb210555c70e9c4d6cf5e18a9c01` |
| Cloud Run | `numista-backend-00494-rew` @ 100% (us-central1) |
| main | `449a9dcf` (PR #268); cherry-pick `dfdbae38` from tip `2234f7e4` |
| Smoke | https://numista.ai → **200** |

## Console links
- Firebase Hosting: https://console.firebase.google.com/project/studio-9101802118-8c9a8/hosting/sites/numista-vault
- Cloud Run revisions: https://console.cloud.google.com/run/detail/us-central1/numista-backend/revisions?project=studio-9101802118-8c9a8
- PR: https://github.com/Numista-AI/Numista.AI/pull/268

Source baton: `BATONS\EXECUTE_DONE_LIVE_CHERRY_PICK_NET595.md` + RADIO NET-597.
