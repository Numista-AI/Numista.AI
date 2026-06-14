# Numista.AI — Project State & Handoff
*Last updated: June 14, 2026 — Desktop Agent architecture finalized. Ready to hand off to new conversation.*

---

## 📌 Vision & Core Purpose (The North Star)

> *"Numista.AI becoming the 'System of Record' for Numismatics — so thorough that Numismatists, collectors, associations, societies and even the US Mint recognize its value — not only for its property accountability and estate planning features, but for its scholarly approach."*

**Origin story:** Aunt AJ, ~$500K collection, needed estate planning help. That's Customer #1.  
**Everything else was building to estate planning** — per the 13 JUN 2026 daily doc.

---

## ✅ Completed — June 14, 2026 Sessions

| Task | What Was Done |
|---|---|
| **PDF Scan fix deployed** | `main.py` `/api/process_invoice` now uses Gemini 2.5 Pro multimodal (DocumentAI fully removed). Deployed to `numista-backend` revision `00061-lbh` on Cloud Run (`studio-9101802118-8c9a8 / us-central1`). Endpoint confirmed live: returns `405 Method Not Allowed` on GET (correct — expects POST with file). |
| **Correct Cloud Run project identified** | Project: `studio-9101802118-8c9a8`. Service: `numista-backend`. URL: `https://numista-backend-568985927038.us-central1.run.app`. The `qntvrqvxma` URL is a separate orphan service on a different project. |
| **Flutter web rebuilt & redeployed** | Firebase Hosting (`numista-vault`) updated with: (1) `hardware_service.dart` URLs changed from `http://` → `https://localhost:5000`, (2) CSP `connect-src` updated to include `https://localhost:5000`. |
| **Microscope hardware server upgraded to HTTPS** | `auto_capture.py` now loads `localhost.crt` / `localhost.key` and serves `https://localhost:5000`. `gen_cert.py` added to `numista_hardware/` to regenerate the cert. Server confirmed running on `https://192.168.1.135:5000`. |
| **Live site fully toured (authenticated)** | Logged in as `eric.seaman@yahoo.com`. All sidebar screens photographed and status confirmed. |

### Live Site Screen Status (Authenticated, Jun 14)

| Screen | Status | Notes |
|---|---|---|
| Morgan Greeter | ✅ Working | Owl avatar, 4 tiles, "browse on my own" link |
| Home Dashboard | ⚠️ Error (guest) | "Dashboard unavailable" in guest mode; fine when logged in |
| My Collection | ✅ Working (logged in) | 628 badge on Review Hub |
| Add New Coins | ✅ Working | 7 tabs: Single Invoice Scan, Bulk Upload, Manual Entry, CSV, Checklist, PCGS, Roll/Batch |
| Microscope Scanner | ⚠️ Needs Desktop Agent | "Hardware Server Offline" — see Desktop Agent plan below |
| Coin Reference Search | ✅ Working | Vertex AI, 1,913+ entries, suggested chip searches |
| AI Deepdive (Ask Morgan) | ✅ Working | Chat loads, Morgan greeting shown |
| Review Hub | ✅ Working | 628 coins pending review |

---

## 🖥️ NEXT CONVERSATION: Microscope Desktop Agent

> [!IMPORTANT]
> Start a **new focused conversation** for this. It's a full feature sprint. Use `/goal` to run it overnight end-to-end.

### Why this exists — Two User Groups

There are two distinct user paths for adding coins, and they need different solutions:

| User Type | Their Path | Status |
|---|---|---|
| **Casual Users** (most people) | "Take a photo" button in app — phone/webcam + Gemini Vision | ✅ Already solved |
| **Power Users** (serious collectors with USB microscopes) | Microscope Scanner screen — requires a local hardware bridge | ⏳ This sprint |

The power-user friction today: `auto_capture.py` is a raw Python script. Users must open a terminal. **That is not a product.**

### The Design Model — Plex / Lightroom / Sonos

Those apps ship a **local background service** that bridges local hardware to a cloud UI. The packaging transforms the user experience:

| Piece | Before (today) | After (Desktop Agent) |
|---|---|---|
| `auto_capture.py` | Run manually in terminal | Packaged into a `.exe` / `.dmg` installer |
| SSL cert problem | Self-signed cert → browser warning | Installer adds cert to OS trust store → no warnings ever |
| "Run Python script" | Requires Python installed + terminal knowledge | Auto-starts on login as a system tray app |
| CORS/CSP issues | Workarounds with Chrome flags | Gone — properly installed cert, no hacks needed |

### The Target UX (verbatim goal for the new conversation)
> *"Download the Numista.AI Desktop Agent → run installer (30 seconds) → it appears in system tray → open numista.ai → Microscope Scanner shows green 'Hardware Server Online' automatically"*

