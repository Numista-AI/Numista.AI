import 'package:cloud_firestore/cloud_firestore.dart';

class CoinModel {
  final String id;
  final String year;
  final String mintMark;
  final String denomination;
  final String programSeries;
  final String themeSubject;
  final String variety;
  final String condition;
  final String strikeType;
  final String holderType;
  final String gradingService;
  final String certificationNumber;
  final String metalContent;
  final String quantity;
  final String purchaseCost;
  final String purchaseDate;
  final String retailer;
  final String retailerItemNo;
  final String retailerInvoiceNo;
  final String storageLocation;
  final String personalNotes;
  final String personalRef;
  final String originalDescription;
  final String country;
  
  // Set details
  final bool isSet;
  final String? setId;
  final List<dynamic>? setContents;
  // Nested set membership (for individual coins that belong to a parent set)
  final String? parentSetId;       // doc ID of the parent SET record
  final String? memberOf;          // sub-group label, e.g. "Philadelphia Mint"
  final bool inOriginalPackaging;  // true = coins kept in original US Mint packaging
  
  // Internal tracking
  final String aiEstimatedValue;
  final String meltValue;
  final String imageUrlObverse;
  final String imageUrlReverse;
  final DateTime? timestamp;

  // Greysheet Integration
  final String greysheetGsid;
  final double greysheetBid;
  final double greysheetAsk;
  final double cpgRetail;
  final double pcgsValue;
  final double ngcValue;
  final double blueBookValue;
  final DateTime? priceLastUpdated;
  final bool hasCac;

  // Image QC / Verification status
  final String imageVerificationStatus; // 'unverified', 'grok_verified', 'human_verified', 'flagged'
  final String imageVerificationReason;

  // Scan origin (Binder Scan coins only)
  final String source;        // e.g. 'Binder Scan', 'Manual Entry'
  final String sourceFile;    // scan_uuid — raw scan identifier
  final String binderDocId;   // Firestore binder_scans doc ID

  // Paper Trail (Bulk Import / PDF Invoice)
  final String receiptId;       // links to receipts/{user}/{receiptId} Firestore doc
  final String receiptGcsPath;  // GCS path of original invoice PDF
  final String importSessionId; // import session that created this coin record
  final String importBatch;     // import_batch tag (e.g. 'lincoln_missing_2026-06-20')

  // Lateral Transfer & Passport Ledger fields
  final List<dynamic> provenanceLedger;
  final String transferStatus; // 'none', 'pending', 'transferred', 'claimed'
  final String transferId;

  CoinModel({
    required this.id,
    this.year = '',
    this.mintMark = '',
    this.denomination = '',
    this.programSeries = '',
    this.themeSubject = '',
    this.variety = '',
    this.condition = 'Ungraded',
    this.strikeType = '',
    this.holderType = '',
    this.gradingService = '',
    this.certificationNumber = '',
    this.metalContent = '',
    this.quantity = '1',
    this.purchaseCost = '\$0.00',
    this.purchaseDate = '',
    this.retailer = '',
    this.retailerItemNo = '',
    this.retailerInvoiceNo = '',
    this.storageLocation = '',
    this.personalNotes = '',
    this.personalRef = '',
    this.originalDescription = '',
    this.aiEstimatedValue = 'Pending',
    this.meltValue = 'N/A',
    this.imageUrlObverse = '',
    this.imageUrlReverse = '',
    this.country = 'USA',
    this.timestamp,
    this.isSet = false,
    this.setId,
    this.setContents,
    this.parentSetId,
    this.memberOf,
    this.inOriginalPackaging = false,
    this.source = '',
    this.sourceFile = '',
    this.binderDocId = '',
    this.receiptId = '',
    this.receiptGcsPath = '',
    this.importSessionId = '',
    this.importBatch = '',
    this.imageVerificationStatus = 'unverified',
    this.imageVerificationReason = '',
    this.greysheetGsid = '',
    this.greysheetBid = 0.0,
    this.greysheetAsk = 0.0,
    this.cpgRetail = 0.0,
    this.pcgsValue = 0.0,
    this.ngcValue = 0.0,
    this.blueBookValue = 0.0,
    this.priceLastUpdated,
    this.hasCac = false,
    this.provenanceLedger = const [],
    this.transferStatus = 'none',
    this.transferId = '',
  });

  factory CoinModel.fromFirestore(DocumentSnapshot doc) {
    return CoinModel.fromMap(doc.data() as Map<String, dynamic>, doc.id);
  }

