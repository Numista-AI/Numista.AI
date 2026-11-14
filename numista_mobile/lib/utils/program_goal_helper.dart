import '../models/program_model.dart';

class ProgramGoalHelper {
  static const String defaultAutoFillGoal = 'Circulation Only';

  /// Returns true if [variety] belongs to [goal].
  /// Variety-less slots (id.isEmpty) always count.
  static bool goalAllowsVariety(ChecklistVariety variety, String goal) {
    final id = variety.id.toUpperCase().trim();
    if (id.isEmpty) return true;

    switch (goal) {
      case 'Circulation Only':
        return isCirculationVariety(id);
      case 'Standard Set':
        if (isCirculationVariety(id)) return true;
        return id == 'S-CLAD' || id == 'S-PROOF' || id.startsWith('S-PROOF-');
      case 'Full Master Set':
      default:
        return true;
    }
  }

  /// True for P and D business-strike variety IDs (does NOT include Proofs, Satin, Silver, W).
  static bool isCirculationVariety(String id) {
    final upper = id.toUpperCase().trim();
    if (upper == 'P' || upper == 'D') return true;
    if (upper == 'P-UNC' || upper == 'D-UNC') return true;
    if (upper == 'P-T1' ||
        upper == 'P-T2' ||
        upper == 'D-T1' ||
        upper == 'D-T2') {
      return true;
    }
    if (upper.startsWith('P-PRIVY-') || upper.startsWith('D-PRIVY-')) {
      return true;
    }
    return false;
  }

  /// Extracts canonical raw physical mint mark ("P", "D", "S", "W", "CC", "O", or "").
  static String extractRawMintMark(ChecklistVariety variety) {
    final id = variety.id.toUpperCase().trim();
    if (id.isEmpty) return '';
    if (id.startsWith('CC')) return 'CC';
    final seg = id.split('-').first;
    if (const {'P', 'D', 'S', 'W', 'O', 'C'}.contains(seg)) return seg;
    return '';
  }

  /// Senior-friendly human label for both the Wish List UI and Family Email.
  static String describeVarietyForSenior(ChecklistVariety variety) {
    final id = variety.id.toUpperCase().trim();
    if (id.isEmpty) return 'Any Mint';
    if (id == 'P' || id == 'P-UNC') return 'P Mint (Philadelphia)';
    if (id == 'D' || id == 'D-UNC') return 'D Mint (Denver)';
    if (id == 'P-T1') return 'P Mint Type 1 (Philadelphia)';
    if (id == 'P-T2') return 'P Mint Type 2 (Philadelphia)';
    if (id == 'D-T1') return 'D Mint Type 1 (Denver)';
    if (id == 'D-T2') return 'D Mint Type 2 (Denver)';
    if (id == 'S-SILVER' || id == 'S-SILVER-PROOF') {
      return 'S Mint (San Francisco Silver Proof)';
    }
    if (id == 'S-PROOF' || id == 'S-CLAD' || id.startsWith('S-PROOF-')) {
      return 'S Mint (San Francisco Clad Proof)';
    }
    if (id == 'S-SATIN') return 'S Mint (San Francisco Satin Finish)';
    if (id.startsWith('W')) return 'W Mint (West Point)';
    if (id == 'CC') return 'CC Mint (Carson City)';
    if (id == 'O') return 'O Mint (New Orleans)';
    return variety.label.isNotEmpty ? variety.label : id;
  }

  /// Builds an unambiguous eBay coin search query including Year + Mint + Program + Design + Strike.
  static String buildEbayQuery({
    required CoinProgram program,
    required ProgramCoin coinSlot,
    required ChecklistVariety variety,
  }) {
    final parts = <String>[];
    if (coinSlot.year != null && coinSlot.year!.trim().isNotEmpty) {
      parts.add(coinSlot.year!.trim());
    }
    final mm = extractRawMintMark(variety);
    if (mm.isNotEmpty) parts.add(mm);
    parts.add(program.name.trim());
    parts.add(coinSlot.name.trim());

    final upperId = variety.id.toUpperCase().trim();
    if (upperId.contains('SILVER')) {
      parts.add('Silver Proof');
    } else if (upperId.contains('PROOF') || upperId == 'S-CLAD') {
      parts.add('Proof');
    } else if (upperId.contains('SATIN')) {
      parts.add('Satin Finish');
    } else if (upperId.contains('UNC')) {
      parts.add('Uncirculated');
    }
    parts.add('coin');
    return parts.where((p) => p.isNotEmpty).join(' ');
  }
}
