import '../models/program_model.dart';

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
          ChecklistVariety(
            id: 'P-UNC', 
            label: 'P (Uncirculated)', 
            referenceImagePath: 'attributed_state-quarter-$stateId-unc-obverse-philadelphia.jpg'
          ),
          ChecklistVariety(
            id: 'D-UNC', 
            label: 'D (Uncirculated)', 
            referenceImagePath: 'attributed_state-quarter-$stateId-unc-obverse-denver.jpg'
          ),
          ChecklistVariety(
            id: 'S-CLAD', 
            label: 'S (Proof - Clad)', 
            referenceImagePath: 'attributed_state-quarter-$stateId-proof-obverse.jpg'
          ),
          ChecklistVariety(
            id: 'S-SILVER', 
            label: 'S (Proof - Silver)', 
            referenceImagePath: 'attributed_state-quarter-$stateId-proof-silver-obverse.jpg'
          ),
          ChecklistVariety(
            id: 'S-SATIN', 
            label: 'S (Satin Finish)', 
            referenceImagePath: 'attributed_state-quarter-$stateId-satin-obverse.jpg'
          ),
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
      // Other programs can be refactored as needed, currently using empty/basic lists for backward compat
      CoinProgram(
        id: "bicentennial",
        name: "Bicentennial Program",
        url: "https://www.usmint.gov/learn/coin-and-medal-programs/bicentennial-coins",
        years: "1976",
        coins: [
          ProgramCoin(id: "quarter", name: "Quarter", varieties: [ChecklistVariety.fromId('P-UNC'), ChecklistVariety.fromId('D-UNC')]),
          ProgramCoin(id: "half", name: "Half Dollar", varieties: [ChecklistVariety.fromId('P-UNC'), ChecklistVariety.fromId('D-UNC')]),
          ProgramCoin(id: "dollar", name: "Dollar", varieties: [ChecklistVariety.fromId('P-UNC'), ChecklistVariety.fromId('D-UNC')]),
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
      )
    ],
    "Collectible Programs": [
      CoinProgram(
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
          ProgramCoin(id: "2026_innovation_dollar", name: "2026 American Innovation \$1 Coin (with 250 Privy)", varieties: [
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
      )
    ]
  };
}