  /// Splits a combined Year+MintMark string.
  /// e.g. "2006D" → (year: '2006', mint: 'D')
  /// e.g. "1776-1976S" → (year: '1776-1976', mint: 'S')
  /// Returns original values unchanged if already separated or no suffix.
  static (String year, String mint) _splitYearMint(String rawYear, String rawMint) {
    if (rawMint.isNotEmpty) return (rawYear, rawMint); // already split
    final trimmed = rawYear.trim();
    // Matches 4-digit year (with optional bicentennial suffix) + single uppercase letter
    final re = RegExp(r'^(\d{4}(?:-\d{4})?)\s*([A-WY-Z])$', caseSensitive: false);
    final m = re.firstMatch(trimmed);
    if (m != null) return (m.group(1)!, m.group(2)!.toUpperCase());
    return (trimmed, rawMint);
  }

  factory CoinModel.fromMap(Map<String, dynamic> data, String id) {
    // Split combined Year+Mint before assigning (e.g. "2006D" → year='2006' mint='D')
    final (year, mintMark) = _splitYearMint(
      data['Year']?.toString().trim() ?? data['year']?.toString().trim() ?? '',
      data['Mint Mark']?.toString().trim() ?? data['mintMark']?.toString().trim() ?? data['MintMark']?.toString().trim() ?? '',
    );
    return CoinModel(
      id: id,
      year: year,
      mintMark: mintMark,
      denomination: data['Denomination']?.toString() ?? data['denomination']?.toString() ?? '',
      programSeries: data['Program/Series']?.toString() ?? data['programSeries']?.toString() ?? data['ProgramSeries']?.toString() ?? '',
      themeSubject: data['Theme/Subject']?.toString() ?? data['themeSubject']?.toString() ?? '',
      variety: data['Variety']?.toString() ?? data['variety']?.toString() ?? '',
      condition: data['Condition']?.toString() ?? data['condition']?.toString() ?? 'Ungraded',
      strikeType: data['Strike Type']?.toString() ?? data['strikeType']?.toString() ?? '',
      holderType: data['Holder Type']?.toString() ?? data['holderType']?.toString() ?? '',
      gradingService: data['Grading Service']?.toString() ?? data['gradingService']?.toString() ?? '',
      certificationNumber: data['Certification Number']?.toString() ?? data['certificationNumber']?.toString() ?? '',
      metalContent: data['Metal Content']?.toString() ?? data['metalContent']?.toString() ?? '',
      quantity: data['Quantity']?.toString() ?? data['quantity']?.toString() ?? '1',
      purchaseCost: data['Purchase Cost']?.toString() ?? data['purchaseCost']?.toString() ?? '\$0.00',
      purchaseDate: data['Purchase Date']?.toString() ?? data['purchaseDate']?.toString() ?? '',
      retailer: data['Retailer/Website']?.toString() ?? data['retailer']?.toString() ?? '',
      retailerItemNo: data['Retailer Item No.']?.toString() ?? data['retailerItemNo']?.toString() ?? '',
      retailerInvoiceNo: data['Retailer Invoice #']?.toString() ?? data['retailerInvoiceNo']?.toString() ?? '',
      storageLocation: data['Storage Location']?.toString() ?? data['storageLocation']?.toString() ?? '',
      personalNotes: data['Personal Notes I']?.toString() ?? data['personalNotes']?.toString() ?? '',
      personalRef: data['Personal Reference #']?.toString() ?? data['personalRef']?.toString() ?? '',
      originalDescription: data['Original Description from source']?.toString() ?? data['originalDescription']?.toString() ?? '',
      aiEstimatedValue: data['AI Estimated Value']?.toString() ?? data['aiEstimatedValue']?.toString() ?? 'Pending',
      meltValue: data['Melt Value']?.toString() ?? data['meltValue']?.toString() ?? 'N/A',
      imageUrlObverse: data['image_url_obverse']?.toString() ?? '',
      imageUrlReverse: data['image_url_reverse']?.toString() ?? '',
      country: data['Country']?.toString() ?? 'USA',
      timestamp: data['timestamp'] is Timestamp ? (data['timestamp'] as Timestamp).toDate() : null,
      source: data['source']?.toString() ?? '',
      sourceFile: data['source_file']?.toString() ?? data['scan_uuid']?.toString() ?? '',
      binderDocId: data['binder_doc_id']?.toString() ?? '',
      receiptId: data['receipt_id']?.toString() ?? '',
      receiptGcsPath: (data['paper_trail'] as Map<String, dynamic>?)?['gcs_path']?.toString() ?? '',
      importSessionId: data['import_session_id']?.toString() ?? '',
      importBatch: data['import_batch']?.toString() ?? '',
      imageVerificationStatus: data['image_verification_status']?.toString() ?? 'unverified',
      imageVerificationReason: data['image_verification_reason']?.toString() ?? '',
      greysheetGsid: data['greysheetGsid']?.toString() ?? data['greysheet_gsid']?.toString() ?? '',
      greysheetBid: (data['greysheet_bid'] as num?)?.toDouble() ?? (data['greysheetBid'] as num?)?.toDouble() ?? 0.0,
      greysheetAsk: (data['greysheet_ask'] as num?)?.toDouble() ?? (data['greysheetAsk'] as num?)?.toDouble() ?? 0.0,
      cpgRetail: (data['cpg_retail'] as num?)?.toDouble() ?? (data['cpgRetail'] as num?)?.toDouble() ?? 0.0,
      pcgsValue: (data['pcgs_value'] as num?)?.toDouble() ?? (data['pcgsVal'] as num?)?.toDouble() ?? 0.0,
      ngcValue: (data['ngc_value'] as num?)?.toDouble() ?? (data['ngcVal'] as num?)?.toDouble() ?? 0.0,
      blueBookValue: (data['blue_book_value'] as num?)?.toDouble() ?? (data['blueBookVal'] as num?)?.toDouble() ?? 0.0,
      priceLastUpdated: data['priceLastUpdated'] is Timestamp 
          ? (data['priceLastUpdated'] as Timestamp).toDate() 
          : null,
      hasCac: (data['cac_premium_flag'] as bool?) ?? (data['hasCac'] as bool?) ?? false,
      isSet: data['is_set'] as bool? ?? false,
      setId: data['set_id']?.toString(),
      setContents: data['set_contents'] as List<dynamic>?,
      parentSetId: data['parent_set_id']?.toString(),
      memberOf: data['member_of']?.toString(),
      inOriginalPackaging: data['in_original_packaging'] as bool? ?? false,
      provenanceLedger: data['provenanceLedger'] as List<dynamic>? ?? [],
      transferStatus: data['transferStatus']?.toString() ?? data['transfer_status']?.toString() ?? 'none',
      transferId: data['transferId']?.toString() ?? data['transfer_id']?.toString() ?? '',
    );
  }

