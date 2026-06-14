# Morgan — Numista.AI's AI Concierge
**Goal:** Build an approachable, guided AI companion named **Morgan** that meets every user at the door, walks them step-by-step through the app, and speaks their language — especially for older or less tech-savvy collectors.

---

## The Vision

> *"I want someone who feels like I'm right there helping them."*

Morgan is NOT a chatbot in a corner. Morgan is a **presence** — a warm, patient guide that greets users by name, anticipates what they want to do, and narrates every step like a knowledgeable friend standing right beside them.

---

## Morgan's Avatar — Choose One

````carousel
![Morgan Option A — Circuit-Eye Owl](C:\Users\ericd\.gemini\antigravity\brain\9cba545f-9b75-465b-bab7-4ce58765d393\morgan_avatar_owl_1781037554633.png)
**Option A** — Closer to the original logo owl. Serious but approachable. Strong brand continuity.
<!-- slide -->
![Morgan Option B — Talking Owl](C:\Users\ericd\.gemini\antigravity\brain\9cba545f-9b75-465b-bab7-4ce58765d393\morgan_avatar_talking_1781037571153.png)
**Option B** — More expressive, beak-open "talking" pose. Warmer and more playful. More Duolingo-style companion feel.
````

> [!TIP]
> Either avatar works in the app as a PNG placed in `numista_mobile/assets/morgan_avatar.png`. We can also animate it in Flutter (gentle bob + blink + mouth open/close on speaking).

---

## Morgan's Persona

| Trait | Description |
|---|---|
| **Name** | Morgan (as in Morgan Dollar — every collector gets it immediately) |
| **Personality** | Warm, patient, encouraging, expert — never condescending |
| **Avatar** | Friendly owl with a coin monocle — navy & gold color scheme |
| **Voice** | Clear, calm, measured (not robotic) — uses plain English always |
| **Tone examples** | "Great choice!" / "Don't worry, I'll take care of the hard part." / "Nice! That's a beautiful coin." |
| **Never says** | "Invoice ingestion" / "Firestore" / "API" / "Upload failed with status 400" |

---

## Architecture Overview

```
Morgan lives in THREE places:

1. MORGAN GREETER (full-screen overlay)
   └── Shown on first login AND optionally on return visits
   └── "What would you like to do today?"
   └── 4 large action tiles + free-text/voice input

2. MORGAN STEP GUIDE (contextual coach marks)
   └── Narration panel that rides alongside each screen
   └── Step-by-step: "Now tap the blue button..."
   └── Celebrates completions: "🎉 Added! Great job."

3. MORGAN CHAT (upgraded AiChatScreen)
   └── Renamed "Chat with Morgan" in sidebar
   └── Collection-aware context injected into every prompt
   └── Voice input (push-to-talk) + TTS output
```

---

## Phased Implementation

---

### Phase 1 — The Morgan Greeter ✅ BUILDING NOW
**Timeline:** This week  
**Files:** NEW `morgan_greeter.dart`, MODIFY `welcome_screen.dart`, `base_layout.dart`

#### What It Does
Replaces the current static `WelcomeScreen` with an animated, conversational greeter that:
- Shows Morgan's avatar with a gentle pulse animation
- Greets the user by first name (pulled from Firebase Auth)
- Presents 4 large, plain-English action tiles
- Includes a free-text "just ask" input at the bottom
- Works on first login AND can be recalled from anywhere via a Morgan FAB button

#### Action Tiles
| Tile | Icon | Plain-English Label | Routes to |
|---|---|---|---|
| 📄 | receipt_long | "Add coins from a purchase receipt or invoice" | Add New Coins → Invoice tab |
| 🔬 | biotech | "Identify a coin with the Microscope" | Microscope Scanner |
| 📱 | photo_camera | "Take a photo to identify a coin" | Add New Coins → Photo tab |
| 🗂️ | collections_bookmark | "Browse my collection" | My Collection |