### What the new conversation needs to build

| Component | Details |
|---|---|
| **Packaging** | PyInstaller → single `.exe` (Windows) / `.app` (Mac) |
| **Installer** | NSIS or WiX for Windows; `.dmg` for Mac. Handles cert installation into OS trust store. |
| **System Tray App** | `pystray` library. Status icon (green/yellow/red). Right-click: Start/Stop, Open Dashboard, Quit. |
| **Auto-start on login** | Windows: registry `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`. Mac: LaunchAgent plist. |
| **SSL cert** | Installer adds `localhost.crt` to Windows/Mac OS cert store → Chrome trusts it natively. No flags, no warnings. |
| **Download page** | A `/download` route on numista.ai with Windows + Mac buttons. |

### Current workaround (for testing only)
Chrome flag `chrome://flags/#allow-insecure-localhost` + run `auto_capture.py` manually from terminal.  
Good enough to validate the AI grading workflow before investing in the installer build.

### Files already written (in `numista_hardware/`)
- `auto_capture.py` — core logic, 690 lines, production-ready
- `gen_cert.py` — cert generation script
- `localhost.crt` / `localhost.key` — already generated
- `identify_coin.py`, `pcgs_service.py` — dependencies

---

## 🔨 Full Feature Status

| Feature | Status | Notes |
|---|---|---|
| Home Dashboard | ✅ Live | Portfolio aggregation, melt value via yfinance |
| My Collection | ✅ Live | Firestore-backed, image support |
| Add Coins – Manual | ✅ Live | Standard form |
| Add Coins – CSV/Excel Upload | ✅ Live | Pandas-based column mapping |
| Add Coins – Invoice Scan (PDF) | ✅ **FIXED & DEPLOYED** | Gemini 2.5 Pro multimodal (no DocumentAI). Jun 14. |
| Coin Programs / Checklists | ✅ Live | US Mint program matching |
| Wishlist | ✅ Live | Firestore sub-collection |
| AI Numismatic Deepdive Chat | ✅ Live | Gemini via Vertex AI |
| Settings & Backup (JSON export) | ✅ Live | |
| PCGS Cert Number Lookup | ✅ Live | API token integrated, working |
| Coin Reference Search | ✅ Live | Vertex AI Search, 1,913+ entries |
| Morgan AI Avatar / Greeter | ✅ Phase 1 Live | Full-screen greeter with 4 action tiles deployed |
| Estate Planning Reports | 🔄 In Progress | NY & NC first; premium tier planned |
| Flutter Migration | 🔄 In Progress | Web + mobile platform |
| Microscope Auto-Capture | ⏳ Next Conversation | Desktop Agent sprint — see above |
| RAG Info Bot (numista_ai/) | 🔄 Planned | Reserved module, not started |

---

## 💡 Ideas & Features Not Yet Worked On

### 🔴 High Priority

#### 1. Guest Account / Onboarding Wizard
- Current guest: only 5 coins. Plan: **100 demo coins** (Silver Eagles, Mercury Dimes, Lincoln Cents, Morgan Dollars, 15 State Quarters, 2026 Semiquincentennial coins)
- Allow guests to use features (manual add, PDF scan, spreadsheet upload)
- Don't let guests download data, but allow uploads to feed Numista.AI's "brain"
- **Key idea:** step-by-step Wizard that walks users through every feature — dismissible at any time

#### 2. COA (Certificate of Authenticity) Review Feature
- Concept noted but file was saved blank. Likely extends PCGS/grading service integration to include COA document review.

#### 3. Invoice Scan Accuracy Improvements
- Now using Gemini 2.5 Pro multimodal — but edge case handling and accuracy on unusual invoice formats is still open.

---

### 🟡 Medium Priority

#### 4. Shareable "Gift List" + eBay Monetization
- Users generate a public, read-only wishlist link (e.g., `numista.ai/wishlist/eric-d`)
- Family clicks **"Find this on eBay"** → eBay Partner Network (EPN) affiliate link filtered by condition and price cap
- **Revenue model:** 1–4% commission on any eBay purchase made during that session (passive, no subscription required)

#### 5. Smart PCGS/Grading Service Enhancements
- Cert number → clickable link showing grading service data
- Dual-column schema: `Grading Service` + `Grading Certification Number` (NGC, ANACS, etc.)
- AI auto-check: entered data vs. PCGS return → prompt to reconcile mismatches
- Smart number parsing: auto-extract cert from full `986403.70/53652580` string
- Admin reminder every ~3 months to re-verify PCGS API token
- Display NFC anti-counterfeiting flag when `IsNFCSecure: true`

