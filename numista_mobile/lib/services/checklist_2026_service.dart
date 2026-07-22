import 'package:cloud_firestore/cloud_firestore.dart';
import '../models/program_model.dart';
import 'coin_programs_data.dart';

class Checklist2026Service {
  static final FirebaseFirestore _db = FirebaseFirestore.instance;

  /// Fetches the Circulating Currency program definition.
  static Future<CoinProgram> getCurrencyProgram() async {
    try {
      final doc = await _db.collection('global_programs').doc('2026_semiquincentennial_currency').get();
      if (doc.exists) {
        return CoinProgram.fromMap(doc.data()!, doc.id);
      }
    } catch (e) {
      // Fallback below
    }
    // Return fallback from CoinProgramsData if Firestore is unavailable
    return _fallbackCurrencyProgram();
  }

  /// Fetches the Numismatic Collectibles program definition.
  static Future<CoinProgram> getCollectiblesProgram() async {
    try {
      final doc = await _db.collection('global_programs').doc('2026_semiquincentennial_collectibles').get();
      if (doc.exists) {
        return CoinProgram.fromMap(doc.data()!, doc.id);
      }
    } catch (e) {
      // Fallback below
    }
    // Return fallback from CoinProgramsData if Firestore is unavailable
    return _fallbackCollectiblesProgram();
  }

  static CoinProgram _fallbackCurrencyProgram() {
    // Generate fallback identical to what we seeded
    return const CoinProgram(
      id: "2026_semiquincentennial_currency",
      name: "2026 America250 - Circulating Currency",
      url: "https://www.usmint.gov/coins/coin-programs/semiquincentennial/",
      years: "2026",
      category: "Circulating Coin Programs",
      mintMarkLocations: "OBVERSE_PORTRAIT",
      coins: [
        ProgramCoin(id: "2026_cent", name: "1776 ~ 2026 Collectible Cent", varieties: [
          ChecklistVariety(id: "P-UNC", label: "P (Uncirculated)"),
          ChecklistVariety(id: "D-UNC", label: "D (Uncirculated)"),
          ChecklistVariety(id: "S-PROOF", label: "S (Proof - Clad)")
        ]),
        ProgramCoin(id: "2026_nickel", name: "1776 ~ 2026 Jefferson Nickel", varieties: [
          ChecklistVariety(id: "P-UNC", label: "P (Uncirculated)"),
          ChecklistVariety(id: "D-UNC", label: "D (Uncirculated)"),
          ChecklistVariety(id: "S-PROOF", label: "S (Proof - Clad)")
        ]),
        ProgramCoin(id: "2026_dime", name: "Emerging Liberty Dime", varieties: [
          ChecklistVariety(id: "P-UNC", label: "P (Uncirculated)"),
          ChecklistVariety(id: "D-UNC", label: "D (Uncirculated)"),
          ChecklistVariety(id: "S-PROOF", label: "S (Proof - Clad)"),
          ChecklistVariety(id: "S-SILVER", label: "S (Proof - Silver)")
        ]),
        ProgramCoin(id: "2026_quarter_mayflower", name: "America250 Quarter #1: Mayflower Compact", varieties: [
          ChecklistVariety(id: "P-UNC", label: "P (Uncirculated)"),
          ChecklistVariety(id: "D-UNC", label: "D (Uncirculated)"),
          ChecklistVariety(id: "S-PROOF", label: "S (Proof - Clad)"),
          ChecklistVariety(id: "S-SILVER", label: "S (Proof - Silver)")
        ]),
        ProgramCoin(id: "2026_quarter_valleyforge", name: "America250 Quarter #2: Revolutionary War", varieties: [
          ChecklistVariety(id: "P-UNC", label: "P (Uncirculated)"),
          ChecklistVariety(id: "D-UNC", label: "D (Uncirculated)"),
          ChecklistVariety(id: "S-PROOF", label: "S (Proof - Clad)"),
          ChecklistVariety(id: "S-SILVER", label: "S (Proof - Silver)")
        ]),
        ProgramCoin(id: "2026_quarter_declaration", name: "America250 Quarter #3: Declaration of Independence", varieties: [
          ChecklistVariety(id: "P-UNC", label: "P (Uncirculated)"),
          ChecklistVariety(id: "D-UNC", label: "D (Uncirculated)"),
          ChecklistVariety(id: "S-PROOF", label: "S (Proof - Clad)"),
          ChecklistVariety(id: "S-SILVER", label: "S (Proof - Silver)"),
          ChecklistVariety(id: "P-PRIVY-JULY4", label: "P (July 4th Privy Mark)"),
          ChecklistVariety(id: "D-PRIVY-JULY4", label: "D (July 4th Privy Mark)")
        ]),
        ProgramCoin(id: "2026_quarter_constitution", name: "America250 Quarter #4: U.S. Constitution", varieties: [
          ChecklistVariety(id: "P-UNC", label: "P (Uncirculated)"),
          ChecklistVariety(id: "D-UNC", label: "D (Uncirculated)"),
          ChecklistVariety(id: "S-PROOF", label: "S (Proof - Clad)"),
          ChecklistVariety(id: "S-SILVER", label: "S (Proof - Silver)")
        ]),
        ProgramCoin(id: "2026_quarter_gettysburg", name: "America250 Quarter #5: Gettysburg Address", varieties: [
          ChecklistVariety(id: "P-UNC", label: "P (Uncirculated)"),
          ChecklistVariety(id: "D-UNC", label: "D (Uncirculated)"),
          ChecklistVariety(id: "S-PROOF", label: "S (Proof - Clad)"),
          ChecklistVariety(id: "S-SILVER", label: "S (Proof - Silver)")
        ]),
        ProgramCoin(id: "2026_half_dollar", name: "Enduring Liberty Half Dollar", varieties: [
          ChecklistVariety(id: "P-UNC", label: "P (Uncirculated)"),
          ChecklistVariety(id: "D-UNC", label: "D (Uncirculated)"),
          ChecklistVariety(id: "S-PROOF", label: "S (Proof - Clad)"),
          ChecklistVariety(id: "S-SILVER", label: "S (Proof - Silver)")
        ])
      ],
    );
  }

