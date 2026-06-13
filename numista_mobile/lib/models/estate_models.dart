import 'package:cloud_firestore/cloud_firestore.dart';

// ─────────────────────────────────────────────────────────────────────────────
// Community property states
// ─────────────────────────────────────────────────────────────────────────────
const Set<String> _communityPropertyStates = {'CA', 'TX', 'NV', 'WA', 'AZ', 'ID', 'NM', 'WI', 'LA'};

// ─────────────────────────────────────────────────────────────────────────────
// EstateBeneficiary — stored as a list inside estate_profile document
// ─────────────────────────────────────────────────────────────────────────────
class EstateBeneficiary {
  final String id;
  final String name;
  final String relationship; // 'Spouse', 'Child', 'Sibling', 'Friend', 'Charity', 'Other'
  final String njClass;      // 'A', 'C', 'D', 'E' — NJ inheritance tax class
  final String email;
  final String notes;

  const EstateBeneficiary({
    required this.id,
    required this.name,
    this.relationship = 'Other',
    this.njClass = 'D',
    this.email = '',
    this.notes = '',
  });

  factory EstateBeneficiary.fromMap(Map<String, dynamic> m) {
    return EstateBeneficiary(
      id:           m['id']?.toString() ?? '',
      name:         m['name']?.toString() ?? '',
      relationship: m['relationship']?.toString() ?? 'Other',
      njClass:      m['njClass']?.toString() ?? 'D',
      email:        m['email']?.toString() ?? '',
      notes:        m['notes']?.toString() ?? '',
    );
  }

  Map<String, dynamic> toMap() => {
    'id':           id,
    'name':         name,
    'relationship': relationship,
    'njClass':      njClass,
    'email':        email,
    'notes':        notes,
  };