#### Design
- Full-screen overlay on dark navy (`0xFF0F172A`) background
- Morgan avatar (animated gentle bob) at top
- Greeting: `"Hello, Eric! 👋 What would you like to do today?"`
- Tiles: large, rounded, high-contrast, minimum 72px tap target
- Bottom: `"Or just ask me anything..."` text field + 🎙️ mic button (Phase 4)
- Subtle fade-in animation on load

#### New SharedPrefs Key
`morgan_greeter_seen` — separate from `welcome_seen` so Morgan can optionally re-appear on return visits (configurable in Settings).

---

### Phase 2 — Guided Step Flows
**Timeline:** July 2026  
**Files:** NEW `morgan_guide_panel.dart`, modify each relevant screen

#### What It Does
A persistent narration strip that rides at the bottom of the screen during multi-step flows. Morgan talks the user through each step:

**Example — Invoice Flow:**
```
Step 1: [Morgan panel] "Great! Let's add your coins. 
         Do you have a receipt or PDF invoice? 
         Tap the camera icon to take a photo, 
         or the folder icon to pick a file."
         
Step 2: [After upload] "Perfect! I'm reading your 
         invoice now... 🔍"

Step 3: [Results] "I found 8 coins! Take a look 
         below. Do any look wrong? Just tap one 
         to fix it."

Step 4: [After approve] "🎉 All 8 coins added to 
         your collection. You're doing great!"
```

#### Implementation
- `MorganGuidePanel` widget: dismissable bottom card with avatar, speech bubble, and action hint
- State machine: each screen gets a `List<MorganStep>` defining narration text per state
- Non-blocking: users can always dismiss or ignore Morgan
- Morgan remembers where the user was — if they navigate away and back, guide resumes

#### Screens to Add Guide To
1. `add_coins_hub.dart` — Invoice tab flow
2. `microscope_scan_screen.dart` — Scan flow
3. `review_hub_screen.dart` — Approve/commit flow

---

### Phase 3 — Collection-Aware Chat
**Timeline:** August 2026  
**Files:** MODIFY `ai_chat_screen.dart`, `numista_backend/main.py`

#### What It Does
Upgrades the existing `AiChatScreen` so Morgan actually KNOWS your collection before answering:

**Before (today):**
- Sends just the user's question to Gemini
- Gemini answers with general numismatic knowledge only

**After (Morgan):**
- Before every query, fetches a collection summary from Firestore:
  - Total coins, total estimated value
  - Top 5 most valuable coins
  - Programs being collected + completion %
  - Recent additions (last 30 days)
  - Wishlist items
- Injects this summary as system context into every Gemini call
- Result: Morgan answers like it knows YOU

**Example conversations after Phase 3:**
> *"Which of my Morgan Dollars is worth the most?"* → Actual answer about the user's specific coins  
> *"What am I missing in my Roosevelt Dime set?"* → Actual gap analysis  
> *"Should I sell anything right now?"* → Advice based on their actual collection  

#### Sidebar rename
`AI Deepdive` → `Chat with Morgan` (with Morgan avatar in the header)

#### Backend
New endpoint: `GET /api/morgan/context?user_email=...`  
Returns a structured collection summary JSON, cached for 5 minutes.

---

### Phase 4 — Voice (Push-to-Talk)
**Timeline:** September–October 2026  
**Flutter packages:** `speech_to_text`, `flutter_tts`

#### What It Does
- 🎙️ **Microphone button** in Morgan Greeter + Chat: tap-and-hold to speak
- Speech transcribed → sent to Gemini as text → response read aloud
- TTS voice: warm, slightly slower pace (configurable in Settings)
- Works on web (Web Speech API) and mobile (native STT)

#### User flow
```
User taps 🎙️ → "I'm listening..." appears
User speaks: "What's my most valuable coin?"
Morgan hears → sends to Gemini → gets answer
Morgan speaks: "Your most valuable coin is your 
               1921 Morgan Dollar, graded MS-63, 
               currently estimated at $95."
Text also displayed in chat for reference.
```

#### Accessibility note
Voice is ALWAYS optional — every voice action is also available via typing.  
Settings screen will have: `Morgan Voice` toggle (on/off) + speed slider.

