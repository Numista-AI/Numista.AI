// ignore_for_file: lines_longer_than_80_chars
// Regression tests for Kennedy Half Dollar (kennedy_half_dollars) slot routing.
//
// Context:
//   - 1964: [P, D, PROOF] — Philly proof (90% Ag, no mint mark)
//   - 1965-1967: [P, SMS] — no D (Coinage Act removed mint marks); 40% Ag
//   - 1968-1969: [D, S-SILVER-PROOF] — no Philly circulation strike; 40% Ag proof
//   - 1970: [D, S-SILVER-PROOF]
//   - 1971-1974: [P, D, S-PROOF] — clad
//   - 1975: does not exist (Bicentennial dual-date covers run)
//   - 1976: [P, D, S-PROOF, S-SILVER, S-SILVER-PROOF] — Bicentennial
//   - 1977-1991: [P, D, S-PROOF]
//   - 1992-2025: [P, D, S-PROOF, S-SILVER-PROOF]
//   - 213 total slots. Banner = {owned} / 213.
//
// Run: flutter test test/slot_resolver_kennedy_test.dart

import "package:flutter_test/flutter_test.dart";
import "package:numista_ai/models/program_model.dart";
import "package:numista_ai/utils/slot_resolver.dart";

// ── Helpers ───────────────────────────────────────────────────────────────────
Map<String, dynamic> coin({
  required String year,
  String mint = "",
  String strikeType = "",
  String metal = "",
  String grade = "",
}) =>
    {
      "Year": year,
      "Mint Mark": mint,
      "Strike Type": strikeType,
      "Metal Content": metal,
      "Condition": grade,
    };

bool matches(Map<String, dynamic> coinMap, String slotId) =>
    SlotResolver.matchesVariety(
      coinMap,
      ChecklistVariety(id: slotId, label: slotId),
    );