  EstateBeneficiary copyWith({
    String? id,
    String? name,
    String? relationship,
    String? njClass,
    String? email,
    String? notes,
  }) {
    return EstateBeneficiary(
      id:           id ?? this.id,
      name:         name ?? this.name,
      relationship: relationship ?? this.relationship,
      njClass:      njClass ?? this.njClass,
      email:        email ?? this.email,
      notes:        notes ?? this.notes,
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// EstateProfile — stored at users/{uid}/estate_profile (single document)
// ─────────────────────────────────────────────────────────────────────────────
class EstateProfile {
  final String ownerName;
  final String ownerEmail;
  final String jurisdiction;          // state code: 'NY', 'NC', etc.
  final String maritalStatus;         // 'Single', 'Married', 'Widowed', 'Divorced'
  final String executorName;
  final String executorEmail;
  final String executorPhone;
  final String attorneyName;
  final String attorneyEmail;
  final String attorneyFirm;
  final String attorneyPhone;
  final String willOrTrustStatus;     // 'Has Will', 'Has Trust', 'Has Both', 'Neither', 'Unknown'
  final List<EstateBeneficiary> beneficiaries;
  final bool isMarried;
  final String maritalPropertyNotes;
  final DateTime? lastUpdated;

  const EstateProfile({
    this.ownerName = '',
    this.ownerEmail = '',
    this.jurisdiction = '',
    this.maritalStatus = 'Single',
    this.executorName = '',
    this.executorEmail = '',
    this.executorPhone = '',
    this.attorneyName = '',
    this.attorneyEmail = '',
    this.attorneyFirm = '',
    this.attorneyPhone = '',
    this.willOrTrustStatus = 'Unknown',
    this.beneficiaries = const [],
    this.isMarried = false,
    this.maritalPropertyNotes = '',
    this.lastUpdated,
  });

  bool get isCommunityPropertyState => _communityPropertyStates.contains(jurisdiction);

  factory EstateProfile.fromFirestore(DocumentSnapshot doc) {
    final m = doc.data() as Map<String, dynamic>? ?? {};
    return EstateProfile(
      ownerName:          m['ownerName']?.toString() ?? '',
      ownerEmail:         m['ownerEmail']?.toString() ?? '',
      jurisdiction:       m['jurisdiction']?.toString() ?? '',
      maritalStatus:      m['maritalStatus']?.toString() ?? 'Single',
      executorName:       m['executorName']?.toString() ?? '',
      executorEmail:      m['executorEmail']?.toString() ?? '',
      executorPhone:      m['executorPhone']?.toString() ?? '',
      attorneyName:       m['attorneyName']?.toString() ?? '',
      attorneyEmail:      m['attorneyEmail']?.toString() ?? '',
      attorneyFirm:       m['attorneyFirm']?.toString() ?? '',
      attorneyPhone:      m['attorneyPhone']?.toString() ?? '',
      willOrTrustStatus:  m['willOrTrustStatus']?.toString() ?? 'Unknown',
      beneficiaries: (m['beneficiaries'] as List<dynamic>? ?? [])
          .map((e) => EstateBeneficiary.fromMap(e as Map<String, dynamic>))
          .toList(),
      isMarried:            m['isMarried'] == true,
      maritalPropertyNotes: m['maritalPropertyNotes']?.toString() ?? '',
      lastUpdated: m['lastUpdated'] is Timestamp
          ? (m['lastUpdated'] as Timestamp).toDate()
          : null,
    );
  }

  Map<String, dynamic> toFirestore() => {
    'ownerName':          ownerName,
    'ownerEmail':         ownerEmail,
    'jurisdiction':       jurisdiction,
    'maritalStatus':      maritalStatus,
    'executorName':       executorName,
    'executorEmail':      executorEmail,
    'executorPhone':      executorPhone,
    'attorneyName':       attorneyName,
    'attorneyEmail':      attorneyEmail,
    'attorneyFirm':       attorneyFirm,
    'attorneyPhone':      attorneyPhone,
    'willOrTrustStatus':  willOrTrustStatus,
    'beneficiaries':      beneficiaries.map((b) => b.toMap()).toList(),
    'isMarried':          isMarried,
    'maritalPropertyNotes': maritalPropertyNotes,
    'lastUpdated':        FieldValue.serverTimestamp(),
  };

  EstateProfile copyWith({
    String? ownerName,
    String? ownerEmail,
    String? jurisdiction,
    String? maritalStatus,
    String? executorName,
    String? executorEmail,
    String? executorPhone,
    String? attorneyName,
    String? attorneyEmail,
    String? attorneyFirm,
    String? attorneyPhone,
    String? willOrTrustStatus,
    List<EstateBeneficiary>? beneficiaries,
    bool? isMarried,
    String? maritalPropertyNotes,
    DateTime? lastUpdated,
  }) {
    return EstateProfile(
      ownerName:          ownerName ?? this.ownerName,
      ownerEmail:         ownerEmail ?? this.ownerEmail,
      jurisdiction:       jurisdiction ?? this.jurisdiction,
      maritalStatus:      maritalStatus ?? this.maritalStatus,
      executorName:       executorName ?? this.executorName,
      executorEmail:      executorEmail ?? this.executorEmail,
      executorPhone:      executorPhone ?? this.executorPhone,
      attorneyName:       attorneyName ?? this.attorneyName,
      attorneyEmail:      attorneyEmail ?? this.attorneyEmail,
      attorneyFirm:       attorneyFirm ?? this.attorneyFirm,
      attorneyPhone:      attorneyPhone ?? this.attorneyPhone,
      willOrTrustStatus:  willOrTrustStatus ?? this.willOrTrustStatus,
      beneficiaries:      beneficiaries ?? this.beneficiaries,
      isMarried:          isMarried ?? this.isMarried,
      maritalPropertyNotes: maritalPropertyNotes ?? this.maritalPropertyNotes,
      lastUpdated:        lastUpdated ?? this.lastUpdated,
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// CoinEstateData — stored at users/{uid}/estate_data/{coinId}
// ─────────────────────────────────────────────────────────────────────────────
class CoinEstateData {
  final String coinId;
  final String? beneficiaryId;
  final String? beneficiaryName;    // denormalized for PDF
  final double? fmvOverride;
  final String? appraiserName;
  final double? formalAppraisalValue;
  final DateTime? appraisalDate;
  final String? appraisalCertNumber;
  final String? estateNotes;
  final bool isHeirloom;
  final bool excludeFromReport;

  const CoinEstateData({
    required this.coinId,
    this.beneficiaryId,
    this.beneficiaryName,
    this.fmvOverride,
    this.appraiserName,
    this.formalAppraisalValue,
    this.appraisalDate,
    this.appraisalCertNumber,
    this.estateNotes,
    this.isHeirloom = false,
    this.excludeFromReport = false,
  });

  factory CoinEstateData.fromFirestore(DocumentSnapshot doc) {
    final m = doc.data() as Map<String, dynamic>? ?? {};
    return CoinEstateData(
      coinId:               doc.id,
      beneficiaryId:        m['beneficiaryId']?.toString(),
      beneficiaryName:      m['beneficiaryName']?.toString(),
      fmvOverride:          (m['fmvOverride'] as num?)?.toDouble(),
      appraiserName:        m['appraiserName']?.toString(),
      formalAppraisalValue: (m['formalAppraisalValue'] as num?)?.toDouble(),
      appraisalDate: m['appraisalDate'] is Timestamp
          ? (m['appraisalDate'] as Timestamp).toDate()
          : null,
      appraisalCertNumber: m['appraisalCertNumber']?.toString(),
      estateNotes:         m['estateNotes']?.toString(),
      isHeirloom:          m['isHeirloom'] == true,
      excludeFromReport:   m['excludeFromReport'] == true,
    );
  }

  Map<String, dynamic> toFirestore() => {
    'coinId':               coinId,
    'beneficiaryId':        beneficiaryId,
    'beneficiaryName':      beneficiaryName,
    'fmvOverride':          fmvOverride,
    'appraiserName':        appraiserName,
    'formalAppraisalValue': formalAppraisalValue,
    'appraisalDate':        appraisalDate != null
        ? Timestamp.fromDate(appraisalDate!)
        : null,
    'appraisalCertNumber':  appraisalCertNumber,
    'estateNotes':          estateNotes,
    'isHeirloom':           isHeirloom,
    'excludeFromReport':    excludeFromReport,
  };

  CoinEstateData copyWith({
    String? coinId,
    Object? beneficiaryId = _sentinel,
    Object? beneficiaryName = _sentinel,
    Object? fmvOverride = _sentinel,
    Object? appraiserName = _sentinel,
    Object? formalAppraisalValue = _sentinel,
    Object? appraisalDate = _sentinel,
    Object? appraisalCertNumber = _sentinel,
    Object? estateNotes = _sentinel,
    bool? isHeirloom,
    bool? excludeFromReport,
  }) {
    return CoinEstateData(
      coinId:               coinId ?? this.coinId,
      beneficiaryId:        beneficiaryId == _sentinel ? this.beneficiaryId : beneficiaryId as String?,
      beneficiaryName:      beneficiaryName == _sentinel ? this.beneficiaryName : beneficiaryName as String?,
      fmvOverride:          fmvOverride == _sentinel ? this.fmvOverride : fmvOverride as double?,
      appraiserName:        appraiserName == _sentinel ? this.appraiserName : appraiserName as String?,
      formalAppraisalValue: formalAppraisalValue == _sentinel ? this.formalAppraisalValue : formalAppraisalValue as double?,
      appraisalDate:        appraisalDate == _sentinel ? this.appraisalDate : appraisalDate as DateTime?,
      appraisalCertNumber:  appraisalCertNumber == _sentinel ? this.appraisalCertNumber : appraisalCertNumber as String?,
      estateNotes:          estateNotes == _sentinel ? this.estateNotes : estateNotes as String?,
      isHeirloom:           isHeirloom ?? this.isHeirloom,
      excludeFromReport:    excludeFromReport ?? this.excludeFromReport,
    );
  }
}

// Sentinel for optional nullable copyWith params
const Object _sentinel = Object();

// ─────────────────────────────────────────────────────────────────────────────
// EstateReportRecord — stored at users/{uid}/estate_reports/{reportId}
// ─────────────────────────────────────────────────────────────────────────────
class EstateReportRecord {
  final String reportId;
  final String mode;          // 'living_inventory' | 'estate_settlement'
  final String state;
  final DateTime generatedAt;
  final int totalCoins;
  final double totalFmv;
  final String? downloadUrl;
  final String? portalToken;
  final String? portalUrl;
  final DateTime? linkExpiresAt;

  const EstateReportRecord({
    required this.reportId,
    required this.mode,
    required this.state,
    required this.generatedAt,
    required this.totalCoins,
    required this.totalFmv,
    this.downloadUrl,
    this.portalToken,
    this.portalUrl,
    this.linkExpiresAt,
  });

  String get modeLabel => mode == 'living_inventory'
      ? 'Living Inventory'
      : 'Estate Settlement';

  factory EstateReportRecord.fromFirestore(DocumentSnapshot doc) {
    final m = doc.data() as Map<String, dynamic>? ?? {};
    return EstateReportRecord(
      reportId:   doc.id,
      mode:       m['mode']?.toString() ?? 'living_inventory',
      state:      m['state']?.toString() ?? '',
      generatedAt: m['generatedAt'] is Timestamp
          ? (m['generatedAt'] as Timestamp).toDate()
          : DateTime.now(),
      totalCoins: (m['totalCoins'] as num?)?.toInt() ?? 0,
      totalFmv:   (m['totalFmv'] as num?)?.toDouble() ?? 0.0,
      downloadUrl:   m['downloadUrl']?.toString(),
      portalToken:   m['portalToken']?.toString(),
      portalUrl:     m['portalUrl']?.toString(),
      linkExpiresAt: m['linkExpiresAt'] is Timestamp
          ? (m['linkExpiresAt'] as Timestamp).toDate()
          : null,
    );
  }

  Map<String, dynamic> toFirestore() => {
    'mode':       mode,
    'state':      state,
    'generatedAt': FieldValue.serverTimestamp(),
    'totalCoins': totalCoins,
    'totalFmv':   totalFmv,
    'downloadUrl':   downloadUrl,
    'portalToken':   portalToken,
    'portalUrl':     portalUrl,
    'linkExpiresAt': linkExpiresAt != null
        ? Timestamp.fromDate(linkExpiresAt!)
        : null,
  };
}
