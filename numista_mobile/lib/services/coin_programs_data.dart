import '../models/program_model.dart';

/// Static offline fallback for [ReferenceService].
///
/// Used ONLY when Firestore is unavailable (cold start with no cache).
///
/// SYNC RULE: Every variety id/label here must match master_coin_programs.json
/// and the live Firestore seed. If you edit one, edit all three.
///
/// Last synced: 2026-08-26 (Phase 1 + Grok corrections)
/// Slot counts  (must match Firestore after seed):
///   morgan_dollars                       = 106
///   barber_dimes                         = 75
///   kennedy_half_dollars                 = 215
///   american_women_quarters              = 100
///   american_innovation_dollars          = 228
///   2026_semiquincentennial_collectibles = 19
///
class CoinProgramsData {
  static List<ProgramCoin> _generateStateQuarters() {
    final states = [
      'Delaware', 'Pennsylvania', 'New Jersey', 'Georgia', 'Connecticut',
      'Massachusetts', 'Maryland', 'South Carolina', 'New Hampshire', 'Virginia',
      'New York', 'North Carolina', 'Rhode Island', 'Vermont', 'Kentucky',
      'Tennessee', 'Ohio', 'Louisiana', 'Indiana', 'Mississippi',
      'Illinois', 'Alabama', 'Maine', 'Missouri', 'Arkansas',
      'Michigan', 'Florida', 'Texas', 'Iowa', 'Wisconsin',
      'California', 'Minnesota', 'Oregon', 'Kansas', 'West Virginia',
      'Nevada', 'Nebraska', 'Colorado', 'North Dakota', 'South Dakota',
      'Montana', 'Washington', 'Idaho', 'Wyoming', 'Utah',
      'Oklahoma', 'New Mexico', 'Arizona', 'Alaska', 'Hawaii'
    ];

    return states.map((state) {
      final stateId = state.toLowerCase().replaceAll(' ', '_');
      return ProgramCoin(
        id: stateId,
        name: state,
        varieties: [
          ChecklistVariety(id: 'P-UNC', label: 'P (Uncirculated)',
              referenceImagePath: 'attributed_state-quarter-$stateId-unc-obverse-philadelphia.jpg'),
          ChecklistVariety(id: 'D-UNC', label: 'D (Uncirculated)',
              referenceImagePath: 'attributed_state-quarter-$stateId-unc-obverse-denver.jpg'),
          ChecklistVariety(id: 'S-CLAD', label: 'S (Proof - Clad)',
              referenceImagePath: 'attributed_state-quarter-$stateId-proof-obverse.jpg'),
          ChecklistVariety(id: 'S-SILVER', label: 'S (Proof - Silver)',
              referenceImagePath: 'attributed_state-quarter-$stateId-proof-silver-obverse.jpg'),
          ChecklistVariety(id: 'S-SATIN', label: 'S (Satin Finish)',
              referenceImagePath: 'attributed_state-quarter-$stateId-satin-obverse.jpg'),
        ],
      );
    }).toList();
  }

