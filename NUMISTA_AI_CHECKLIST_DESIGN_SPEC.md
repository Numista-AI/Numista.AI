# Numista.AI Native Checklist — Design Specification

**Created:** April 16, 2026  
**Status:** Design Phase — Not Yet Implemented

---

## Background & Motivation

Littleton Coin Company checklists are the most common physical checklist format used by
older coin collectors. However, they have proven extremely difficult to parse reliably with
Document AI due to several structural issues:

| Littleton Problem | Impact |
|---|---|
| Checkboxes encoded as **Wingdings font characters** (U+F0A6, U+F06D, U+00A6) | Must detect Unicode glyphs instead of actual visual circles |
| Some PDFs use **non-embedded fonts** (Kennedy, Roosevelt Dime series) | Results in U+FFFD replacement chars — completely undetectable |
| **Mixed column layouts** — some years have 1 circle, others 3 (P/D/S) on one row | Hard to model consistently; ambiguous which mint mark owns which circle |
| **Decorative headers and magazine-style layout** | Low information density, complex bounding box relationships |
| Small, tightly-spaced radio buttons with no clear text anchoring | Low confidence bounding boxes in Document AI |

### The Core Insight
Rather than continuing to reverse-engineer Littleton's format, we design **our own checklist**
optimized from the ground up for:
1. **Older users** who print it at home and fill it in by hand
2. **Document AI extraction** after it's scanned/photographed

---

## Design Goals

### For the User (Printability & Usability)
- Large, easy-to-read text (minimum 12pt body, 14pt coin identifiers)
- Generous checkbox size (at least 0.25" × 0.25") — easy to check with a pen
- Clean visual hierarchy — clear program header, grouped by denomination/series
- Prints cleanly on standard US Letter paper (8.5" × 11")
- Works in black and white (no color-dependent information)
- Portrait orientation with comfortable margins

### For Document AI (Machine Readability)
- **One row per YEAR GROUP** — coins are grouped by year, with separate mint mark checkboxes on the same row
- **Standard printed square checkboxes** — NOT Wingdings, NOT Unicode circles
- **Fixed column layout** — Year | □P | □D | □S | □S-SLV | Notes:
  ```
  Year    │ P  │ D  │ S  │ S-SLV │ Notes
  ────────┼────┼────┼────┼───────┼──────────────────
  1921    │ □  │    │    │       │ High Relief
  1922    │ □  │ □  │ □  │       │
  1923    │ □  │    │ □  │       │
  1950    │ □  │    │    │       │ Proof
  ```
- **Empty cell = mint not issued** that year (no checkbox drawn) — Document AI interprets blank as N/A
- **Checkbox always in same column per mint** — P always column 2, D column 3, S column 4, S-SLV column 5
- **Year always in column 1** — clear anchor for each row
- **High contrast** — black text on white, no decorative backgrounds
- **Plain embedded fonts** — no Wingdings, no Symbol, no decorative typefaces
- **Machine-readable header** with program metadata:
  - Series name (e.g., "PEACE DOLLAR SERIES")
  - Year range (e.g., "1921–1935, 2021, 2023")
  - Denomination (e.g., "Silver Dollar")
  - Numista.AI logo + "Print and check the coins you own"

> 💡 **Why grouped layout?** Littleton puts each mint mark on its OWN separate row  
> (e.g., 1937, 1937-D, 1937-S = 3 rows). This wastes space and creates schema ambiguity.  
> Our format groups by year with per-mint checkboxes — more compact, more legible for older  
> users, and directly maps to a clean schema.

---

## Schema Alignment

**Two schemas — used for different scenarios:**

### Schema A: v4 (Littleton format — current labeling target)
Used when a checklist puts EACH MINT MARK on its own separate row:
```
○ 1937         
○ 1937-D       
○ 1937-S       
```
| Field | Value | How determined |
|---|---|---|
| `coin_subject` | `"1937-D"` | Full printed text of that row |
| `is_owned` | `true/false` | Whether that row's circle is filled |

Mint mark is **already in the subject** — `is_owned` simply = did they fill the circle.

---

### Schema B: Grouped (Numista.AI native format)
Used when ONE row covers a year with MULTIPLE mint mark checkboxes:
```
1937:  □P  ☑D  □S
```
| Field | Value | How determined |
|---|---|---|
| `coin_subject` | `"1937"` | Year text in column 1 |
| `has_p` | `false` | Philadelphia checkbox filled? |
| `has_d` | `true` | Denver checkbox filled? |
| `has_s` | `false` | San Francisco checkbox filled? |
| `has_s_slv` | `false` | Silver/proof-S checkbox filled? |

Ownership is captured **per mint mark directly** — no `is_owned` field needed because  
the `has_*` fields ARE the ownership indicators.

> ✅ This is why `has_d/p/s/s_slv` were in the original v3 schema — they're correct for  
> the grouped layout. The v4 `is_owned` schema is correct for the per-row Littleton layout.  
> **Both schemas are valid — for different checklist formats.**

**Numista.AI native format uses Schema B.**

---

## Implementation Plan

### Phase 1: Template Design
- Design a Flutter-based PDF generator (or Python `reportlab` script) that produces
  a Numista.AI branded checklist PDF from our Reference Library data
- Output format: PDF, US Letter, portrait, black & white friendly

### Phase 2: Backend Integration
- Add `format: "numista"` detection to `_detect_checklist_format()` in `main.py`
- Add a dedicated Document AI processor (or processor version) trained on Numista.AI format
- This processor will be the highest-confidence path since we control the source format

### Phase 3: Flutter App Feature
- Allow users to select a coin program from the Reference Library
- Tap "Print Checklist" → generates a PDF → share sheet (AirPrint, Google Print, etc.)
- After user fills it out and scans/photographs it → run through the checklist pipeline
- Ownership data auto-populates their Numista.AI collection

---

## Why This Matters

The Numista.AI format becomes a **closed loop**:

```
App generates checklist PDF
         ↓
User prints → fills in owned coins
         ↓
User scans/photographs → uploads to app
         ↓
Document AI extracts with near-perfect accuracy (our format, our training data)
         ↓
Collection auto-populated ✅
```

This is particularly powerful for:
- **Onboarding new users** who already have physical collections
- **Older collectors** who prefer paper but want digital tracking
- **Estate/inheritance scenarios** where someone catalogues an inherited collection

---

## Competitive Advantage

No other coin collecting app offers a paper-to-digital pipeline designed this way.
Littleton, PCGS, NGC all have digital tools but none close the print → scan → ingest loop.
This is a differentiator that specifically serves the older collector demographic.

---

## Open Questions / Next Steps

- [ ] Choose PDF generation approach: Flutter plugin vs Python `reportlab` vs HTML-to-PDF
- [ ] Decide on checkbox style: Unicode `☐`/`☑` vs printed rectangle outline (which does Document AI handle better?)
- [ ] Determine which coin programs to support first (50 State Quarters, Peace Dollars, Lincoln Cents?)
- [ ] Add Numista.AI branding guidelines to the checklist template
- [ ] Prototype one checklist PDF and test Document AI detection accuracy vs Littleton format

---

*Concept origin: April 16, 2026 — Eric identified that designing our own format would     
sidestep persistent Littleton parsing problems while serving the older-collector use case.*