  static CoinProgram _fallbackCollectiblesProgram() {
    return const CoinProgram(
      id: "2026_semiquincentennial_collectibles",
      name: "2026 America250 - Numismatic Collectibles",
      url: "https://www.usmint.gov/coins/coin-programs/semiquincentennial/",
      years: "2026",
      category: "Collectible Programs",
      mintMarkLocations: "MIXED",
      coins: [
        ProgramCoin(id: "2026_dollar_trump", name: "Commemorative Presidential Dollar: Donald J. Trump", varieties: [
          ChecklistVariety(id: "P-UNC", label: "P (Uncirculated)"),
          ChecklistVariety(id: "D-UNC", label: "D (Uncirculated)"),
          ChecklistVariety(id: "S-PROOF", label: "S (Proof - Clad)")
        ]),
        ProgramCoin(id: "2026_buffalo_gold", name: "1776 ~ 2026 American Buffalo Gold Coin (with 250 Privy)", varieties: [
          ChecklistVariety(id: "W-PROOF", label: "W (Proof)"),
          ChecklistVariety(id: "W-UNC", label: "W (Uncirculated)")
        ]),
        ProgramCoin(id: "2026_eagle_silver", name: "1776 ~ 2026 American Silver Eagle (with 250 Privy)", varieties: [
          ChecklistVariety(id: "W-PROOF", label: "W (Proof)"),
          ChecklistVariety(id: "S-PROOF", label: "S (Proof)"),
          ChecklistVariety(id: "W-UNC", label: "W (Uncirculated)"),
          ChecklistVariety(id: "P-UNC", label: "P (Uncirculated)")
        ]),
        ProgramCoin(id: "2026_eagle_gold", name: "1776 ~ 2026 American Gold Eagle (with 250 Privy)", varieties: [
          ChecklistVariety(id: "W-PROOF", label: "W (Proof)"),
          ChecklistVariety(id: "W-UNC", label: "W (Uncirculated)")
        ]),
        ProgramCoin(id: "2026_innovation_dollar", name: "2026 American Innovation $1 Coin (with 250 Privy)", varieties: [
          ChecklistVariety(id: "P-UNC", label: "P (Uncirculated)"),
          ChecklistVariety(id: "D-UNC", label: "D (Uncirculated)"),
          ChecklistVariety(id: "S-PROOF", label: "S (Proof)"),
          ChecklistVariety(id: "S-REVERSE-PROOF", label: "S (Reverse Proof)")
        ]),
        ProgramCoin(id: "2026_morgan_dollar", name: "2026 Morgan Silver Dollar (with 250 Privy)", varieties: [
          ChecklistVariety(id: "P-PROOF", label: "P (Proof)"),
          ChecklistVariety(id: "P-UNC", label: "P (Uncirculated)")
        ]),
        ProgramCoin(id: "2026_peace_dollar", name: "2026 Peace Silver Dollar (with 250 Privy)", varieties: [
          ChecklistVariety(id: "P-PROOF", label: "P (Proof)"),
          ChecklistVariety(id: "P-UNC", label: "P (Uncirculated)")
        ]),
        ProgramCoin(id: "2026_companion_medal", name: "2026 Semiquincentennial Companion Silver Medal", varieties: [
          ChecklistVariety(id: "P-PROOF", label: "P (Proof)")
        ])
      ],
    );
  }
}
