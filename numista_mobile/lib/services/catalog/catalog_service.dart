/// U.S. Numismatics Master Catalog (1776 - 2026) client service, data models,
/// faceted filter engine, guest anti-scraping guards, and personal photo toggle.
///
/// Spec: Plan.v2.1 sections 2.3, 3.1-3.3, 6.1-6.5.
library;

import 'nac_code_parser.dart';

class CatalogSpecifications {
  final String? designerObverse;
  final String? designerReverse;
  final String composition;
  final double? fineness;
  final String preciousMetalType;
  final double? actualMetalWeightOz;
  final double? weightGrams;
  final double? diameterMm;
  final double? heightMm;
  final String? edge;
  final String alignment;

  const CatalogSpecifications({
    this.designerObverse,
    this.designerReverse,
    required this.composition,
    this.fineness,
    this.preciousMetalType = 'NONE',
    this.actualMetalWeightOz,
    this.weightGrams,
    this.diameterMm,
    this.heightMm,
    this.edge,
    required this.alignment,
  });
}

class CatalogCitation {
  final String tier;
  final String sourceName;
  final String citationText;
  final String? documentUrl;
  final String verifiedDate;

  const CatalogCitation({
    required this.tier,
    required this.sourceName,
    required this.citationText,
    this.documentUrl,
    required this.verifiedDate,
  });
}

class CatalogItemModel {
  final String nacCode;
  final List<String> nacAliases;
  final String seoSlug;
  final String kind;
  final String cc;
  final String countryEra;
  final String? stateOrEntity;
  final String denominationClass;
  final String series;
  final int year;
  final String yearDisplay;
  final String facilityCode;
  final bool mintMarkOnCoin;
  final String? mintMark;
  final String? facilityNote;
  final String title;
  final String subtitle;
  final String defaultFace; // 'OBVERSE' | 'REVERSE'
  final String? obverseImageUrl;
  final String? reverseImageUrl;
  final bool hasObverseImage;
  final bool hasReverseImage;
  final String imageTier; // 'MUSEUM' | 'PUBLIC_DOMAIN' | 'VERIFIED_COMMUNITY' | 'NONE'
  final String? imageSourceCredit;
  final String imageLicenseType;
  final int? mintageOfficialMint;
  final int? mintageCommercial;
  final int? mintageProof;
  final bool mintageEstimated;
  final String? mintageReconciliationNote;
  final CatalogSpecifications specifications;
  final List<CatalogCitation> primaryCitations;

  const CatalogItemModel({
    required this.nacCode,
    this.nacAliases = const [],
    required this.seoSlug,
    required this.kind,
    required this.cc,
    required this.countryEra,
    this.stateOrEntity,
    required this.denominationClass,
    required this.series,
    required this.year,
    required this.yearDisplay,
    required this.facilityCode,
    required this.mintMarkOnCoin,
    this.mintMark,
    this.facilityNote,
    required this.title,
    required this.subtitle,
    this.defaultFace = 'OBVERSE',
    this.obverseImageUrl,
    this.reverseImageUrl,
    this.hasObverseImage = false,
    this.hasReverseImage = false,
    this.imageTier = 'NONE',
    this.imageSourceCredit,
    this.imageLicenseType = 'NONE',
    this.mintageOfficialMint,
    this.mintageCommercial,
    this.mintageProof,
    this.mintageEstimated = false,
    this.mintageReconciliationNote,
    required this.specifications,
    required this.primaryCitations,
  });

  String get targetCollection => NacCodeParser.kindToCollection(kind);

  String get deterministicDocId => '${nacCode}_SLOT1';
}

/// Tracks a user's collection entry and their Founder Q3 photo toggle state.
class CollectionEntryState {
  final String nacCode;
  final String collection;
  final String docId;
  final bool usePersonalPhoto;
  final String? customObverseImageUrl;
  final String? customReverseImageUrl;
  final String? stockObverseImageUrl;
  final String? stockReverseImageUrl;

  const CollectionEntryState({
    required this.nacCode,
    required this.collection,
    required this.docId,
    this.usePersonalPhoto = false,
    this.customObverseImageUrl,
    this.customReverseImageUrl,
    this.stockObverseImageUrl,
    this.stockReverseImageUrl,
  });