#### 6. Numista.AI "Info Bot" (RAG-powered)
- Chatbot grounded in: `numista_coins.db` (906KB), `master_coin_programs.json` (515KB), `training_output/` JSON
- Architecture slot already reserved: `numista_ai/` folder (currently empty)
- Could be a second tab/mode in the existing `AiChatScreen`
- RAG packages identified: `sentence-transformers`, `faiss-cpu`, `langchain-core`

#### 7. Attorney Portal for Estate Planning Reports
- Email link to a time-limited GCS signed URL
- Read-only attorney view of a client's estate report
- Tiered pricing: $4.99/month add-on or $29/year; $100/year for 5K+ coins or $250K+ collections

#### 8. Multi-State Estate Planning Expansion
- Currently: NY and NC first
- Next: NJ, Florida, CA, TX, SC
- Feature idea: let users request support for new states

---

### 🟢 Longer-Term / Future Vision

#### 9. Expand Beyond Coins
- Paper currency, foreign currency, stamps, comic books, family heirlooms
- **Sneaker/Air Jordan collection app** — owned sneakergeek.com in the 1990s; enabled by Numista.AI success

#### 10. Morgan AI Avatar — Remaining Phases
- **Phase 1:** ✅ Live — full-screen greeter with 4 action tiles
- **Phase 2 (Jul):** Guided narration strip during Invoice, Microscope, Review flows
- **Phase 3 (Aug):** Collection-aware chat (inject full collection summary before every Gemini call)
- **Phase 4 (Sep–Oct):** Voice push-to-talk (speech_to_text + flutter_tts)
- *Post-launch:* Proactive Morgan alerts; Morgan taking agentic actions

#### 11. Vertex AI Search / GenAI App Builder Deepdive
- Move AI Deepdive to a grounded GenAI App Builder agent
- $1,000 credit available (Credit ID noted in doc)
- Ground agent on `numista.db` + Official US Mint Terms list

#### 12. Connecting Numista.AI to NotebookLM
- Potentially using NotebookLM as a research/knowledge management layer

---

## 📋 Known Issues / Bug Tracker

| Issue | Status | Notes |
|---|---|---|
| **Upload via Scan (PDF)** | ✅ **FIXED & DEPLOYED** | Gemini 2.5 Pro multimodal. Revision `00061-lbh`. Jun 14. |
| **Orphan Cloud Run service** | ⚠️ Still exists | `numista-backend-qntvrqvxma-uc.a.run.app` is an old service on a different project. `constants.dart` points to this URL — should be reconciled. |
| **Microscope Scanner offline** | ⏳ Next conversation | Requires Desktop Agent packaging. Workaround: Chrome flag + run `auto_capture.py` manually. |
| **Review Hub 628 badge** | ❓ Unknown | 628 coins in review queue — expected backlog from testing? |
| **Morgan tour (Step 1 of 6)** | ⚠️ Minor | Tour popup re-appears on every login. Needs a "don't show again" Firestore flag per user. |

---

## 🗺️ Roadmap (Christmas 2026 Goal)

| Phase | Timeline | Goal |
|---|---|---|
| Phase 1: Foundation | Apr–Jun 2026 | Flutter shell + Firestore migration ✅ |
| Phase 2: The Core | Jul–Sep 2026 | Rebuild AI Deepdive + Invoice Scanning in Flutter |
| Phase 3: The Lens | Oct–Nov 2026 | Microscope integration → Desktop Agent |
| Phase 4: Launch | Dec 2026 | Security audit, Estate Planning finalized, Public Release |

---

## 🔑 Quick-Win Shortlist (Not Yet Started)

1. **Fix Guest Account** (100 coins + Wizard) — highest impact for new user conversion
2. **eBay Affiliate Wishlist Sharing** — passive revenue, builds on existing Wishlist feature
3. **Grading Service schema** (dual column: Service + Cert #) + clickable cert link
4. **RAG Info Bot** (`numista_ai/` module) — all assets already exist, zero production risk
5. **Morgan Phase 2** — guided narration strip (Phase 1 already live)

---

## 🗒️ Miscellaneous Notes

- **Google for Startups Cloud Program** accepted — onboarding guide on file
- **PCGS API token** is live and working
- **eBay EPN affiliate** program identified as passive monetization path
- **Apple** folder exists — App Store considerations noted
- **Beta Testing surveys** (Mar 2026) already conducted
- **GCP credits optimization** doc (10 JUN 26) — worth reviewing to reduce burn rate
- **Sheldon 1-70 scale doc** — standard coin grading scale reference
- **US Mint Coin Sets Images not Found doc** — tracking coverage gaps in coin imagery
- **Smithsonian** folder — digital asset policies (SD609, SD610)
