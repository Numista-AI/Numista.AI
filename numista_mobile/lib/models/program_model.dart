class ChecklistVariety {
  final String id; // e.g., 'P-UNC'
  final String label; // e.g., 'P (Uncirculated)'
  final String? imagePath; // Legacy
  final String? referenceImagePath; // Path in gs://us_mint_coin_images
  /// If true, item must carry a 250/SEMIQUINCENTENNIAL/AMERICA250 token in
  /// theme_subject or official_us_mint_title to match this slot.
  final bool? requiresPrivy;

  const ChecklistVariety({
    required this.id,
    required this.label,
    this.imagePath,
    this.referenceImagePath,
    this.requiresPrivy,
  });

  factory ChecklistVariety.fromId(String id) {
    String label = id;
    if (id == 'P-UNC')   label = 'P Unc';
    if (id == 'D-UNC')   label = 'D Unc';
    if (id == 'S-PROOF') label = 'S Proof';
    if (id == 'S-SILVER')label = 'S Silver';
    if (id == 'S-SATIN') label = 'S Satin';
    if (id == 'P-T1')    label = 'P Type 1';
    if (id == 'P-T2')    label = 'P Type 2';
    if (id == 'D-T1')    label = 'D Type 1';
    if (id == 'D-T2')    label = 'D Type 2';
    return ChecklistVariety(id: id, label: label);
  }

  factory ChecklistVariety.fromMap(Map<String, dynamic> map) {
    return ChecklistVariety(
      id: map['id'] ?? '',
      label: map['label'] ?? '',
      imagePath: map['imagePath'],
      referenceImagePath: map['referenceImagePath'],
      requiresPrivy: map['requiresPrivy'] as bool?,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'label': label,
      if (imagePath != null) 'imagePath': imagePath,
      if (referenceImagePath != null) 'referenceImagePath': referenceImagePath,
      if (requiresPrivy != null) 'requiresPrivy': requiresPrivy,
    };
  }
}

class ProgramCoin {
  final String id; // e.g., 'delaware'
  final String name; 
  final List<ChecklistVariety> varieties;
  final String? year;
  final String? referenceImagePath; // Fallback image for the whole coin type

  const ProgramCoin({
    required this.id,
    required this.name,
    required this.varieties,
    this.year,
    this.referenceImagePath,
  });

  factory ProgramCoin.fromMap(Map<String, dynamic> map) {
    return ProgramCoin(
      id: map['id'] ?? '',
      name: map['name'] ?? '',
      varieties: (map['varieties'] as List? ?? [])
          .map((v) {
            // Handle both Map format {'id':..,'label':..} and legacy String format 'P'
            if (v is Map<String, dynamic>) {
              return ChecklistVariety.fromMap(v);
            } else if (v is String) {
              return ChecklistVariety.fromId(v);
            }
            return ChecklistVariety.fromId(v.toString());
          })
          .toList(),
      year: map['year'],
      referenceImagePath: map['referenceImagePath'],
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'name': name,
      'varieties': varieties.map((v) => v.toMap()).toList(),
      if (year != null) 'year': year,
      if (referenceImagePath != null) 'referenceImagePath': referenceImagePath,
    };
  }
}

class CoinProgram {
  final String id;
  final String name;
  final String url;
  final String years;
  final String category;
  final String mintMarkLocations;
  /// One of: EDGE, OBVERSE_PORTRAIT, OBVERSE_DATE, REVERSE_EAGLE,
  /// REVERSE_LOWER, REVERSE_UPPER, MIXED, NONE
  final String? mintMarkType;
  /// Per-program human-readable mint mark location guidance.
  final String? mintMarkDescription;
  final List<ProgramCoin> coins;

  const CoinProgram({
    required this.id,
    required this.name,
    required this.url,
    required this.years,
    this.category = 'Other',
    this.mintMarkLocations = '',
    this.mintMarkType,
    this.mintMarkDescription,
    required this.coins,
  });