  String? get activeObverseImageUrl =>
      (usePersonalPhoto && customObverseImageUrl != null)
          ? customObverseImageUrl
          : stockObverseImageUrl;

  String? get activeReverseImageUrl =>
      (usePersonalPhoto && customReverseImageUrl != null)
          ? customReverseImageUrl
          : stockReverseImageUrl;

  CollectionEntryState copyWith({
    bool? usePersonalPhoto,
    String? customObverseImageUrl,
    String? customReverseImageUrl,
  }) {
    return CollectionEntryState(
      nacCode: nacCode,
      collection: collection,
      docId: docId,
      usePersonalPhoto: usePersonalPhoto ?? this.usePersonalPhoto,
      customObverseImageUrl: customObverseImageUrl ?? this.customObverseImageUrl,
      customReverseImageUrl: customReverseImageUrl ?? this.customReverseImageUrl,
      stockObverseImageUrl: stockObverseImageUrl,
      stockReverseImageUrl: stockReverseImageUrl,
    );
  }
}

class UsNumismaticsCatalogService {
  /// Filtering helper matching backend `/api/v1/catalog` parameters.
  static List<CatalogItemModel> filterItems(
    List<CatalogItemModel> items, {
    String? kind,
    String? cc,
    String? era,
    String? facility,
    String? state,
    int? maxYear,
    String? query,
    String? denominationClass,
  }) {
    final q = (query ?? '').trim().toLowerCase();
    return items.where((item) {
      if (kind != null && kind.isNotEmpty && item.kind != kind) {
        return false;
      }
      if (cc != null && cc.isNotEmpty && item.cc != cc) {
        return false;
      }
      if (era != null && era.isNotEmpty && item.countryEra != era) {
        return false;
      }
      if (facility != null &&
          facility.isNotEmpty &&
          item.facilityCode != facility) {
        return false;
      }
      if (state != null && state.isNotEmpty && item.stateOrEntity != state) {
        return false;
      }
      if (denominationClass != null &&
          denominationClass.isNotEmpty &&
          item.denominationClass != denominationClass) {
        return false;
      }
      if (maxYear != null && item.year > maxYear) {
        return false;
      }
      if (q.isNotEmpty) {
        final haystack = [
          item.title,
          item.subtitle,
          item.nacCode,
          item.yearDisplay,
          item.series,
          item.denominationClass,
          item.facilityNote ?? '',
        ].join(' ').toLowerCase();
        if (!haystack.contains(q)) {
          return false;
        }
      }
      return true;
    }).toList();
  }

  /// Founder Q4 policy: Unauthenticated guests cannot download catalog images.
  static bool canDownloadImage({required bool isAuthenticated}) {
    return isAuthenticated;
  }

