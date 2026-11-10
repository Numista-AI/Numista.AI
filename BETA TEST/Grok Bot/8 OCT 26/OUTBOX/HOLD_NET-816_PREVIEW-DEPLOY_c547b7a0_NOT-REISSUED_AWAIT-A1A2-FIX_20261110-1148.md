# HOLD — NET-816 p7-gate preview-deploy at c547b7a0 is not re-issued (AG CoS v5)
From: GB CoS via Desk. Decision time: **10 Nov 2026 ~11:47 AM ET** (America/New_York).
Filed: 2026-11-10 11:48:17 EST by Grok Bot Desk. **Decision record only. No WAKE. No code, git, Firebase, or gcloud.**
To: AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
This record grants **no new authority**.

## Decision
The NET-816 preview-deploy baton `BATON_NET-816_AGCOS-V5_PREVIEW-DEPLOY_CATALOG-CHUNK1_v2.2_p7-gate_20261110-1007.md` (SHA-256 `c65658e0e2783477e0d07b271dcf6cee1e5d939764ccd5ae4f257539e7fcdf0c`) is **HELD**.

It was **BLOCKED** at **11:40 AM ET** with Firebase/gcloud credentials expired, per AG file:
- `BLOCKED_BATON_NET-816_PREVIEW-DEPLOY_CATALOG-CHUNK1_v2.2_p7-gate_20261110-1140.md`
- SHA-256 `67c5a39002c7cbee71c3c986fbd9b47a8df4fcc9b05f639bc472cb44464c47fe` (2245 B; found on day RADIO NET / BATONS / INBOX / OUTBOX; not seen in mailbox on this check)

**Do NOT re-issue or retry that preview deploy at `c547b7a0`.** That commit lacks the `/catalog` rewrite in `firebase.json` (**A1**), so /catalog would 404.

Re-issue the p7-gate preview deploy **only** at the **A1/A2-fixed commit**, after that fail-fix plan passes **CoS 95 + SAG 95 + Eric's typed YES**.
Eric's **10:06 AM ET YES** (card `t2455s9467`) covered **`c547b7a0` only**. The fixed commit needs his own **new scoped YES**.

## Credentials
Eric has been asked to run `firebase login --reauth` and `gcloud auth application-default login` on EDS_Laptop. This is **CoS-stated and not yet confirmed**. No agent handles his passwords.

## Free tier
Free tier is **10 coins lifetime** per `DECISION_NET-827_FREE-TIER-10-COINS-LIFETIME_RELEASES-HOLD_20261110-1139.md` (SHA-256 `2bf48ebcf9590f119987cc994b38256a7a147f015a8932352e863b35729942a9`).
That decision postdates and **supersedes** AG's contemporaneous ACK §4 wording (see findings below).

## Unchanged
- Go-live addendum `c2b6ac93b844a51d22be23ba428b3d098ad3f2e087e004b3aa6d63919755b4c2` stays **NOT ACTIVE** under HOLD `41b8bd5fd437eb626b823ccabe7c8f111b4d24322335b5ea1ef3bcf6e778943d`.
- The A1/A2 and B1–B5 fail-fix plans remain **plan-only**.
- NET-827 stays **queued**.

## AG BLOCKED / ACK findings (Desk read-only)
- **BLOCKED** as named above: named blocker is expired Firebase CLI session credentials; also records failed `gcloud auth application-default` refresh; live / main / Firestore / Stripe untouched; secondary note confirms A1 missing `/catalog` rewrite at `c547b7a0`.
- No separate ACK of that BLOCKED file, or of the preview-deploy baton, was found on this check.
- Contemporaneous AG ACK at ~11:40: `ACK_HOLD_NET-816_NET-827_AGCOS-V5_20261110-1140.md` SHA-256 `e358a92d6ed82b9d63b3f5985f342ecbb01eb05b6da1a4b74bbfe803694eee3a` (1436 B) — this ACKs the earlier HOLD / fail-fix plan-order notice, not the BLOCKED file.
- That ACK **§4** (“Free-Tier Coin Limit Hold”) says the free-tier limit is “Retained untouched at current codebase state pending CoS written confirmation of Eric's final decision.” That wording is **superseded** by the 10-coin lifetime decision above.

Filing this record ≠ a new preview-deploy baton and ≠ credential confirmation.
