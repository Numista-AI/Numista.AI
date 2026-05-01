class ChecklistVariety {
  final String id; // e.g., 'P-UNC'
  final String label; // e.g., 'P (Uncirculated)'
  final String? imagePath; // Legacy
  final String? referenceImagePath; // Path in gs://us_mint_coin_images

  const ChecklistVariety({
    required this.id,
    required this.label,
    this.imagePath,
    this.referenceImagePath,
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
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'label': label,
      if (imagePath != null) 'imagePath': imagePath,
      if (referenceImagePath != null) 'referenceImagePath': referenceImagePath,
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

  @override
  bool operator ==(Object other) =>
      identical(this, other) || (other is CoinProgram && other.id == id);

  @override
  int get hashCode => id.hashCode;
}