  factory CoinProgram.fromMap(Map<String, dynamic> map, String docId) {
    return CoinProgram(
      id: docId,
      name: map['name'] ?? '',
      url: map['url'] ?? '',
      years: map['years'] ?? '',
      category: map['category'] ?? 'Other',
      mintMarkLocations: map['mint_mark_locations'] ?? '',
      mintMarkType: map['mint_mark_type'],
      mintMarkDescription: map['mint_mark_description'],
      coins: (map['coins'] as List? ?? [])
          .map((c) => ProgramCoin.fromMap(c as Map<String, dynamic>))
          .toList(),
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'name': name,
      'url': url,
      'years': years,
      'category': category,
      'mint_mark_locations': mintMarkLocations,
      if (mintMarkType != null) 'mint_mark_type': mintMarkType,
      if (mintMarkDescription != null) 'mint_mark_description': mintMarkDescription,
      'coins': coins.map((c) => c.toMap()).toList(),
    };
  }

  /// Check if a database Program/Series name belongs to this program.
  bool matchesDbSeries(String dbSeries) {
    final dbLower = dbSeries.toLowerCase().trim();
    final progLower = name.toLowerCase().trim();

    if (dbLower.isEmpty) return false;

    // Direct substring matches
    if (dbLower.contains(progLower) || progLower.contains(dbLower)) {
      return true;
    }

    // 1. Presidential Dollars
    if (progLower == 'presidential dollars') {
      return dbLower.contains('presidential');
    }

    // 2. Sacagawea & Native American Dollars
    if (progLower == 'sacagawea & native american dollars') {
      return dbLower.contains('sacagawea') || dbLower.contains('native american');
    }

    // 3. American Innovation $1 Coin Program
    if (progLower == 'american innovation \$1 coin program') {
      return dbLower.contains('american innovation');
    }

    // 4. America the Beautiful Quarters (National Parks)
    if (progLower == 'america the beautiful quarters (national parks)') {
      return dbLower.contains('america the beautiful') || dbLower.contains('national park');
    }

    // 5. 50 State Quarters
    if (progLower == '50 state quarters') {
      return dbLower.contains('state quarters') || dbLower.contains('state and territory quarters');
    }

    // 6. Washington Quarters (Classic)
    if (progLower == 'washington quarters (classic)') {
      return dbLower.contains('washington') && dbLower.contains('quarter');
    }

    // 7. Lincoln Cents / Lincoln Wheat Pennies / Lincoln Memorial Cents / Lincoln Shield Cents
    if (progLower == 'lincoln cents') {
      return dbLower == 'lincoln cent' ||
             dbLower == 'lincoln cents' ||
             dbLower == 'lincoln head cent' ||
             dbLower == 'lincoln head penny' ||
             dbLower == 'lincoln penny';
    }
    if (progLower == 'lincoln wheat pennies') {
      return dbLower.contains('wheat cent') ||
             dbLower.contains('wheat penny') ||
             dbLower.contains('wheat pennies') ||
             dbLower.contains('wheat cents');
    }
    if (progLower == 'lincoln memorial cents') {
      return dbLower.contains('memorial');
    }
    if (progLower == 'lincoln shield cents') {
      return dbLower.contains('shield');
    }

    // 8. Flying Eagle & Indian Head Cents
    if (progLower == 'flying eagle & indian head cents') {
      return dbLower.contains('indian head') || dbLower.contains('flying eagle');
    }

    // 9. Liberty Head (V) Nickels
    if (progLower == 'liberty head (v) nickels') {
      return dbLower.contains('liberty head nickel') || dbLower.contains('v nickel');
    }

    // 10. Jefferson Nickels
    if (progLower == 'jefferson nickels') {
      return dbLower.contains('jefferson nickel');
    }

    // 11. Roosevelt Dimes
    if (progLower == 'roosevelt dimes') {
      return dbLower.contains('roosevelt dime');
    }

    // 12. Franklin Half Dollars
    if (progLower == 'franklin half dollars') {
      return dbLower.contains('franklin') && dbLower.contains('half');
    }

    // 13. Liberty Walking Half Dollars
    if (progLower == 'liberty walking half dollars') {
      return (dbLower.contains('liberty walking') || dbLower.contains('walking liberty')) && dbLower.contains('half');
    }

    // 14. Buffalo Nickels
    if (progLower == 'buffalo nickels') {
      return dbLower.contains('buffalo nickel');
    }

    // 15. Mercury Dimes
    if (progLower == 'mercury dimes') {
      return dbLower.contains('mercury');
    }

    // 16. Kennedy Half Dollars
    if (progLower == 'kennedy half dollars') {
      return dbLower.contains('kennedy');
    }

    // 17. Morgan Dollars
    if (progLower == 'morgan dollars') {
      return dbLower.contains('morgan');
    }

    // 18. Peace Dollars
    if (progLower == 'peace dollars') {
      return dbLower.contains('peace');
    }

    // 19. Eisenhower Dollars
    if (progLower == 'eisenhower dollars') {
      return dbLower.contains('eisenhower') || dbLower.contains('ike dollar');
    }

    // 20. Susan B. Anthony Dollars
    if (progLower == 'susan b. anthony dollars') {
      return dbLower.contains('susan b') || dbLower.contains('sba');
    }

    // 21. American Silver Eagles
    if (progLower == 'american silver eagles') {
      return dbLower.contains('silver eagle') || (dbLower.contains('american eagle') && !dbLower.contains('gold') && !dbLower.contains('platinum'));
    }

    // 22. American Women Quarters
    if (progLower == 'american women quarters') {
      return dbLower.contains('american women') || dbLower.contains('women\'s quarters') || dbLower.contains('women quarters');
    }

    // 23. U.S. Proof Sets & Uncirculated Sets
    if (progLower.contains('proof set') || progLower.contains('uncirculated set')) {
      return dbLower.contains('proof set') || dbLower.contains('uncirculated set') || dbLower.contains('mint set');
    }

    // 24. 2026 America250 / Semiquincentennial programs (v10 — tightened split)
    if (progLower.contains('2026') || progLower.contains('america250') ||
        progLower.contains('semiquincentennial')) {

      // CIRCULATING branch — new-design names + explicit circulating tags
      // 'semiquincentennial' in dbLower is circulating-only (coins storing that
      //  series tag are circulating redesigns, not privy bullion).
      // '250th anniversary' removed — belongs only in hasPrivy on the Collectibles side.
      // 'valley forge' removed — substring present in Native American $1 Polly Cooper reverse.
      // Bare '2026' not accepted — too broad.
      if (progLower.contains('circulating') || progLower.contains('currency')) {
        if (dbLower.contains('semiquincentennial') || dbLower.contains('america250')) {
          return true;
        }
        const circulatingDesigns = [
          'emerging liberty',           // dime
          'enduring liberty',           // half dollar
          'mayflower compact',
          'revolutionary war',          // quarter ('valley forge' alias removed)
          'declaration of independence',
          'u.s. constitution',
          'gettysburg address',
          '1776 ~ 2026',                // nickel (with spaces as per Mint copy)
          '1776~2026',                  // nickel (compact form)
        ];
        return circulatingDesigns.any((n) => dbLower.contains(n));
      }

      // COLLECTIBLES branch — parent series only
      // 'semiquincentennial' NOT accepted here: a coin tagged Semiquincentennial
      // is a circulating redesign; privy bullion keeps its parent series.
      // 'american eagle' excluded — too broad (Gold Eagle, Platinum Eagle, etc.)
      if (progLower.contains('collectible') || progLower.contains('numismatic')) {
        const collectibleSeries = [
          'silver eagle',
          'peace dollar',
          'morgan dollar',
          'american buffalo',
          'buffalo gold',
          'innovation dollar',
          'companion medal',
        ];
        return collectibleSeries.any((n) => dbLower.contains(n));
        // requiresPrivy gate in matchesVariety is the second required check.
      }
    }

    return false;
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) || (other is CoinProgram && other.id == id);

  @override
  int get hashCode => id.hashCode;
}