  static final Map<String, List<CoinProgram>> usPrograms = {
    "Circulating Coin Programs": [
      CoinProgram(
        id: "50state",
        name: "50 State Quarters Program",
        url: "https://www.usmint.gov/learn/coin-and-medal-programs/50-state-quarters",
        years: "1999-2008",
        coins: _generateStateQuarters(),
      ),
      CoinProgram(
        id: "bicentennial",
        name: "Bicentennial Program",
        url: "https://www.usmint.gov/learn/coin-and-medal-programs/bicentennial-coins",
        years: "1976",
        coins: [
          ProgramCoin(id: "quarter", name: "Quarter",
              varieties: [ChecklistVariety.fromId('P-UNC'), ChecklistVariety.fromId('D-UNC')]),
          ProgramCoin(id: "half",    name: "Half Dollar",
              varieties: [ChecklistVariety.fromId('P-UNC'), ChecklistVariety.fromId('D-UNC')]),
          ProgramCoin(id: "dollar",  name: "Dollar",
              varieties: [ChecklistVariety.fromId('P-UNC'), ChecklistVariety.fromId('D-UNC')]),
        ],
      ),
      CoinProgram(
        id: "2026_semiquincentennial_currency",
        name: "2026 America250 - Circulating Currency",
        url: "https://www.usmint.gov/coins/coin-programs/semiquincentennial/",
        years: "2026",
        category: "Circulating Coin Programs",
        mintMarkLocations: "OBVERSE_PORTRAIT",
        coins: [
          ProgramCoin(id: "2026_nickel", name: "1776 ~ 2026 Jefferson Nickel", varieties: [
            ChecklistVariety(id: "P-UNC",   label: "P (Uncirculated)"),
            ChecklistVariety(id: "D-UNC",   label: "D (Uncirculated)"),
            ChecklistVariety(id: "S-PROOF", label: "S (Proof - Clad)")
          ]),
          ProgramCoin(id: "2026_dime", name: "Emerging Liberty Dime", varieties: [
            ChecklistVariety(id: "P-UNC",    label: "P (Uncirculated)"),
            ChecklistVariety(id: "D-UNC",    label: "D (Uncirculated)"),
            ChecklistVariety(id: "S-PROOF",  label: "S (Proof - Clad)"),
            ChecklistVariety(id: "S-SILVER", label: "S (Proof - Silver)")
          ]),
          ProgramCoin(id: "2026_quarter_mayflower", name: "America250 Quarter #1: Mayflower Compact", varieties: [
            ChecklistVariety(id: "P-UNC",    label: "P (Uncirculated)"),
            ChecklistVariety(id: "D-UNC",    label: "D (Uncirculated)"),
            ChecklistVariety(id: "S-PROOF",  label: "S (Proof - Clad)"),
            ChecklistVariety(id: "S-SILVER", label: "S (Proof - Silver)")
          ]),
          ProgramCoin(id: "2026_quarter_valleyforge", name: "America250 Quarter #2: Revolutionary War", varieties: [
            ChecklistVariety(id: "P-UNC",    label: "P (Uncirculated)"),
            ChecklistVariety(id: "D-UNC",    label: "D (Uncirculated)"),
            ChecklistVariety(id: "S-PROOF",  label: "S (Proof - Clad)"),
            ChecklistVariety(id: "S-SILVER", label: "S (Proof - Silver)")
          ]),
          ProgramCoin(id: "2026_quarter_declaration", name: "America250 Quarter #3: Declaration of Independence", varieties: [
            ChecklistVariety(id: "P-UNC",         label: "P (Uncirculated)"),
            ChecklistVariety(id: "D-UNC",         label: "D (Uncirculated)"),
            ChecklistVariety(id: "S-PROOF",       label: "S (Proof - Clad)"),
            ChecklistVariety(id: "S-SILVER",      label: "S (Proof - Silver)"),
            ChecklistVariety(id: "P-PRIVY-JULY4", label: "P (July 4th Privy Mark)"),
            ChecklistVariety(id: "D-PRIVY-JULY4", label: "D (July 4th Privy Mark)")
          ]),
          ProgramCoin(id: "2026_quarter_constitution", name: "America250 Quarter #4: U.S. Constitution", varieties: [
            ChecklistVariety(id: "P-UNC",    label: "P (Uncirculated)"),
            ChecklistVariety(id: "D-UNC",    label: "D (Uncirculated)"),
            ChecklistVariety(id: "S-PROOF",  label: "S (Proof - Clad)"),
            ChecklistVariety(id: "S-SILVER", label: "S (Proof - Silver)")
          ]),
          ProgramCoin(id: "2026_quarter_gettysburg", name: "America250 Quarter #5: Gettysburg Address", varieties: [
            ChecklistVariety(id: "P-UNC",    label: "P (Uncirculated)"),
            ChecklistVariety(id: "D-UNC",    label: "D (Uncirculated)"),
            ChecklistVariety(id: "S-PROOF",  label: "S (Proof - Clad)"),
            ChecklistVariety(id: "S-SILVER", label: "S (Proof - Silver)")
          ]),
          ProgramCoin(id: "2026_half_dollar", name: "Enduring Liberty Half Dollar", varieties: [
            ChecklistVariety(id: "P-UNC",    label: "P (Uncirculated)"),
            ChecklistVariety(id: "D-UNC",    label: "D (Uncirculated)"),
            ChecklistVariety(id: "S-PROOF",  label: "S (Proof - Clad)"),
            ChecklistVariety(id: "S-SILVER", label: "S (Proof - Silver)")
          ]),
          ProgramCoin(id: "2026_native_american_dollar", name: "Native American \$1 Coin — Polly Cooper (Oneida Allies at Valley Forge)", varieties: [
            ChecklistVariety(id: "P-UNC",   label: "P (Uncirculated)"),
            ChecklistVariety(id: "D-UNC",   label: "D (Uncirculated)"),
            ChecklistVariety(id: "S-PROOF", label: "S (Proof - Clad)")
          ]),
          ProgramCoin(id: "2026_cent", name: "1776 ~ 2026 Collectible Cent", varieties: [
            ChecklistVariety(id: "P-UNC",   label: "P (Uncirculated)"),
            ChecklistVariety(id: "D-UNC",   label: "D (Uncirculated)"),
            ChecklistVariety(id: "S-PROOF", label: "S (Proof - Clad)")
          ])
        ],
      )
    ],
    "Collectible Programs": [
      // ── 2026 America250 Numismatic Collectibles ──────────────────────────────
      // 19 slots = Morgan(2) + Peace(2) + ASE(3) + AGE(2) + Buffalo(1)
      //           + Innovation Iowa/WI/CA/MN×P+D(8) + Trump(1)
      // Firestore doc: 2026_semiquincentennial_collectibles
      CoinProgram(
        id: "2026_semiquincentennial_collectibles",
        name: "2026 America250 - Numismatic Collectibles",
        url: "https://www.usmint.gov/coins/coin-programs/semiquincentennial/",
        years: "2026",
        category: "Collectible Programs",
        mintMarkLocations: "MIXED",
        coins: [
          ProgramCoin(id: "2026_morgan_reverse_proof",
            productFamily: "morgan",
            name: "2026 Morgan Silver Dollar Reverse Proof", year: "2026",
            varieties: [
              ChecklistVariety(id: "P-REVERSE-PROOF", label: "Philadelphia Reverse Proof (P)"),
            ]),
          ProgramCoin(id: "2026_peace_silver_dollar_reverse_proof",
            productFamily: "peace",
            name: "2026 Peace Silver Dollar Reverse Proof", year: "2026",
            varieties: [
              ChecklistVariety(id: "P-REVERSE-PROOF", label: "Philadelphia Reverse Proof (P)"),
            ]),
          ProgramCoin(id: "2026_morgan_silver_dollar_enhanced_uncirculated",
            productFamily: "morgan",
            name: "2026 Morgan Silver Dollar Enhanced Uncirculated", year: "2026",
            varieties: [
              ChecklistVariety(id: "EU",
                label: "Enhanced Uncirculated (struck at West Point; confirm mint mark on coin)"),
            ]),
          ProgramCoin(id: "2026_peace_silver_dollar_enhanced_uncirculated",
            productFamily: "peace",
            name: "2026 Peace Silver Dollar Enhanced Uncirculated", year: "2026",
            varieties: [
              ChecklistVariety(id: "EU",
                label: "Enhanced Uncirculated (struck at West Point; confirm mint mark on coin)"),
            ]),
          ProgramCoin(id: "2026_american_eagle_one_ounce_silver_proof_coin",
            productFamily: "ase",
            name: "2026 American Eagle One Ounce Silver Proof Coin", year: "2026",
            varieties: [
              ChecklistVariety(id: "W-PROOF", label: "West Point Proof 250 privy (W)"),
            ]),
          ProgramCoin(id: "2026_american_eagle_one_ounce_silver_enhanced_uncirculated_coin",
            productFamily: "ase",
            name: "2026 American Eagle One Ounce Silver Enhanced Uncirculated Coin", year: "2026",
            varieties: [
              ChecklistVariety(id: "W-EU", label: "West Point Enhanced Uncirculated (W)"),
            ]),
          ProgramCoin(id: "2026_american_eagle_one_ounce_silver_proof_coin_congratulations_set",
            productFamily: "ase",
            name: "2026 American Eagle One Ounce Silver Proof Coin (Congratulations Set)", year: "2026",
            varieties: [
              ChecklistVariety(id: "P-PROOF-CONG",
                label: "Philadelphia Proof — Congratulations Set (P)"),
            ]),
          ProgramCoin(id: "2026_american_eagle_one_ounce_gold_proof_coin",
            productFamily: "age",
            name: "2026 American Eagle One Ounce Gold Proof Coin", year: "2026",
            varieties: [
              ChecklistVariety(id: "W-PROOF", label: "West Point Proof (W)"),
            ]),
          ProgramCoin(id: "2026_american_eagle_one_ounce_gold_enhanced_uncirculated_coin",
            productFamily: "age",
            name: "2026 American Eagle One Ounce Gold Enhanced Uncirculated Coin", year: "2026",
            varieties: [
              ChecklistVariety(id: "W-EU", label: "West Point Enhanced Uncirculated (W)"),
            ]),
          ProgramCoin(id: "2026_american_buffalo_one_ounce_gold_proof_coin",
            productFamily: "buffalo",
            name: "2026 American Buffalo One Ounce Gold Proof Coin", year: "2026",
            varieties: [
              ChecklistVariety(id: "W-PROOF", label: "West Point Proof (W)"),
            ]),
          ProgramCoin(id: "2026_american_innovation_1_iowa",
            productFamily: "innovation:iowa",
            name: "2026 American Innovation \$1 — Iowa", year: "2026",
            varieties: [
              ChecklistVariety(id: "P", label: "Philadelphia (P)"),
              ChecklistVariety(id: "D", label: "Denver (D)"),
            ]),
          ProgramCoin(id: "2026_american_innovation_1_wisconsin",
            productFamily: "innovation:wisconsin",
            name: "2026 American Innovation \$1 — Wisconsin", year: "2026",
            varieties: [
              ChecklistVariety(id: "P", label: "Philadelphia (P)"),
              ChecklistVariety(id: "D", label: "Denver (D)"),
            ]),
          ProgramCoin(id: "2026_american_innovation_1_california",
            productFamily: "innovation:california",
            name: "2026 American Innovation \$1 — California", year: "2026",
            varieties: [
              ChecklistVariety(id: "P", label: "Philadelphia (P)"),
              ChecklistVariety(id: "D", label: "Denver (D)"),
            ]),
          ProgramCoin(id: "2026_american_innovation_1_minnesota",
            productFamily: "innovation:minnesota",
            name: "2026 American Innovation \$1 — Minnesota", year: "2026",
            varieties: [
              ChecklistVariety(id: "P", label: "Philadelphia (P)"),
              ChecklistVariety(id: "D", label: "Denver (D)"),
            ]),
          // Pending: on sale September 2, 2026 at noon ET. Philadelphia only.
          ProgramCoin(id: "2026_semiquincentennial_president_donald_j_trump_1_coin",
            productFamily: "trump",
            name: "2026 Semiquincentennial President Donald J. Trump \$1 Coin", year: "2026",
            varieties: [
              ChecklistVariety(id: "P",
                label: "Philadelphia (P) — On sale September 2, 2026"),
            ]),
        ],
      ),
    ]
  };
}