  /// Canonical 15-item seed catalog covering all 13 verified Plan.v2.1 §2.2 vectors
  /// plus the 1787 Connecticut Copper and 1899 $5 Silver Certificate.
  static const List<CatalogItemModel> seedItems = [
    CatalogItemModel(
      nacCode: 'NAC1.CN.CO.1C.FUGIO.1787.XX.BASE.K',
      nacAliases: ['NAC1.CN.PF.1C.FUGIO.1787.XX.BASE.H'],
      seoSlug: 'coins/fugio-cent/1787-club-rays',
      kind: 'CN',
      cc: 'CO',
      countryEra: 'PRE_FEDERAL',
      stateOrEntity: 'CONTINENTAL',
      denominationClass: '1C',
      series: 'FUGIO',
      year: 1787,
      yearDisplay: '1787 · Pre-Federal',
      facilityCode: 'XX',
      mintMarkOnCoin: false,
      mintMark: null,
      facilityNote: 'New Haven private contract (Abel Buell dies)',
      title: '1787 Fugio Cent — Club Rays',
      subtitle: 'Continental Congress · Sundial / 13 Linked States',
      defaultFace: 'OBVERSE',
      mintageCommercial: 400000,
      mintageEstimated: true,
      specifications: CatalogSpecifications(
        designerObverse: 'Abel Buell',
        designerReverse: 'Abel Buell',
        composition: 'Copper',
        weightGrams: 10.2,
        diameterMm: 28.5,
        edge: 'Plain',
        alignment: 'COIN',
      ),
      primaryCitations: [
        CatalogCitation(
          tier: 'TIER_B_ACADEMIC',
          sourceName: 'Continental Treasury Board Reports (1787)',
          citationText: 'Contract authorization with James Jarvis',
          verifiedDate: '2026-10-29',
        ),
      ],
    ),
    CatalogItemModel(
      nacCode: 'NAC1.CN.CO.1C.CT.1787.XX.DRAPED.V',
      nacAliases: ['NAC1.CN.PF.1C.CT.1787.XX.DRAPED.9'],
      seoSlug: 'coins/connecticut-copper/1787-draped-bust',
      kind: 'CN',
      cc: 'CO',
      countryEra: 'PRE_FEDERAL',
      stateOrEntity: 'CT',
      denominationClass: '1C',
      series: 'CT',
      year: 1787,
      yearDisplay: '1787 · State of CT',
      facilityCode: 'XX',
      mintMarkOnCoin: false,
      mintMark: null,
      facilityNote: 'Company for Coining Coppers (New Haven, CT)',
      title: '1787 Connecticut Copper (Draped Bust)',
      subtitle: 'AUCTORI CONNEC · Inde Et Lib Seated Liberty',
      defaultFace: 'OBVERSE',
      mintageCommercial: 1100000,
      mintageEstimated: true,
      specifications: CatalogSpecifications(
        designerObverse: 'Abel Buell',
        designerReverse: 'Abel Buell',
        composition: 'Copper',
        weightGrams: 9.5,
        diameterMm: 28.0,
        edge: 'Plain',
        alignment: 'COIN',
      ),
      primaryCitations: [
        CatalogCitation(
          tier: 'TIER_B_ACADEMIC',
          sourceName: 'Connecticut State Archives',
          citationText: '1785-1788 State Coinage Grant Records',
          verifiedDate: '2026-10-29',
        ),
      ],
    ),
    CatalogItemModel(
      nacCode: 'NAC1.CN.FS.1D.SPAN8R.1798.MO.BASE.P',
      seoSlug: 'coins/spanish-8-reales/1798-mo-charles-iv',
      kind: 'CN',
      cc: 'FS',
      countryEra: 'FOREIGN_CIRCULATING',
      stateOrEntity: 'SPANISH_MILLED',
      denominationClass: '1D',
      series: 'SPAN8R',
      year: 1798,
      yearDisplay: '1798-Mo · Foreign Specie (U.S. Legal Tender)',
      facilityCode: 'MO',
      mintMarkOnCoin: true,
      mintMark: 'Mo',
      facilityNote: "Mexico City Mint (Circulating U.S. Legal Tender until 1857; FAC='MO')",
      title: '1798-Mo Spanish-American 8 Reales (Charles IV)',
      subtitle: 'Legal Tender in U.S. until Coinage Act of Feb 21, 1857',
      defaultFace: 'OBVERSE',
      imageTier: 'MUSEUM',
      imageSourceCredit: 'Smithsonian National Numismatic Collection (CC0)',
      imageLicenseType: 'CC0',
      mintageCommercial: 24000000,
      mintageEstimated: true,
      mintageReconciliationNote:
          'Authorized U.S. legal tender per Act of Feb 9, 1793 through Feb 21, 1857.',
      specifications: CatalogSpecifications(
        composition: '90.27% Silver, 9.73% Copper',
        fineness: 0.9027,
        preciousMetalType: 'SILVER',
        actualMetalWeightOz: 0.7859,
        weightGrams: 27.07,
        diameterMm: 39.0,
        edge: 'Cordoncillo (Security Edge)',
        alignment: 'COIN',
      ),
      primaryCitations: [
        CatalogCitation(
          tier: 'TIER_A_GOV',
          sourceName:
              'U.S. Coinage Act of Feb 9, 1793 & Act of Feb 21, 1857',
          citationText:
              'Regulating foreign coins as legal tender within the United States',
          verifiedDate: '2026-10-29',
        ),
      ],
    ),
    CatalogItemModel(
      nacCode: 'NAC1.CN.US.G5.LIBCAP.1838.DD.BASE.3',
      seoSlug: 'coins/liberty-head-half-eagle/1838-d-dahlonega',
      kind: 'CN',
      cc: 'US',
      countryEra: 'FEDERAL',
      denominationClass: 'G5',
      series: 'LIBCAP',
      year: 1838,
      yearDisplay: '1838-D (Dahlonega)',
      facilityCode: 'DD',
      mintMarkOnCoin: true,
      mintMark: 'D',
      facilityNote: "FAC='DD' disambiguates Dahlonega from Denver",
      title: '1838-D Classic Head \$5 Half Eagle',
      subtitle: "First Year Dahlonega Mint · Obverse Mint Mark 'D'",
      defaultFace: 'OBVERSE',
      imageTier: 'MUSEUM',
      imageSourceCredit: 'Smithsonian National Numismatic Collection (CC0)',
      imageLicenseType: 'CC0',
      mintageOfficialMint: 20583,
      mintageCommercial: 20583,
      specifications: CatalogSpecifications(
        designerObverse: 'William Kneass',
        designerReverse: 'William Kneass',
        composition: '89.92% Gold, 10.08% Alloy',
        fineness: 0.8992,
        preciousMetalType: 'GOLD',
        actualMetalWeightOz: 0.24187,
        weightGrams: 8.36,
        diameterMm: 22.5,
        edge: 'Reeded',
        alignment: 'COIN',
      ),
      primaryCitations: [
        CatalogCitation(
          tier: 'TIER_A_GOV',
          sourceName: 'U.S. Mint Annual Report (1839)',
          citationText: 'Dahlonega Branch Mint 1838 Half Eagle Deliveries',
          verifiedDate: '2026-10-29',
        ),
      ],
    ),
    CatalogItemModel(
      nacCode: 'NAC1.MD.US.PRV.CWT.1863.XX.BASE.H',
      seoSlug: 'medals/civil-war-tokens/1863-union-forever',
      kind: 'MD',
      cc: 'US',
      countryEra: 'FEDERAL',
      stateOrEntity: 'NY',
      denominationClass: 'PRV',
      series: 'CWT',
      year: 1863,
      yearDisplay: '1863 · Private Token/Medal',
      facilityCode: 'XX',
      mintMarkOnCoin: false,
      mintMark: null,
      facilityNote: 'Scovill / Private Die-Sinkers (Civil War Emergency Issue)',
      title: "1863 Civil War Patriotic Token — 'Union For Ever'",
      subtitle: 'Private Mint Emergency Copper Token · CLASS=PRV',
      defaultFace: 'OBVERSE',
      imageTier: 'PUBLIC_DOMAIN',
      imageSourceCredit: 'ANS MANTIS Public Domain Collection',
      imageLicenseType: 'CC0',
      mintageCommercial: 50000,
      mintageEstimated: true,
      specifications: CatalogSpecifications(
        composition: 'Copper/Bronze',
        weightGrams: 3.11,
        diameterMm: 19.0,
        edge: 'Plain',
        alignment: 'MEDAL',
      ),
      primaryCitations: [
        CatalogCitation(
          tier: 'TIER_B_ACADEMIC',
          sourceName: 'American Numismatic Society (ANS) MANTIS',
          citationText: 'Civil War Patriotic & Store Card Classification',
          verifiedDate: '2026-10-29',
        ),
      ],
    ),
    CatalogItemModel(
      nacCode: 'NAC1.CN.US.1D.MORGAN.1881.S.BASE.E',
      seoSlug: 'coins/morgan-dollar/1881-s',
      kind: 'CN',
      cc: 'US',
      countryEra: 'FEDERAL',
      denominationClass: '1D',
      series: 'MORGAN',
      year: 1881,
      yearDisplay: '1881-S',
      facilityCode: 'S',
      mintMarkOnCoin: true,
      mintMark: 'S',
      facilityNote: 'San Francisco Mint',
      title: '1881-S Morgan Silver Dollar',
      subtitle: 'George T. Morgan Liberty / Heraldic Eagle',
      defaultFace: 'OBVERSE',
      imageTier: 'MUSEUM',
      imageSourceCredit: 'Smithsonian National Numismatic Collection (CC0)',
      imageLicenseType: 'CC0',
      mintageOfficialMint: 12760000,
      mintageCommercial: 12760000,
      specifications: CatalogSpecifications(
        designerObverse: 'George T. Morgan',
        designerReverse: 'George T. Morgan',
        composition: '90% Silver, 10% Copper',
        fineness: 0.9,
        preciousMetalType: 'SILVER',
        actualMetalWeightOz: 0.77344,
        weightGrams: 26.73,
        diameterMm: 38.1,
        edge: 'Reeded',
        alignment: 'COIN',
      ),
      primaryCitations: [
        CatalogCitation(
          tier: 'TIER_A_GOV',
          sourceName: 'Annual Report of the Director of the Mint (FY 1882)',
          citationText: 'Table of Coinage — San Francisco Mint',
          verifiedDate: '2026-10-29',
        ),
      ],
    ),
    CatalogItemModel(
      nacCode: 'NAC1.BN.US.TN1000.TREAS.1890.BEP.WM.C',
      seoSlug: 'banknotes/treasury-note-1000/series-1890-grand-watermelon',
      kind: 'BN',
      cc: 'US',
      countryEra: 'FEDERAL',
      denominationClass: 'TN1000',
      series: 'TREAS',
      year: 1890,
      yearDisplay: 'Series 1890 · BEP',
      facilityCode: 'BEP',
      mintMarkOnCoin: false,
      mintMark: null,
      facilityNote: 'Bureau of Engraving and Printing',
      title: "Series 1890 \$1,000 Treasury Note — 'Grand Watermelon'",
      subtitle: 'Maj. Gen. George G. Meade · Large Zeroes Reverse',
      defaultFace: 'REVERSE',
      imageTier: 'MUSEUM',
      imageSourceCredit:
          'Bureau of Engraving and Printing Historical Proof Archive',
      imageLicenseType: 'US_GOV_PUBLIC_DOMAIN',
      mintageOfficialMint: 16000,
      mintageCommercial: 16000,
      specifications: CatalogSpecifications(
        designerObverse: 'Charles Burt',
        designerReverse: 'BEP Engraving Division',
        composition: '75% Cotton, 25% Linen Rag',
        diameterMm: 187.0,
        heightMm: 79.0,
        alignment: 'NOTE',
      ),
      primaryCitations: [
        CatalogCitation(
          tier: 'TIER_A_GOV',
          sourceName:
              'BEP Certified Proofs & Treasury Note Delivery Ledger (1890)',
          citationText: 'Act of July 14, 1890 Treasury Coin Notes',
          verifiedDate: '2026-10-29',
        ),
      ],
    ),
    CatalogItemModel(
      nacCode: 'NAC1.BN.US.SC5.SILV.1899.BEP.BASE.A',
      seoSlug: 'banknotes/silver-certificate-5/series-1899-chief',
      kind: 'BN',
      cc: 'US',
      countryEra: 'FEDERAL',
      denominationClass: 'SC5',
      series: 'SILV',
      year: 1899,
      yearDisplay: 'Series 1899 · BEP',
      facilityCode: 'BEP',
      mintMarkOnCoin: false,
      mintMark: null,
      facilityNote: 'Bureau of Engraving and Printing',
      title: "\$5 Silver Certificate — 'Indian Chief'",
      subtitle: 'Running Antelope · Large Size Note',
      defaultFace: 'OBVERSE',
      imageTier: 'MUSEUM',
      imageSourceCredit: 'Smithsonian National Numismatic Collection (CC0)',
      imageLicenseType: 'CC0',
      mintageCommercial: 566068000,
      specifications: CatalogSpecifications(
        designerObverse: 'George F.C. Smillie',
        designerReverse: 'BEP Engraving Division',
        composition: 'Linen/Cotton Rag',
        diameterMm: 187.0,
        heightMm: 79.0,
        alignment: 'NOTE',
      ),
      primaryCitations: [
        CatalogCitation(
          tier: 'TIER_A_GOV',
          sourceName: 'BEP Annual Production Ledger',
          citationText: 'Series 1899 Silver Certificate Deliveries',
          verifiedDate: '2026-10-29',
        ),
      ],
    ),
    CatalogItemModel(
      nacCode: 'NAC1.CN.PF.1P.PHL1P.1903.S.BASE.3',
      nacAliases: ['NAC1.CN.PF.1P.USPI.1908.S.BASE.Z'],
      seoSlug: 'coins/philippines-peso/1903-s-insular',
      kind: 'CN',
      cc: 'PF',
      countryEra: 'US_PHILIPPINES',
      denominationClass: '1P',
      series: 'PHL1P',
      year: 1903,
      yearDisplay: '1903-S · U.S. Philippines',
      facilityCode: 'S',
      mintMarkOnCoin: true,
      mintMark: 'S',
      facilityNote:
          'Struck at San Francisco for the Insular Government of the Philippines',
      title: '1903-S U.S.-Philippines One Peso',
      subtitle: 'Insular Government · Standing Filipina / Eagle & Shield',
      defaultFace: 'OBVERSE',
      imageTier: 'MUSEUM',
      imageSourceCredit: 'Smithsonian National Numismatic Collection (CC0)',
      imageLicenseType: 'CC0',
      mintageOfficialMint: 2791159,
      mintageCommercial: 2791159,
      specifications: CatalogSpecifications(
        designerObverse: 'Melecio Figueroa / Charles E. Barber',
        designerReverse: 'Melecio Figueroa / Charles E. Barber',
        composition: '90% Silver, 10% Copper',
        fineness: 0.9,
        preciousMetalType: 'SILVER',
        actualMetalWeightOz: 0.7785,
        weightGrams: 26.95,
        diameterMm: 38.0,
        edge: 'Reeded',
        alignment: 'COIN',
      ),
      primaryCitations: [
        CatalogCitation(
          tier: 'TIER_A_GOV',
          sourceName:
              'U.S. Mint Annual Report (1903) & Philippine Coinage Act',
          citationText: 'San Francisco Mint Philippine Coinage Deliveries',
          verifiedDate: '2026-10-29',
        ),
      ],
    ),
    CatalogItemModel(
      nacCode: 'NAC1.CN.US.1D.MORGAN.1921.P.BASE.4',
      seoSlug: 'coins/morgan-dollar/1921-p',
      kind: 'CN',
      cc: 'US',
      countryEra: 'FEDERAL',
      denominationClass: '1D',
      series: 'MORGAN',
      year: 1921,
      yearDisplay: '1921 (Philadelphia — No Mint Mark)',
      facilityCode: 'P',
      mintMarkOnCoin: false,
      mintMark: null,
      facilityNote: "Philadelphia Mint; FAC='P' while mint_mark_on_coin=false",
      title: '1921 Morgan Silver Dollar (Philadelphia)',
      subtitle: "Pittman Act Resumption · No Mint Mark on Coin (FAC='P')",
      defaultFace: 'OBVERSE',
      imageTier: 'MUSEUM',
      imageSourceCredit: 'Smithsonian National Numismatic Collection (CC0)',
      imageLicenseType: 'CC0',
      mintageOfficialMint: 44690000,
      mintageCommercial: 44690000,
      specifications: CatalogSpecifications(
        designerObverse: 'George T. Morgan',
        designerReverse: 'George T. Morgan',
        composition: '90% Silver, 10% Copper',
        fineness: 0.9,
        preciousMetalType: 'SILVER',
        actualMetalWeightOz: 0.77344,
        weightGrams: 26.73,
        diameterMm: 38.1,
        edge: 'Reeded',
        alignment: 'COIN',
      ),
      primaryCitations: [
        CatalogCitation(
          tier: 'TIER_A_GOV',
          sourceName: 'Annual Report of the Director of the Mint (FY 1921)',
          citationText: 'Philadelphia Mint Silver Dollar Coinage',
          verifiedDate: '2026-10-29',
        ),
      ],
    ),
    CatalogItemModel(
      nacCode: 'NAC1.MD.US.PRES.PRES.1923.P.COOL.W',
      seoSlug: 'medals/presidential-series/1923-calvin-coolidge',
      kind: 'MD',
      cc: 'US',
      countryEra: 'FEDERAL',
      denominationClass: 'PRES',
      series: 'PRES',
      year: 1923,
      yearDisplay: '1923 · Official Mint Medal',
      facilityCode: 'P',
      mintMarkOnCoin: false,
      mintMark: null,
      facilityNote: 'Philadelphia Mint Medallic Department',
      title: 'Calvin Coolidge Presidential Medal',
      subtitle: 'U.S. Mint Official Bronze Series',
      defaultFace: 'OBVERSE',
      imageTier: 'PUBLIC_DOMAIN',
      imageSourceCredit: 'U.S. Mint Medallic Archive',
      imageLicenseType: 'US_GOV_PUBLIC_DOMAIN',
      specifications: CatalogSpecifications(
        designerObverse: 'John R. Sinnock',
        designerReverse: 'John R. Sinnock',
        composition: 'Bronze',
        diameterMm: 76.2,
        edge: 'Plain',
        alignment: 'MEDAL',
      ),
      primaryCitations: [
        CatalogCitation(
          tier: 'TIER_B_ACADEMIC',
          sourceName: 'U.S. Mint Medals Catalog',
          citationText: 'Presidential Bronze Series No. 130',
          verifiedDate: '2026-10-29',
        ),
      ],
    ),
    CatalogItemModel(
      nacCode: 'NAC1.CN.US.5C.BUFFALO.1937.D.3LEG.3',
      seoSlug: 'coins/buffalo-nickel/1937-d-3-legged',
      kind: 'CN',
      cc: 'US',
      countryEra: 'FEDERAL',
      denominationClass: '5C',
      series: 'BUFFALO',
      year: 1937,
      yearDisplay: '1937-D · 3-Legged Variety',
      facilityCode: 'D',
      mintMarkOnCoin: true,
      mintMark: 'D',
      facilityNote: "Denver Mint (FAC='D')",
      title: '1937-D 3-Legged Buffalo Nickel',
      subtitle: 'Over-Polished Reverse Die Variety · VAR=3LEG',
      defaultFace: 'REVERSE',
      imageTier: 'MUSEUM',
      imageSourceCredit: 'Smithsonian National Numismatic Collection (CC0)',
      imageLicenseType: 'CC0',
      mintageOfficialMint: 17826000,
      mintageCommercial: 17826000,
      mintageEstimated: true,
      mintageReconciliationNote:
          'Included within total 1937-D Denver Mint delivery of 17,826,000 pieces.',
      specifications: CatalogSpecifications(
        designerObverse: 'James Earle Fraser',
        designerReverse: 'James Earle Fraser',
        composition: '75% Copper, 25% Nickel',
        weightGrams: 5.0,
        diameterMm: 21.2,
        edge: 'Plain',
        alignment: 'COIN',
      ),
      primaryCitations: [
        CatalogCitation(
          tier: 'TIER_A_GOV',
          sourceName: 'Annual Report of the Director of the Mint (FY 1938)',
          citationText: 'Denver Mint Five-Cent Coinage',
          verifiedDate: '2026-10-29',
        ),
      ],
    ),
    CatalogItemModel(
      nacCode: 'NAC1.BN.US.FRN1.FED.2017A.BEP.BASE.6',
      seoSlug: 'banknotes/federal-reserve-note-1/series-2017a',
      kind: 'BN',
      cc: 'US',
      countryEra: 'FEDERAL',
      denominationClass: 'FRN1',
      series: 'FED',
      year: 2017,
      yearDisplay: 'Series 2017A · BEP',
      facilityCode: 'BEP',
      mintMarkOnCoin: false,
      mintMark: null,
      facilityNote: 'Bureau of Engraving and Printing (DC & Fort Worth)',
      title: 'Series 2017A \$1 Federal Reserve Note',
      subtitle: 'George Washington · Great Seal of the United States',
      defaultFace: 'OBVERSE',
      imageTier: 'PUBLIC_DOMAIN',
      imageSourceCredit: 'Bureau of Engraving and Printing',
      imageLicenseType: 'US_GOV_PUBLIC_DOMAIN',
      mintageOfficialMint: 6502400000,
      mintageCommercial: 6502400000,
      specifications: CatalogSpecifications(
        designerObverse: 'Gilbert Stuart / BEP',
        designerReverse: 'BEP Engraving Division',
        composition: '75% Cotton, 25% Linen',
        weightGrams: 1.0,
        diameterMm: 155.95,
        heightMm: 66.29,
        alignment: 'NOTE',
      ),
      primaryCitations: [
        CatalogCitation(
          tier: 'TIER_A_GOV',
          sourceName: 'BEP Monthly Production Report (Series 2017A)',
          citationText: 'Federal Reserve Note Print Orders',
          verifiedDate: '2026-10-29',
        ),
      ],
    ),
    CatalogItemModel(
      nacCode: 'NAC1.CN.US.25C.AWQ.2022.P.MAYA.Z',
      seoSlug: 'coins/american-women-quarters/2022-p-maya-angelou',
      kind: 'CN',
      cc: 'US',
      countryEra: 'FEDERAL',
      denominationClass: '25C',
      series: 'AWQ',
      year: 2022,
      yearDisplay: '2022-P · AWQ Series',
      facilityCode: 'P',
      mintMarkOnCoin: true,
      mintMark: 'P',
      facilityNote: 'Philadelphia Mint',
      title: '2022-P Maya Angelou Quarter',
      subtitle: 'American Women Quarters · Default Unique Identity Side',
      defaultFace: 'REVERSE',
      imageTier: 'PUBLIC_DOMAIN',
      imageSourceCredit: 'United States Mint Pressroom',
      imageLicenseType: 'US_GOV_PUBLIC_DOMAIN',
      mintageOfficialMint: 258200000,
      mintageCommercial: 258200000,
      specifications: CatalogSpecifications(
        designerObverse: 'Laura Gardin Fraser',
        designerReverse: 'Emily Damstra / Craig Campbell',
        composition: 'Cupronickel Clad',
        weightGrams: 5.67,
        diameterMm: 24.26,
        edge: 'Reeded',
        alignment: 'COIN',
      ),
      primaryCitations: [
        CatalogCitation(
          tier: 'TIER_A_GOV',
          sourceName: 'U.S. Mint 2022 Circulating Coin Production Report',
          citationText: 'American Women Quarters Program — Maya Angelou',
          verifiedDate: '2026-10-29',
        ),
      ],
    ),
    CatalogItemModel(
      nacCode: 'NAC1.CN.US.1D.ASE.2024.W.PRF.S',
      seoSlug: 'coins/american-silver-eagle/2024-w-proof',
      kind: 'CN',
      cc: 'US',
      countryEra: 'FEDERAL',
      denominationClass: '1D',
      series: 'ASE',
      year: 2024,
      yearDisplay: '2024-W · Proof',
      facilityCode: 'W',
      mintMarkOnCoin: true,
      mintMark: 'W',
      facilityNote: 'West Point Mint',
      title: '2024-W American Silver Eagle (Proof)',
      subtitle: 'Walking Liberty / Type 2 Landing Eagle · West Point Mint',
      defaultFace: 'OBVERSE',
      imageTier: 'PUBLIC_DOMAIN',
      imageSourceCredit: 'United States Mint Pressroom',
      imageLicenseType: 'US_GOV_PUBLIC_DOMAIN',
      mintageOfficialMint: 310000,
      mintageCommercial: 310000,
      mintageProof: 310000,
      specifications: CatalogSpecifications(
        designerObverse: 'Adolph A. Weinman',
        designerReverse: 'Emily Damstra / Michael Gaudioso',
        composition: '99.9% Fine Silver',
        fineness: 0.999,
        preciousMetalType: 'SILVER',
        actualMetalWeightOz: 1.0,
        weightGrams: 31.103,
        diameterMm: 40.6,
        edge: 'Reeded (Anti-Counterfeiting)',
        alignment: 'COIN',
      ),
      primaryCitations: [
        CatalogCitation(
          tier: 'TIER_A_GOV',
          sourceName: 'U.S. Mint Cumulative Sales Report (2024)',
          citationText: '2024-W Proof American Eagle 1 oz Silver Coin',
          verifiedDate: '2026-10-29',
        ),
      ],
    ),
  ];
}