---

## File Map

### New Files
| File | Purpose |
|---|---|
| `lib/widgets/morgan_greeter.dart` | Full-screen greeter overlay (Phase 1) |
| `lib/widgets/morgan_guide_panel.dart` | Step narration strip (Phase 2) |
| `lib/services/morgan_service.dart` | Collection context fetch + Morgan state (Phase 3) |

### Modified Files
| File | Change |
|---|---|
| `lib/screens/welcome_screen.dart` | Replace content with Morgan greeter redirect |
| `lib/screens/base_layout.dart` | Add Morgan FAB button (recall greeter anytime) |
| `lib/screens/ai_chat_screen.dart` | Rename to Morgan, inject collection context |
| `lib/screens/add_coins_hub.dart` | Add Phase 2 guide panel |
| `lib/screens/microscope_scan_screen.dart` | Add Phase 2 guide panel |
| `numista_backend/main.py` | Add `/api/morgan/context` endpoint |

---

## Design Standards for Morgan

### Language Rules
| ❌ Never say | ✅ Say instead |
|---|---|
| "Upload failed" | "That didn't go through — want to try again?" |
| "Processing invoice" | "I'm reading your receipt..." |
| "Firestore write successful" | "Saved! Your coin is in your collection." |
| "Navigate to Review Hub" | "Take a look at what I found — tap 'Review'" |
| "API error 400" | "Something went wrong — let's try that again." |

### Tap Target Rules
- All Morgan action tiles: minimum **72px tall**
- All Morgan buttons: minimum **48px tall**
- Font size in Morgan panels: minimum **15px**
- Never more than **4 choices** at once

### Animation Guidelines
- Avatar: gentle 3-second bob (up 4px, down 4px, loop)
- Tile selection: scale to 0.97 on press, back to 1.0
- Morgan panel: slide-up from bottom (300ms, ease-out curve)
- Greeting text: fade-in letter by letter (optional — subtle)

---

## Verification Plan

### Phase 1 Verification
- [ ] Greeter appears on new account (empty Firestore)
- [ ] Greeter does NOT appear for existing users with coins
- [ ] All 4 tiles navigate to correct screen
- [ ] "Skip for now" works and greeter doesn't re-appear same session
- [ ] Morgan FAB in sidebar recalls greeter correctly
- [ ] Works on mobile (< 800px) AND desktop (sidebar) layouts
- [ ] Displays correctly on tablet (iPad Pro 12.9")

### Phase 2 Verification
- [ ] Invoice guide narrates each step in correct order
- [ ] Dismissing guide doesn't break the underlying screen
- [ ] Guide resumes correctly after navigate-away-and-back
- [ ] Celebration message appears after successful coin add

### Phase 3 Verification  
- [ ] Morgan correctly names user's most valuable coin
- [ ] Collection context is injected in every message (check backend logs)
- [ ] Context caches properly (5 min TTL)
- [ ] Falls back gracefully if context fetch fails (still answers, just without personal data)

### Phase 4 Verification
- [ ] Mic button activates speech recognition on Chrome/Edge (web)
- [ ] Mic button activates native STT on Android
- [ ] TTS reads Morgan's response clearly
- [ ] Voice toggle in Settings correctly silences TTS
- [ ] Entire experience works without voice (typing only path unchanged)

---

## Nov 1, 2026 Launch Scope

| Feature | In Launch? |
|---|---|
| Morgan Greeter (Phase 1) | ✅ Yes |
| Guided Invoice Flow (Phase 2) | ✅ Yes |
| Guided Microscope Flow (Phase 2) | ✅ Yes |
| Collection-aware chat (Phase 3) | ✅ Yes |
| Voice push-to-talk (Phase 4) | ✅ Yes (if Phase 3 stable by Oct) |
| Always-listening voice | ❌ Post-launch |
| Morgan proactive alerts | ❌ Post-launch |
| Morgan takes actions (agentic) | ❌ Post-launch |
