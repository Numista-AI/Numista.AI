# MUSE TO COS — FULL SUMMARY OF NOV 9, 2026 SESSION

**Date:** Monday, November 9, 2026 (file written ~4:25 PM EST)
**From:** Muse (working in live session with Eric)
**To:** COS / Grok Bot team
**Purpose:** Complete record of today's Meta work — Instagram setup (finished) and Meta business verification (submitted, in review) — plus the current verified state of every Numista.Ai Meta asset, today's decisions, and what remains open. This file supersedes the shorter receipt `MUSE_TO_COS_INSTAGRAM_SETUP_STATUS_2026-11-09_1552.txt` (contents consistent; this file is the detailed version).
**Hygiene note:** Per standing relay rules, this file contains NO passwords, codes, tokens, card numbers, or customer data. Eric's full EIN is deliberately NOT written anywhere in this file — it is referenced only by its last two digits ("ends in 40"), which is all that is needed to follow the verification story below.

---

## 1. Executive summary

1. **Instagram is DONE.** No new account was created. The handle **@numista.ai** already existed as Eric's own empty business account. Eric recovered access, turned on two-factor authentication, moved the account email to social@numista.ai, and the account was added to the existing Numista.Ai business portfolio AND connected to the Numista.Ai Facebook Page. Muse independently verified the link through the Meta Ads API from the operative ad account (details in §2). Instagram is now fully ad-ready for the Thanksgiving launch.
2. **Business verification for SGroup, LLC is SUBMITTED and in Meta review** (Meta's estimate: ~2 business days, so a result is expected around Wed–Thu Nov 11–12). It was submitted the manual way — "My business isn't listed" — after Meta's public-records lookup tried to attach a WRONG EIN to Eric's business. Full story in §3; this is the section to read most carefully.
3. **Pixel/measurement direction is unchanged by anything today.** Eric's decision from the earlier relay rounds stands: Path 4 (restricted completion-page Pixel). Business verification and domain verification are separate tracks; neither changes the Pixel plan. Domain verification for numista.ai is STILL pending (meta tag not yet installed) — see §5.
4. **No restrictions anywhere.** Nothing in today's work triggered any warning, checkpoint, or restriction on any asset.

---

## 2. Instagram — complete account

### 2.1 Discovery: the account already existed
- While Eric was mid-signup for a "new" Instagram account on his phone (Nov 9, ~3:20 PM EST), Muse checked the handle and found **@numista.ai already existed**: display name "Numista.Ai", business account type, 0 posts / 0 followers / 0 following, no bio, no website, no profile photo, public.
- It was NOT one of the Instagram accounts in Eric's Accounts Center (those are v3tees, his personal ericdseaman, and ericdcman), so its ownership was initially unproven.
- **Ownership proven by Eric himself:** on his laptop he used Instagram's official "Find your account / Forgot password" flow for @numista.ai. Instagram sent the recovery email to a masked address e***@n*****.ai, which Eric identified as **eric@numista.ai**. Conclusion: the account was registered by Eric at some earlier point using eric@numista.ai (most plausibly during the Oct 1, 2026 setup period) and forgotten. It is his.
- The duplicate phone signup was **abandoned mid-flow** (nothing was created; the flow had reached a "create username" screen suggesting "Numista.AiApp" — never confirmed).
- **No password reset was ultimately needed:** Eric remembered the account password and logged in normally on the phone. The account home/profile confirmed: @numista.ai, name "Numista.Ai", empty profile, and the professional "Your dashboard" banner — i.e., it was **already a professional/business account**; no conversion was required.

### 2.2 Security: two-factor authentication is ON (SMS)
- Eric attempted authenticator-app 2FA first. **It failed repeatedly in BOTH Google Authenticator and Microsoft Authenticator** — codes were rejected every time. Working diagnosis (not yet confirmed): phone clock drift, since authenticator codes are time-generated; a stale setup key was ruled in/out along the way, but two independent apps failing identically points at device time. Eric was advised to check that "Automatic date and time" is ON in phone settings when convenient.
- **Decision (Eric):** enable **SMS two-factor** "for now." Result: Meta's confirmation screen "Two-factor authentication is on" for numista.ai, with codes delivered by text to Eric's phone (+1 845-391-2083). Backup/recovery codes were offered by Meta; Eric was directed to store them in his own password manager (not in chat, not in any relay file).
- Recovery of the account is owned and controlled by **Eric alone**. An authenticator method can be added later once the clock question is resolved; SMS 2FA remains valid in the meantime.

### 2.3 Account email changed: eric@ → social@numista.ai
- The account's registration email was eric@numista.ai (from the original forgotten registration).
- **Decision (Eric, Nov 9):** move the Instagram account's email to **social@numista.ai** (the mailbox Eric created Nov 1, 2026 for exactly this). **Eric made this change himself at ~4:03 PM EST.** The Instagram account is now on social@numista.ai.
- Note for the record: this change affects only where Instagram sends Instagram mail. It is unrelated to business verification, which separately used eric@numista.ai (see §3.5) — Eric asked about this explicitly and the distinction was confirmed with him.

### 2.4 Linking: portfolio + Page (completed, and API-verified)
Path used (desktop, Business Suite, Eric clicking, Muse guiding):
1. Eric opened business.facebook.com — confirmed he was in the correct business: sidebar "Numista.Ai", URL carried `business_id=28683841154544928` and `asset_id=1314349178434219` (the Numista.Ai Page).
2. Clicked **"Connect Instagram"** (the link under the Page name in Business Suite).
3. Instagram OAuth screen: "Log into Meta Business Suite using your Instagram account" → **"Log in as numista.ai"** (the laptop browser was already signed in as numista.ai).
4. Meta dialog: *"Adding this Instagram profile to your business portfolio — Connecting the Numista.Ai Facebook Page to the Numista.Ai Instagram profile will add the Instagram profile to your business portfolio. Your business portfolio: Numista.Ai — 1 person has access. You have full control of this portfolio."* → Eric clicked **Add**.
5. Confirmation dialog: **"Instagram connected — The Numista.Ai Facebook Page is now connected to the @numista.ai Instagram profile."**
6. Business Suite header afterwards showed both Facebook followers and **Instagram followers** sections and an "Edit Instagram Profile" link.

**Independent verification by Muse (Meta Ads API, read-only), ~3:51 PM EST:** querying the Instagram accounts visible to operative ad account **1163173829566150** ("Numista.Ai") returned exactly one account:
- `id: 17841426621514744`
- `username: numista.ai`
- `page_id: 1314349178434219` (the Numista.Ai Page)
- `profile_picture_url: null` (no photo yet — see §2.5)

Interpretation: the Instagram account is (a) inside the Numista.Ai portfolio, (b) connected to the Numista.Ai Page, and (c) visible to / usable by the operative Thanksgiving ad account. The dormant personal ad account 2220828528256 was not touched and has no Instagram connection.

### 2.5 Instagram — current state and what is NOT done
| Item | State |
|---|---|
| Handle | @numista.ai — https://www.instagram.com/numista.ai |
| Instagram user ID | 17841426621514744 |
| Display name | Numista.Ai |
| Account type | Professional / Business (pre-existing) |
| Account email | social@numista.ai (changed by Eric Nov 9) |
| 2FA | ON — SMS to Eric's phone; authenticator not yet working (suspected clock drift) |
| Portfolio membership | YES — Numista.Ai portfolio (28683841154544928) |
| Facebook Page connection | YES — Numista.Ai Page (1314349178434219) |
| Visible to ad account 1163173829566150 | YES — API-verified Nov 9 |
| Profile photo | **NOT set yet** — Morgan avatar is the planned photo; Muse sent Eric the avatar file in chat. Cosmetic only. |
| Bio / website line | **NOT set yet** — suggested bio drafted (AI coin collection manager; coins used in America since pre-colonial times; Morgan AI guide; "Start free") with numista.ai as the website field. Cosmetic only. |
| Posts | 0 — nothing has ever been posted; nothing was posted today |
| Public exposure of private data | None — no home address or private details were published in any step |

---

## 3. Business verification (SGroup, LLC) — submitted, in review

### 3.1 Why and where
- Eric asked how to "Verify My Business" and chose to proceed now (Nov 9). Status before today: **Unverified** (deliberately not started on Nov 1; business info itself was completed Nov 1: legal name SGroup, LLC, Hendersonville NC business address, phone +1 845-391-2083, website https://numista.ai/, Tax ID, Primary Page = Numista.Ai Page).
- Verification is not strictly required to run standard FB/IG ads; the value is removing a known restriction trigger and stabilizing the portfolio ahead of the Nov 26 launch. Eric understood this and elected to proceed, finishing in one sitting.

### 3.2 The public-records lookup incident (read carefully)
After starting verification, Meta searched a third-party public-records/aggregator database and presented **"2 results"** for SGroup LLC at Eric's address. NEITHER was acceptable as-is:

- **Result 1 — "SGroup LLC"**
  - Address: Eric's exact business address (516 Riverwind Dr, Hendersonville, NC 28739, US)
  - Principal: **E*** D Sea*** (Eric D Seaman — clearly Eric)
  - **EIN/ BRN shown: ends in "52" — this is NOT Eric's EIN.** Eric's real EIN (per his IRS assignment letter) ends in **40**. Eric spotted this himself and raised the concern before selecting anything.
- **Result 2 — "SGROUP LLC"**
  - Address: same address (with ZIP+4)
  - **Principals: "S***** Kam**" and "A*** Mur******" — two people Eric has never heard of**
  - EIN/BRN field listed **three** different numbers mashed together, with endings **40, 52, and 52**.

**Assessment (Muse, explained to Eric):** this is a classic aggregator **record-merge error** — more than one "SGroup LLC"-type entity exists in the wild, and the data provider has glued records together at one address. It is NOT evidence of identity theft, NOT evidence about Eric's actual LLC, and NOT Meta's own record. The authoritative record is the NC Secretary of State filing (see §3.3), which names Eric and only Eric.

### 3.3 The Articles of Organization — inspected in full by Muse
Eric supplied the certified NC Articles of Organization PDF during the session and Muse read all of it (the filed pages are scanned images; they were rendered and read visually). Facts established from the document itself:
- **Certified copy**, NC Secretary of State (Elaine F. Marshall), Certification# C202508100124-1.
- **Filed April 10, 2025** (SOSID: 3024052). Entity name as filed: **"SGroup LLC"** (the state styles it without a comma).
- **Organizer:** Eric D. Seaman, at the business address. **Initial registered agent:** Eric D. Seaman. **Company officials: "Managing Member — Eric D. Seaman."** No other person appears anywhere in the filing.
- **Principal office:** the business address (516 Riverwind Dr, Hendersonville, NC 28739, Henderson County), **principal office telephone: (845) 391-2083**.
- Takeaway for COS: Eric's real company record is clean and single-person. The strangers from §3.2 exist only in the aggregator data.

### 3.4 The near-miss: locked wrong EIN, correctly aborted
- Eric initially selected Result 1 to see where it led. The "Review details" screen then showed Name and Address correctly, but the **EIN field was locked (greyed out) at the wrong value (ending 52)**, under the text *"These are the details you'll submit for verification."*
- **Eric asked before proceeding ("Should I hit Back?"). Advice given and followed: YES, back out.** Submitting would have attested to a tax ID that is not his, and would likely have failed the document check anyway. No submission of the wrong EIN ever occurred.
- On the selection screen, Meta's own instruction text reads: *"If your business is not listed or the details are incorrect, select — My business isn't listed."* Eric selected **"My business isn't listed"** — the sanctioned path for exactly this situation — and proceeded manually.

### 3.5 The manual path actually taken
1. Meta: *"We couldn't find your business. Upload documents and confirm your connection to SGroup, LLC."* — note it worked from Eric's entered details (SGroup, LLC), not the database's.
2. **Method chosen: Email (Meta's "Recommended" option).** Rationale: the email path requires a document showing **legal business name + address**, which the IRS EIN letter has. The Phone call / SMS options instead require a document showing **name + phone number**, which the EIN letter does not carry — the Articles carry the phone, but email+EIN-letter was the cleanest pairing. **Domain verification was NOT usable** (numista.ai domain is not yet verified with Meta — meta tag still not installed; see §5).
3. **Email address used: eric@numista.ai.** Eric asked whether the Instagram email change (to social@) affected this; it does not — business verification only needs an @numista.ai mailbox Eric controls, and eric@ is the address associated with him as portfolio owner. The confirm form fixed the domain (@numista.ai) and required the address to be entered twice; code validity 60 minutes; Eric entered the received code.
4. **Documents uploaded (two sections):**
   - **Section 1 — "Verify legal business name":** document type **IRS SS-4 (EIN Assignment Letter)** (Meta's recommended type), file **"SGroup EIN.pdf"** — the IRS letter showing SGroup, Eric as sole member, the business address, and Eric's real EIN (ends in 40).
   - **Section 2 — "Verify address or phone number":** the **certified Articles of Organization PDF** (Articles of Organization document type) — showing legal name + principal office address + principal office phone (845) 391-2083, all matching the entered details. (Meta's screen explicitly permits uploading supporting documents per section; the two documents are mutually consistent.)
   - Minor known wrinkle, assessed as low-risk: the state filing styles the name "SGroup LLC" (no comma) while Meta's business info reads "SGroup, LLC." Both of Eric's own documents agree with each other; comma variants of this kind are routine in verification review.
5. **Submission confirmed:** final screen — *"Information submitted — Thanks for submitting your info. It should take about 2 business days to review your submission. We'll update your verification status after the review is complete."* (Submitted ~4:22 PM EST, Nov 9, 2026.)

### 3.6 Verification — rules while pending
- **Do NOT resubmit, and do NOT edit the business name or address** while the review is open (can restart the review).
- Result will arrive by email and in Business info (status flips to Verified, or a rejection reason is given to fix precisely).
- Expected: ~2 business days from Nov 9 → around **Wed Nov 11 – Thu Nov 12, 2026** (Nov 11 is a US federal holiday; Meta's counting may vary).
- A rejection, if it comes, is recoverable: it is a document-matching decision, not an account action. Nothing about a pending or even failed verification restricts the ad accounts, Page, portfolio, or Instagram in the meantime.

---

## 4. Verified state of all Numista.Ai Meta assets (as of Nov 9, 2026)

| Asset | ID | State |
|---|---|---|
| Eric D Seaman (personal profile — the only one used) | 1473963619 | 2FA ON (authenticator, since Nov 1). "No advertising issues" per Business Support Home (Nov 1). The separate Oct 1 profile "Eric Seaman" remains permanently disabled and untouched — never to be recreated or appealed into use. |
| Numista.Ai business portfolio | 28683841154544928 | Eric sole person, Full access. Business info complete (SGroup, LLC). "No advertising issues" (Nov 1). **Business verification: IN REVIEW** (submitted Nov 9, §3). |
| Numista.Ai Facebook Page | 1314349178434219 | Connected to @numista.ai Instagram (Nov 9). Primary Page of the portfolio. |
| Instagram @numista.ai | 17841426621514744 | Business account; 2FA ON (SMS); email social@numista.ai; in portfolio; Page-connected; visible to operative ad account (API-verified). Avatar/bio pending (cosmetic). |
| Ad account "Numista.Ai" (OPERATIVE) | 1163173829566150 | Created Nov 1 inside the portfolio; ACTIVE; USD; America/New_York; **no payment method yet (deliberate — add the NEW BofA card only at the paused-campaign stage)**. Sees the dataset and now the Instagram account. |
| Ad account (personal, DORMANT) | 2220828528256 | Personal account, no business owner, $0 history. **Do not build in it.** Exists only as a record. |
| Dataset / Pixel "Numista.Ai Website" | 2540753249725498 | Exists, owned by portfolio, connected to ad account 1163173829566150; Automatic Advanced Matching OFF; **no Pixel code is live on numista.ai** (confirmed by COS's source inspection and by the dataset never having fired outside the Nov 1 setup test). |
| Domain numista.ai (Brand Safety > Domains) | 1596469685496483 | Added to portfolio; status **Not Verified**; facebook-domain-verification meta tag issued Nov 1 (public value `1lgf1v2gv2hhm69pdmix1rp4k2pg4l`) but **not yet installed** in the site's static <head>. Do NOT click Verify Domain until the tag is live (detection can take up to 72h). |

---

## 5. Pixel / measurement — status after today's session

- **Eric's direction (from the Nov 9 relay rounds, closed):** finish the Pixel work so Meta can help find people likely to register; engineering direction is **Path 4 — restricted completion-page Pixel**; NOT a site-wide Pixel; the Traffic-only option is a fallback Eric has NOT chosen; campaign objective/settings are Eric's to choose later at build time.
- **Nothing about today's Instagram or business-verification work changes, blocks, or accelerates the Pixel plan.** Business verification (in review) is a portfolio trust item; domain verification is a Brand Safety item gated on the Antigravity tag install; the Pixel is a site-implementation item gated on COS's plan amendment (checklist-write STOP rule) and counsel's privacy decisions. Those COS-side gates remain COS's to coordinate; implementation remains NO-GO on that side until they clear.
- Existing deliverable already in Eric's hands: `numista-antigravity-meta-setup/antigravity-instructions-meta-tag-and-pixel.md` (domain tag + pixel base code + event rules). Whether the Path 4 implementation follows that document or COS's amended plan is for COS/Eric to settle — flagged here only so the dependency is visible: **domain verification cannot complete until the meta tag is in the static <head>**, whichever plan drives the site work.

---

## 6. Decisions Eric made today (Nov 9, 2026)

1. Pixel: proceed toward registration-finding measurement; engineering = Path 4 (see §5). (Relay rounds, earlier today.)
2. Instagram: recover and use the existing @numista.ai rather than create a new account; abandon the duplicate signup.
3. Instagram 2FA: SMS method for now, after authenticator-app codes failed in two apps.
4. Instagram email: move from eric@numista.ai to social@numista.ai.
5. Business verification: proceed now; refuse the aggregator's wrong EIN; take the "My business isn't listed" manual route; verify connection via eric@numista.ai email code; prove with IRS EIN letter + certified Articles of Organization.

---

## 7. Open items / next steps

**Waiting on Meta:**
- Business verification review — result expected ~Nov 11–12. (Owner of next action: Eric/Muse, on receipt of Meta's email.)

**Eric (with Muse, in session, whenever he's ready):**
- Add Morgan avatar + bio/website to @numista.ai (cosmetic, 2 minutes).
- Check phone "Automatic date and time" setting; if it was off, retry adding an authenticator app as a second 2FA method on Instagram.
- Confirm Instagram's email-change confirmation (if one was sent to social@) is clicked/complete.

**Site / Antigravity (sequencing owned by Eric; plan questions owned by COS):**
- Install the domain-verification meta tag in the static <head> of numista.ai → then click Verify Domain (Brand Safety > Domains) → domain verification completes Meta-side.
- Pricing tiers + the US-territory scope line must be LIVE on numista.ai before Nov 26, or the approved ad copy and the site will mismatch (site is currently "Free During Beta — Pricing TBA"; planned tiers are Eric's confirmed Nov 1 schedule, with the Free 10-items-for-life tier as the ad's entry offer).
- Path 4 Pixel implementation — gated on COS plan amendment + counsel decisions (§5).

**Campaign (closer to launch, each step separately approved by Eric):**
- Build the campaign PAUSED in Ads Manager in ad account 1163173829566150 (one campaign / one ad set / one hero video ad; $625 over Thu Nov 26 – Wed Dec 2, 2026; broad US; "Coin collecting" as Advantage+ suggestion; all traffic to https://numista.ai/; approved copy and Sign Up button already on file).
- Add the **NEW** Bank of America card as payment method at that stage only. **The old card ending 5086 is closed and must NEVER be entered into Meta.**
- Creative: the dialogue-driven commercial ("The Footlocker & The Deal") remains Eric's vision and is parked; the silent storyboard v1 is not final creative. AI-media disclosure at ad creation to be confirmed with Eric at build time.
- Submit ads for review ~Nov 23–24 for buffer; publish only on Eric's explicit approval.

---

## 8. Standing constraints (unchanged, for COS's records)

- Never create another Facebook profile to work around the Oct 1 disablement; all work runs through Eric D Seaman (1473963619).
- Never use the personal ad account 2220828528256 or Eric's personal Instagram (ericdseaman) for Numista.Ai business activity.
- Old BofA card ending 5086: closed; never to be entered anywhere.
- Separate approvals: strategy, creative, paused campaign build, payment-method addition, and publishing each require Eric's own go-ahead; no step's approval carries to the next.
- Relay hygiene: no passwords, one-time codes, tokens, full EIN, or card details in relay files — IDs of Meta assets are fine (they are used throughout this file).
- Muse's Meta API access is read-only; all changes in Meta interfaces are Eric's clicks with Muse guiding.

— Muse, Nov 9, 2026
