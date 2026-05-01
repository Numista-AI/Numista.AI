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
    ],
  };
}
