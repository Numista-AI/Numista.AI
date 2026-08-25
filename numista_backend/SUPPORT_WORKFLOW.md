# Support Workflow — Scoped Consent Support Access

**Numista.AI** · Updated Aug 2026

---

## Overview

This document describes how to use the support ticket and scoped access system.
The privacy boundary is enforced server-side — you never see financial data,
personal notes, or storage locations, regardless of what the user chooses to share.

---

## 1. User Raises a Ticket

The user fills out the "Submit a Help Ticket" form on the Customer Service screen.
A ticket document is created in Firestore at `tickets/{ticket_id}`.

**Fields you can read from the base document (admin-readable):**
- `ticket_id`, `user_id`, `status`, `subject`, `description`, `category`
- `platform`, `app_version`, `created_at`, `updated_at`, `grant_active`

**Fields you CANNOT see:**
- `resolution_notes` (admin-write only, never returned to the user)
- Anything in `tickets/{id}/private/grant_and_diag` — this is backend Admin SDK only

---

## 2. Viewing the Support Queue

**Endpoint:** `GET /support/tickets`  
**Auth:** Firebase ID token with `admin == true` custom claim

Returns tickets with status `open`, `in_progress`, or `waiting_on_user`.
No grant token required for the queue list.

---

## 3. User Issues a Support Grant

The user navigates to **My Tickets**, finds their open ticket, and taps
**"Grant Temporary Support Access"**. They choose a duration (up to 48 hours)
and optionally select specific coins.

The backend generates a random 64-character token and shows it to the user **once**.
Only the SHA-256 hash is stored in Firestore — the raw token is never persisted.

The user then pastes the token into a message to you (or directly into the
Support Portal token field).

---

## 4. Viewing a Ticket with Grant Access

**Endpoint:** `GET /support/tickets/{ticket_id}`  
**Auth:** Firebase ID token (`admin == true`) + `X-Grant-Token: <token>` header  

The backend:
1. Verifies the ID token is valid and has `admin == true`
2. Verifies the grant token hash matches what is stored
3. Checks the grant has not expired (`expires_at > now`) and is not revoked
4. Re-fetches live coin data from `users/{email}/coins/{coin_id}` (server-side)
5. Strips ALWAYS_REDACTED fields AND any user-elected redactions
6. Returns snake_case coin fields + `redacted_fields_applied` list

**In the Support Portal UI:**
1. Paste the token into the token field at the top of the queue panel
2. Click the ticket to load the redacted view
3. The yellow banner lists any fields the user chose to hide beyond the default set

---

## 5. ALWAYS_REDACTED Fields (never visible to support)

```
purchase_cost     personal_notes    storage_location
ai_estimated_value  greysheet_value   melt_value
purchase_price    insurance_value   cost  notes
```

These are hardcoded server-side. The user cannot un-redact them.

---

## 6. Responding to a Ticket

**Endpoint:** `POST /support/tickets/{ticket_id}/messages`  
**Auth:** Admin token + `X-Grant-Token` header  

Type a reply in the Support Portal message box and click "Send Reply".
The user sees replies in their My Tickets view.

---

## 7. Updating Ticket Status

**Endpoint:** `PATCH /support/tickets/{ticket_id}/status`  
**Auth:** Admin token only (no grant token needed for status changes)

Use the dropdown in the ticket detail view. When status is set to `closed`,
the backend automatically revokes the active grant (if any) and sets
`grant_active = false` on the base document.

Valid statuses: `open`, `in_progress`, `waiting_on_user`, `resolved`, `closed`

---

## 8. Grant Expiry

Cloud Scheduler hits `GET /support/expire-grants` every 30 minutes.
Any ticket with `grant_active = true` whose `expires_at` has passed is
automatically revoked and `grant_active` is set to `false`.

---

## 9. Audit Log

Every support action is written to `support_access_logs/{log_id}` by the
backend Admin SDK. Admin can read this collection. Clients cannot write to it.

Actions logged: `grant_created`, `grant_used`, `document_read`,
`grant_revoked`, `grant_expired`, `message_sent`, `portal_opened`

---

## 10. Privacy Boundary Summary

| Who | Can See |
|-----|---------|
| User | Their own ticket base document and messages |
| Admin (Firestore) | Base ticket document only — no private sub-doc |
| Support Portal (HTTP + grant token) | Server-redacted coin fields only |
| Anyone | `private/grant_and_diag` — NEVER (Admin SDK only) |
