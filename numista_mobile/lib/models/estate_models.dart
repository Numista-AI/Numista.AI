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
  final String alias;        // Replaces name (e.g. "Primary Heir", "Daughter")
  final String relationship; // 'Spouse', 'Child', 'Sibling', 'Friend', 'Charity', 'Other'
  final String njClass;      // 'A', 'C', 'D', 'E' — NJ inheritance tax class
  final String notes;

  const EstateBeneficiary({
    required this.id,
    required this.alias,
    this.relationship = 'Other',
    this.njClass = 'D',
    this.notes = '',
  });

  factory EstateBeneficiary.fromMap(Map<String, dynamic> m) {
    return EstateBeneficiary(
      id:           m['id']?.toString() ?? '',
      alias:        m['alias']?.toString() ?? m['name']?.toString() ?? '',
      relationship: m['relationship']?.toString() ?? 'Other',
      njClass:      m['njClass']?.toString() ?? 'D',
      notes:        m['notes']?.toString() ?? '',
    );
  }

  Map<String, dynamic> toMap() => {
    'id':           id,
    'alias':        alias,
    'relationship': relationship,
    'njClass':      njClass,
    'notes':        notes,
  };

  EstateBeneficiary copyWith({
    String? id,
    String? alias,
    String? relationship,
    String? njClass,
    String? notes,
  }) {
    return EstateBeneficiary(
      id:           id ?? this.id,
      alias:        alias ?? this.alias,
      relationship: relationship ?? this.relationship,
      njClass:      njClass ?? this.njClass,
      notes:        notes ?? this.notes,
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// EstateProfile — stored at users/{uid}/estate_profile/data (single document)
// ─────────────────────────────────────────────────────────────────────────────
class EstateProfile {
  // PII fields ownerName, ownerEmail, executor*, attorney* removed
  final String jurisdiction;          // state code: 'NY', 'NC', etc.
  final String maritalStatus;         // 'Single', 'Married', 'Widowed', 'Divorced'
  final String willOrTrustStatus;     // 'Has Will', 'Has Trust', 'Has Both', 'Neither', 'Unknown'
  final List<EstateBeneficiary> beneficiaries;
  final bool isMarried;
  final String maritalPropertyNotes;
  final DateTime? lastUpdated;
  final int heirsCount;
  final String liquidationPreference; // 'consign_all' | 'maximize_value' | 'keep_family'
  final String preferredConsignor;    // 'GreatCollections' | 'Heritage' | 'StacksBowers' | 'None'

  const EstateProfile({
    this.jurisdiction = '',
    this.maritalStatus = 'Single',
    this.willOrTrustStatus = 'Unknown',
    this.beneficiaries = const [],
    this.isMarried = false,
    this.maritalPropertyNotes = '',
    this.lastUpdated,
    this.heirsCount = 1,
    this.liquidationPreference = 'consign_all',
    this.preferredConsignor = 'None',
  });

  bool get isCommunityPropertyState => _communityPropertyStates.contains(jurisdiction);

  factory EstateProfile.fromFirestore(DocumentSnapshot doc) {
    final m = doc.data() as Map<String, dynamic>? ?? {};
    return EstateProfile(
      jurisdiction:       m['jurisdiction']?.toString() ?? '',
      maritalStatus:      m['maritalStatus']?.toString() ?? 'Single',
      willOrTrustStatus:  m['willOrTrustStatus']?.toString() ?? 'Unknown',
      beneficiaries: (m['beneficiaries'] as List<dynamic>? ?? [])
          .map((e) => EstateBeneficiary.fromMap(e as Map<String, dynamic>))
          .toList(),
      isMarried:            m['isMarried'] == true,
      maritalPropertyNotes: m['maritalPropertyNotes']?.toString() ?? '',
      lastUpdated: m['lastUpdated'] is Timestamp
          ? (m['lastUpdated'] as Timestamp).toDate()
          : null,
      heirsCount:         (m['heirsCount'] as num?)?.toInt() ?? 1,
      liquidationPreference: m['liquidationPreference']?.toString() ?? 'consign_all',
      preferredConsignor: m['preferredConsignor']?.toString() ?? 'None',
    );
  }

  Map<String, dynamic> toFirestore() => {
    'jurisdiction':       jurisdiction,
    'maritalStatus':      maritalStatus,
    'willOrTrustStatus':  willOrTrustStatus,
    'beneficiaries':      beneficiaries.map((b) => b.toMap()).toList(),
    'isMarried':          isMarried,
    'maritalPropertyNotes': maritalPropertyNotes,
    'lastUpdated':        FieldValue.serverTimestamp(),
    'heirsCount':         heirsCount,
    'liquidationPreference': liquidationPreference,
    'preferredConsignor': preferredConsignor,
  };

  EstateProfile copyWith({
    String? jurisdiction,
    String? maritalStatus,
    String? willOrTrustStatus,
    List<EstateBeneficiary>? beneficiaries,
    bool? isMarried,
    String? maritalPropertyNotes,
    DateTime? lastUpdated,
    int? heirsCount,
    String? liquidationPreference,
    String? preferredConsignor,
  }) {
    return EstateProfile(
      jurisdiction:       jurisdiction ?? this.jurisdiction,
      maritalStatus:      maritalStatus ?? this.maritalStatus,
      willOrTrustStatus:  willOrTrustStatus ?? this.willOrTrustStatus,
      beneficiaries:      beneficiaries ?? this.beneficiaries,
      isMarried:          isMarried ?? this.isMarried,
      maritalPropertyNotes: maritalPropertyNotes ?? this.maritalPropertyNotes,
      lastUpdated:        lastUpdated ?? this.lastUpdated,
      heirsCount:          heirsCount ?? this.heirsCount,
      liquidationPreference: liquidationPreference ?? this.liquidationPreference,
      preferredConsignor:  preferredConsignor ?? this.preferredConsignor,
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// EphemeralReportIdentity — RAM only, never written to persistent store
// ─────────────────────────────────────────────────────────────────────────────
class EphemeralReportIdentity {
  final String ownerLegalName;
  final String executorName;
  final String attorneyName;
  final String attorneyFirm;
  final String attorneyEmail;
  final Map<String, String> aliasToLegalName; // "Primary Heir" -> "Jane Smith"
  final String reportDate;
  final String? dateOfDeath;
  final bool includeContactsInPdf;

  const EphemeralReportIdentity({
    required this.ownerLegalName,
    this.executorName = '',
    this.attorneyName = '',
    this.attorneyFirm = '',
    this.attorneyEmail = '',
    this.aliasToLegalName = const {},
    required this.reportDate,
    this.dateOfDeath,
    this.includeContactsInPdf = true,
  });

  Map<String, dynamic> toJson() => {
    'owner_name': ownerLegalName, // maps to expected backend field 'owner_name'
    'executor_name': executorName,
    'attorney_name': attorneyName,
    'attorney_firm': attorneyFirm,
    'attorney_email': attorneyEmail,
    'beneficiaries': aliasToLegalName.entries.map((e) => {
      'alias': e.key,
      'name': e.value,
    }).toList(), // maps aliases to legal names for backend pdf generation
    'report_date': reportDate,
    'date_of_death': dateOfDeath,
    'include_contacts_in_pdf': includeContactsInPdf,
  };
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
  final String? assignedHeirId;
  final bool divisionLocked;

  final String? custodialLocation;
  final String? subHandReceiptHolder;
  final DateTime? handReceiptSignedAt;
  final String? handReceiptHash;
  final String? trustScheduleIdentifier;

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
    this.assignedHeirId,
    this.divisionLocked = false,
    this.custodialLocation,
    this.subHandReceiptHolder,
    this.handReceiptSignedAt,
    this.handReceiptHash,
    this.trustScheduleIdentifier,
  });

  factory CoinEstateData.fromFirestore(DocumentSnapshot doc) {
    final m = doc.data() as Map<String, dynamic>? ?? {};
    return CoinEstateData(
      coinId:               doc.id,
      beneficiaryId:        m['beneficiaryId']?.toString() ?? m['beneficiary_id']?.toString(),
      beneficiaryName:      m['beneficiaryName']?.toString() ?? m['beneficiary_name']?.toString(),
      fmvOverride:          (m['fmvOverride'] ?? m['fmv_override'] as num?)?.toDouble(),
      appraiserName:        m['appraiserName']?.toString() ?? m['appraiser_name']?.toString(),
      formalAppraisalValue: (m['formalAppraisalValue'] ?? m['formal_appraisal_value'] as num?)?.toDouble(),
      appraisalDate: m['appraisalDate'] is Timestamp
          ? (m['appraisalDate'] as Timestamp).toDate()
          : m['appraisal_date'] is Timestamp
              ? (m['appraisal_date'] as Timestamp).toDate()
              : null,
      appraisalCertNumber: m['appraisalCertNumber']?.toString() ?? m['appraisal_cert_number']?.toString(),
      estateNotes:         m['estateNotes']?.toString() ?? m['estate_notes']?.toString(),
      isHeirloom:          m['isHeirloom'] == true || m['is_heirloom'] == true,
      excludeFromReport:   m['excludeFromReport'] == true || m['exclude_from_report'] == true,
      assignedHeirId:       m['assignedHeirId']?.toString() ?? m['assigned_heir_id']?.toString(),
      divisionLocked:       m['divisionLocked'] == true || m['division_locked'] == true,
      custodialLocation:    m['custodialLocation']?.toString() ?? m['custodial_location']?.toString(),
      subHandReceiptHolder: m['subHandReceiptHolder']?.toString() ?? m['sub_hand_receipt_holder']?.toString(),
      handReceiptSignedAt: m['handReceiptSignedAt'] is Timestamp
          ? (m['handReceiptSignedAt'] as Timestamp).toDate()
          : null,
      handReceiptHash:      m['handReceiptHash']?.toString() ?? m['hand_receipt_hash']?.toString(),
      trustScheduleIdentifier: m['trustScheduleIdentifier']?.toString() ?? m['trust_schedule_identifier']?.toString(),
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
    'assignedHeirId':       assignedHeirId,
    'divisionLocked':       divisionLocked,
    'custodialLocation':    custodialLocation,
    'subHandReceiptHolder': subHandReceiptHolder,
    'handReceiptSignedAt':  handReceiptSignedAt != null
        ? Timestamp.fromDate(handReceiptSignedAt!)
        : null,
    'handReceiptHash':      handReceiptHash,
    'trustScheduleIdentifier': trustScheduleIdentifier,
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
    Object? assignedHeirId = _sentinel,
    bool? divisionLocked,
    Object? custodialLocation = _sentinel,
    Object? subHandReceiptHolder = _sentinel,
    Object? handReceiptSignedAt = _sentinel,
    Object? handReceiptHash = _sentinel,
    Object? trustScheduleIdentifier = _sentinel,
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
      assignedHeirId:       assignedHeirId == _sentinel ? this.assignedHeirId : assignedHeirId as String?,
      divisionLocked:       divisionLocked ?? this.divisionLocked,
      custodialLocation:    custodialLocation == _sentinel ? this.custodialLocation : custodialLocation as String?,
      subHandReceiptHolder: subHandReceiptHolder == _sentinel ? this.subHandReceiptHolder : subHandReceiptHolder as String?,
      handReceiptSignedAt:  handReceiptSignedAt == _sentinel ? this.handReceiptSignedAt : handReceiptSignedAt as DateTime?,
      handReceiptHash:      handReceiptHash == _sentinel ? this.handReceiptHash : handReceiptHash as String?,
      trustScheduleIdentifier: trustScheduleIdentifier == _sentinel ? this.trustScheduleIdentifier : trustScheduleIdentifier as String?,
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
          : m['generated_at'] is String
              ? DateTime.tryParse(m['generated_at'].toString()) ?? DateTime.now()
              : m['generated_at_ts'] is Timestamp
                  ? (m['generated_at_ts'] as Timestamp).toDate()
                  : DateTime.now(),
      totalCoins: (m['totalCoins'] ?? m['total_coins'] as num?)?.toInt() ?? 0,
      totalFmv:   (m['totalFmv'] ?? m['total_fmv'] as num?)?.toDouble() ?? 0.0,
      downloadUrl:   m['downloadUrl']?.toString() ?? m['download_url']?.toString(),
      portalToken:   m['portalToken']?.toString() ?? m['portal_token']?.toString(),
      portalUrl:     m['portalUrl']?.toString() ?? m['portal_url']?.toString(),
      linkExpiresAt: m['linkExpiresAt'] is Timestamp
          ? (m['linkExpiresAt'] as Timestamp).toDate()
          : m['link_expires_at'] is Timestamp
              ? (m['link_expires_at'] as Timestamp).toDate()
              : null,
    );
  }

  Map<String, dynamic> toFirestore() => {
    'mode':       mode,
    'state':      state,
    'generated_at_ts': FieldValue.serverTimestamp(),
    'generated_at': '${DateTime.now().toUtc().toIso8601String()}Z',
    'total_coins': totalCoins,
    'total_fmv':   totalFmv,
    'download_url':   downloadUrl,
    'portal_token':   portalToken,
    'portal_url':     portalUrl,
    'link_expires_at': linkExpiresAt != null
        ? Timestamp.fromDate(linkExpiresAt!)
        : null,
  };
}

// ─────────────────────────────────────────────────────────────────────────────
// EstateAuditRecord — stored at users/{uid}/estate_audits/{auditId}
// Inspired by GCSS-Army Sensitive Item & Cyclic Spot-Check Audits
// ─────────────────────────────────────────────────────────────────────────────
class EstateAuditRecord {
  final String auditId;
  final String coinId;
  final String auditType;            // 'routine_spot_check' | 'high_value_verification' | 'annual_100_percent'
  final DateTime verifiedAt;
  final String verifiedByAlias;
  final String physicalConditionCode; // 'Choice', 'Impaired', 'Damaged'
  final bool certVerified;
  final String auditHash;            // SHA-256 tamper-evident hash

  const EstateAuditRecord({
    required this.auditId,
    required this.coinId,
    this.auditType = 'routine_spot_check',
    required this.verifiedAt,
    this.verifiedByAlias = 'Owner',
    this.physicalConditionCode = 'Choice',
    this.certVerified = true,
    this.auditHash = '',
  });

  factory EstateAuditRecord.fromFirestore(DocumentSnapshot doc) {
    final m = doc.data() as Map<String, dynamic>? ?? {};
    return EstateAuditRecord(
      auditId:               doc.id,
      coinId:                m['coinId']?.toString() ?? '',
      auditType:             m['auditType']?.toString() ?? 'routine_spot_check',
      verifiedAt: m['verifiedAt'] is Timestamp
          ? (m['verifiedAt'] as Timestamp).toDate()
          : DateTime.now(),
      verifiedByAlias:       m['verifiedByAlias']?.toString() ?? 'Owner',
      physicalConditionCode: m['physicalConditionCode']?.toString() ?? 'Choice',
      certVerified:          m['certVerified'] == true,
      auditHash:             m['auditHash']?.toString() ?? '',
    );
  }

  Map<String, dynamic> toFirestore() => {
    'coinId':                coinId,
    'auditType':             auditType,
    'verifiedAt':            Timestamp.fromDate(verifiedAt),
    'verifiedByAlias':       verifiedByAlias,
    'physicalConditionCode': physicalConditionCode,
    'certVerified':          certVerified,
    'auditHash':             auditHash,
  };
}

// ─────────────────────────────────────────────────────────────────────────────
// EstateDocumentRegisterRecord — stored at users/{uid}/document_register/{docNumber}
// Inspired by DA Form 3161 / GCSS-Army Sequential Document Registers
// Format: NUM-DOC-YYYY-XXXXX
// ─────────────────────────────────────────────────────────────────────────────
class EstateDocumentRegisterRecord {
  final String docNumber;             // e.g. "NUM-DOC-2026-00001"
  final String docType;               // 'baseline_lock' | 'custody_transfer' | 'appraisal_entry' | 'stepped_up_basis' | 'bequest_transfer'
  final DateTime createdAt;
  final int assetCount;
  final double totalFmv;
  final String signatureHash;
  final String? pdfStoragePath;
  final String title;

  const EstateDocumentRegisterRecord({
    required this.docNumber,
    required this.docType,
    required this.createdAt,
    required this.assetCount,
    required this.totalFmv,
    this.signatureHash = '',
    this.pdfStoragePath,
    required this.title,
  });

  String get typeLabel {
    switch (docType) {
      case 'baseline_lock':
        return 'Initial Estate Baseline Lock';
      case 'custody_transfer':
        return 'Custody Transfer & Loan Agreement';
      case 'appraisal_entry':
        return 'Formal Appraisal Register Entry';
      case 'stepped_up_basis':
        return 'Stepped-Up Basis Snapshot (IRC § 1014)';
      case 'bequest_transfer':
        return 'Executor Receipt of Bequest Distribution';
      default:
        return 'Document Register Record';
    }
  }

  factory EstateDocumentRegisterRecord.fromFirestore(DocumentSnapshot doc) {
    final m = doc.data() as Map<String, dynamic>? ?? {};
    return EstateDocumentRegisterRecord(
      docNumber:      doc.id,
      docType:        m['docType']?.toString() ?? 'baseline_lock',
      createdAt: m['createdAt'] is Timestamp
          ? (m['createdAt'] as Timestamp).toDate()
          : DateTime.now(),
      assetCount:     (m['assetCount'] as num?)?.toInt() ?? 0,
      totalFmv:       (m['totalFmv'] as num?)?.toDouble() ?? 0.0,
      signatureHash:  m['signatureHash']?.toString() ?? '',
      pdfStoragePath: m['pdfStoragePath']?.toString(),
      title:          m['title']?.toString() ?? 'Estate Document Record',
    );
  }

  Map<String, dynamic> toFirestore() => {
    'docType':        docType,
    'createdAt':      Timestamp.fromDate(createdAt),
    'assetCount':     assetCount,
    'totalFmv':       totalFmv,
    'signatureHash':  signatureHash,
    'pdfStoragePath': pdfStoragePath,
    'title':          title,
  };
}