  Map<String, dynamic> toFirestore() {
    return {
      'Year': year,
      'Mint Mark': mintMark,
      'Denomination': denomination,
      'Program/Series': programSeries,
      'Theme/Subject': themeSubject,
      'Variety': variety,
      'Condition': condition,
      'Strike Type': strikeType,
      'Holder Type': holderType,
      'Grading Service': gradingService,
      'Certification Number': certificationNumber,
      'Metal Content': metalContent,
      'Quantity': quantity,
      'Purchase Cost': purchaseCost,
      'Purchase Date': purchaseDate,
      'Retailer/Website': retailer,
      'Retailer Item No.': retailerItemNo,
      'Retailer Invoice #': retailerInvoiceNo,
      'Storage Location': storageLocation,
      'Personal Notes I': personalNotes,
      'Personal Reference #': personalRef,
      'Original Description from source': originalDescription,
      'AI Estimated Value': aiEstimatedValue,
      'Melt Value': meltValue,
      'image_url_obverse': imageUrlObverse,
      'image_url_reverse': imageUrlReverse,
      'image_verification_status': imageVerificationStatus,
      'image_verification_reason': imageVerificationReason,
      'greysheetGsid': greysheetGsid,
      'greysheetBid': greysheetBid,
      'greysheetAsk': greysheetAsk,
      'cpgRetail': cpgRetail,
      'priceLastUpdated': priceLastUpdated != null ? Timestamp.fromDate(priceLastUpdated!) : null,
      'hasCac': hasCac,
      'is_set': isSet,
      'set_id': setId,
      'set_contents': setContents,
      'parent_set_id': parentSetId,
      'member_of': memberOf,
      'in_original_packaging': inOriginalPackaging,
      'provenanceLedger': provenanceLedger,
      'transferStatus': transferStatus,
      'transferId': transferId,
      'Country': country,
      'timestamp': timestamp ?? FieldValue.serverTimestamp(),
    };
  }

  /// Returns the direct official verification URL for slabbed coins,
  /// or null if uncertified, raw, or missing cert number.
  /// Supports PCGS, NGC, ANACS, CAC (Sticker), and CACG (Slab).
  String? getVerificationUrl() {
    final cert = certificationNumber.replaceAll(RegExp(r'\D'), '').trim();
    if (cert.isEmpty) return null;

    final svc = (gradingService.isNotEmpty ? gradingService : holderType).trim().toUpperCase();
    final holder = holderType.trim().toUpperCase();

    if (svc.contains('PCGS')) {
      return 'https://www.pcgs.com/cert/$cert';
    } else if (svc.contains('NGC')) {
      return 'https://www.ngccoin.com/certlookup/$cert/';
    } else if (svc.contains('ANACS')) {
      return 'https://www.anacs.com/Verify/CertVerification.aspx?Cert=$cert';
    } else if (svc.contains('CACG') || holder.contains('CACG')) {
      return 'https://www.cacgrading.com/cert-verify/$cert';
    } else if (svc.contains('CAC') || holder.contains('CAC') || hasCac) {
      return 'https://www.caccoin.com/cert-lookup/';
    }
    return null;
  }
}