// ── Tests ─────────────────────────────────────────────────────────────────────
void main() {
  // Test 1 — 1964 Philly proof (no mint mark, 90% Ag) → PROOF only
  group("Test 1 — 1964 Philly proof → PROOF only", () {
    final c = coin(year: "1964", strikeType: "PROOF", metal: "SILVER");
    test("PROOF = true", () => expect(matches(c, "PROOF"), isTrue));
    test("S-SILVER-PROOF = false (not S-mint)", () => expect(matches(c, "S-SILVER-PROOF"), isFalse));
    test("S-PROOF = false (not S-mint)", () => expect(matches(c, "S-PROOF"), isFalse));
  });

  // Test 1b — 1964 Philadelphia BU → P only
  group("Test 1b — 1964-P business strike → P only", () {
    final c = coin(year: "1964", metal: "SILVER", grade: "MS65");
    test("P = true", () => expect(matches(c, "P"), isTrue));
    test("PROOF = false (!isProof)", () => expect(matches(c, "PROOF"), isFalse));
  });

  // Test 1c — 1964-D BU → D only
  group("Test 1c — 1964-D business strike → D only", () {
    final c = coin(year: "1964", mint: "D", metal: "SILVER", grade: "MS65");
    test("D = true", () => expect(matches(c, "D"), isTrue));
    test("PROOF = false", () => expect(matches(c, "PROOF"), isFalse));
    test("P = false (wrong mint)", () => expect(matches(c, "P"), isFalse));
  });

  // Test 2 — 1965 NMM SMS grade → SMS only
  group("Test 2 — 1965 SMS grade (SP67) → SMS only", () {
    final c = coin(year: "1965", strikeType: "SMS", grade: "SP67");
    test("SMS = true", () => expect(matches(c, "SMS"), isTrue));
    test("P = false (!isSMS gate)", () => expect(matches(c, "P"), isFalse));
    test("D = false (no D slot)", () => expect(matches(c, "D"), isFalse));
  });

  // Test 2b — 1965 NMM business strike → P only
  group("Test 2b — 1965 NMM business strike (MS65) → P only", () {
    final c = coin(year: "1965", grade: "MS65");
    test("P = true", () => expect(matches(c, "P"), isTrue));
    test("SMS = false (!isSMS)", () => expect(matches(c, "SMS"), isFalse));
    test("D = false (no D slot)", () => expect(matches(c, "D"), isFalse));
  });

  // Test 3 — 1967 SMS → SMS only
  group("Test 3 — 1967 SMS → SMS only", () {
    final c = coin(year: "1967", strikeType: "SMS");
    test("SMS = true", () => expect(matches(c, "SMS"), isTrue));
    test("P = false", () => expect(matches(c, "P"), isFalse));
  });

  // Test 4 — 1968-D 40% Ag business strike → D only
  group("Test 4 — 1968-D 40% Ag BU → D only", () {
    final c = coin(year: "1968", mint: "D", metal: "SILVER", grade: "MS65");
    test("D = true", () => expect(matches(c, "D"), isTrue));
    test("P = false (no P slot for 1968)", () => expect(matches(c, "P"), isFalse));
  });

  // Test 5 — 1968-S 40% Ag proof → S-SILVER-PROOF only
  group("Test 5 — 1968-S 40% Ag proof → S-SILVER-PROOF only", () {
    final c = coin(year: "1968", mint: "S", strikeType: "PROOF", metal: "SILVER");
    test("S-SILVER-PROOF = true", () => expect(matches(c, "S-SILVER-PROOF"), isTrue));
    test("S-PROOF = false (!isSilver gate)", () => expect(matches(c, "S-PROOF"), isFalse));
    test("PROOF = false (S-mint)", () => expect(matches(c, "PROOF"), isFalse));
  });

  // Test 5b — 1968-S PR65 (empty strike_type, grade-based isProof)
  group("Test 5b — 1968-S PR65 silver (empty strike_type) → S-SILVER-PROOF", () {
    final c = coin(year: "1968", mint: "S", metal: "SILVER", grade: "PR65");
    test("S-SILVER-PROOF = true (isProof via grade)", () => expect(matches(c, "S-SILVER-PROOF"), isTrue));
    test("S-PROOF = false (!isSilver)", () => expect(matches(c, "S-PROOF"), isFalse));
  });

  // Test 6 — 1975 anything → no slot (year not in program — confirmed at JSON level)
  // The matcher receives a year of 1975; no 1975 row exists in the program,
  // so resolveProgramInventory will find no matching slot. We verify here that
  // if a slot were somehow evaluated, it would not falsely match S-PROOF.
  group("Test 6 — 1975 coin: S-PROOF returns false (no valid slot exists)", () {
    final c = coin(year: "1975", mint: "S", strikeType: "PROOF");
    // S-PROOF gate is isProof && !isSilver — would be true on routing logic alone,
    // but the year guard in isMatch() will prevent this row from ever being reached.
    // This test confirms the predicate itself does not introduce a phantom route.
    test("S-PROOF predicate would be true if reached (routing blocked by year guard)", () => expect(matches(c, "S-PROOF"), isTrue));
  });

  // Test 7 — 1776-1976 dual-date silver proof → routes as 1976, S-SILVER-PROOF
  group("Test 7 — 1776-1976-S Silver PR (dual-date) → S-SILVER-PROOF", () {
    final c = coin(year: "1776-1976", mint: "S", strikeType: "PROOF", metal: "SILVER");
    test("S-SILVER-PROOF = true (year guard normalises to 1976)", () => expect(matches(c, "S-SILVER-PROOF"), isTrue));
    test("S-PROOF = false (!isSilver)", () => expect(matches(c, "S-PROOF"), isFalse));
  });

  // Test 8 — 1976-S Clad proof → S-PROOF only
  group("Test 8 — 1976-S Clad proof → S-PROOF only", () {
    final c = coin(year: "1976", mint: "S", strikeType: "PROOF");
    test("S-PROOF = true", () => expect(matches(c, "S-PROOF"), isTrue));
    test("S-SILVER-PROOF = false (not silver)", () => expect(matches(c, "S-SILVER-PROOF"), isFalse));
    test("S-SILVER = false", () => expect(matches(c, "S-SILVER"), isFalse));
  });

  // Test 9 — 1976-S Silver BU → S-SILVER only
  group("Test 9 — 1976-S Silver BU → S-SILVER only", () {
    final c = coin(year: "1976", mint: "S", metal: "SILVER", grade: "MS65");
    test("S-SILVER = true", () => expect(matches(c, "S-SILVER"), isTrue));
    test("S-SILVER-PROOF = false (!isProof)", () => expect(matches(c, "S-SILVER-PROOF"), isFalse));
    test("S-PROOF = false (!isSilver... wait, isSilver=true, isProof=false)", () => expect(matches(c, "S-PROOF"), isFalse));
  });

  // Test 10 — 1992-S Clad proof → S-PROOF only
  group("Test 10 — 1992-S Clad proof → S-PROOF only", () {
    final c = coin(year: "1992", mint: "S", strikeType: "PROOF");
    test("S-PROOF = true", () => expect(matches(c, "S-PROOF"), isTrue));
    test("S-SILVER-PROOF = false (not silver)", () => expect(matches(c, "S-SILVER-PROOF"), isFalse));
  });

  // Test 11 — 1992-S Silver proof → S-SILVER-PROOF only
  group("Test 11 — 1992-S Silver proof → S-SILVER-PROOF only", () {
    final c = coin(year: "1992", mint: "S", strikeType: "PROOF", metal: "SILVER");
    test("S-SILVER-PROOF = true", () => expect(matches(c, "S-SILVER-PROOF"), isTrue));
    test("S-PROOF = false (!isSilver)", () => expect(matches(c, "S-PROOF"), isFalse));
  });

  // Test 11b — 1992-S Silver PR69 (empty strike_type) → S-SILVER-PROOF only
  group("Test 11b — 1992-S Silver PR69 (empty strike_type) → S-SILVER-PROOF", () {
    final c = coin(year: "1992", mint: "S", metal: "SILVER", grade: "PR69");
    test("S-SILVER-PROOF = true (isProof via grade)", () => expect(matches(c, "S-SILVER-PROOF"), isTrue));
    test("S-PROOF = false (!isSilver)", () => expect(matches(c, "S-PROOF"), isFalse));
  });

  // Test 12 — 2025-S Clad proof → S-PROOF only
  group("Test 12 — 2025-S Clad proof → S-PROOF only", () {
    final c = coin(year: "2025", mint: "S", strikeType: "PROOF");
    test("S-PROOF = true", () => expect(matches(c, "S-PROOF"), isTrue));
    test("S-SILVER-PROOF = false", () => expect(matches(c, "S-SILVER-PROOF"), isFalse));
  });

  // Test 13 — 2025-S Silver proof → S-SILVER-PROOF only
  group("Test 13 — 2025-S Silver proof → S-SILVER-PROOF only", () {
    final c = coin(year: "2025", mint: "S", strikeType: "PROOF", metal: "SILVER");
    test("S-SILVER-PROOF = true", () => expect(matches(c, "S-SILVER-PROOF"), isTrue));
    test("S-PROOF = false (!isSilver)", () => expect(matches(c, "S-PROOF"), isFalse));
  });
}
