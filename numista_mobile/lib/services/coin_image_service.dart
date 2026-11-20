import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/foundation.dart' show debugPrint, visibleForTesting;
import 'canonical_mint_asset_service.dart';

/// Looks up reference coin images from the Firestore coin_image_index collection,
/// which is built by build_image_index.py from the GCS buckets:
///   - gs://us_mint_coin_images        (Tier 1 — US Mint official images)
///   - gs://numista-reference-library  (Tier 2–5 — reference + Wikimedia)
///
/// Key format in Firestore: {year}[_{mint}][_{subject}]_{program}_{side}
/// where subject is the state/president/woman slug for series coins.
///
/// Returns null for both obverse and reverse if no image is found — the caller
/// should fall back to "No photo yet" rather than showing an error.

class CoinImageService {
  static const _collection = 'coin_image_index';

  /// Programs that have per-design subjects (state, president, woman, etc.)
  /// Matches SUBJECT_PROGRAMS in build_image_index.py.
  static const _subjectPrograms = {
    '50-state-quarters',
    'presidential-dollars',
    'american-women-quarters',
    'america-the-beautiful',
    'american-innovation',
    'native-american-dollar',
    'commemorative',
    'uncirculated-sets',
    'semiquincentennial',
    // Generic programs — subject resolution still useful for fallback / 2026
    'dollar',
    'quarter',
    'dime',
  };

  /// Maps canonical program slug -> canonical denomination slug.
  /// Mirrors program_to_denom in coin_image_schema.json.
  static const _programToDenom = <String, String>{
    'lincoln-cent': 'cent',
    'indian-head-cent': 'cent',
    'flying-eagle-cent': 'cent',
    'cent': 'cent',
    'jefferson-nickel': 'nickel',
    'buffalo-nickel': 'nickel',
    'nickel': 'nickel',
    'mercury-dime': 'dime',
    'barber-dime': 'dime',
    'dime': 'dime',
    '50-state-quarters': 'quarter',
    'america-the-beautiful': 'quarter',
    'american-women-quarters': 'quarter',
    'barber-quarter': 'quarter',
    'quarter': 'quarter',
    'semiquincentennial': 'quarter',
    'kennedy-half-dollar': 'half-dollar',
    'franklin-half-dollar': 'half-dollar',
    'liberty-walking-half-dollar': 'half-dollar',
    'walking-liberty': 'half-dollar',
    'barber-half-dollar': 'half-dollar',
    'half-dollar': 'half-dollar',
    'presidential-dollars': 'dollar',
    'native-american-dollar': 'dollar',
    'american-innovation': 'dollar',
    'morgan-dollar': 'dollar',
    'peace-dollar': 'dollar',
    'eisenhower-dollar': 'dollar',
    'dollar': 'dollar',
    'american-eagle-silver': 'dollar',
    'american-eagle-gold': 'gold',
    'american-eagle-platinum': 'platinum',
    'american-eagle-palladium': 'palladium',
    'saint-gaudens': 'gold',
    'bicentennial': 'quarter',
    'commemorative': 'commemorative',
    'uncirculated-sets': 'set',
    'american-liberty': 'dollar',
    'flowing-hair': 'dollar',
  };

  /// Shared-side wildcard entries (e.g. Statue of Liberty reverse for Presidential $1).
  static const _sharedWildcardSides = <String, String>{
    'presidential-dollars': 'reverse',
    'native-american-dollar': 'obverse',
    'american-innovation': 'obverse',
    'america-the-beautiful': 'obverse',
    'american-women-quarters': 'obverse',
    '50-state-quarters': 'obverse',
  };

  /// Program-scoped exact name lists (mirrors coin_image_schema.json).
  static const _presidentialSubjects = <String, String>{
    'george washington': 'george-washington',
    'washington': 'george-washington',
    'john adams': 'john-adams',
    'adams': 'john-adams',
    'thomas jefferson': 'thomas-jefferson',
    'jefferson': 'thomas-jefferson',
    'james madison': 'james-madison',
    'madison': 'james-madison',
    'james monroe': 'james-monroe',
    'monroe': 'james-monroe',
    'john quincy adams': 'john-quincy-adams',
    'andrew jackson': 'andrew-jackson',
    'jackson': 'andrew-jackson',
    'martin van buren': 'martin-van-buren',
    'van buren': 'martin-van-buren',
    'william henry harrison': 'william-henry-harrison',
    'john tyler': 'john-tyler',
    'tyler': 'john-tyler',
    'james k polk': 'james-k-polk',
    'james polk': 'james-k-polk',
    'polk': 'james-k-polk',
    'zachary taylor': 'zachary-taylor',
    'taylor': 'zachary-taylor',
    'millard fillmore': 'millard-fillmore',
    'fillmore': 'millard-fillmore',
    'franklin pierce': 'franklin-pierce',
    'pierce': 'franklin-pierce',
    'james buchanan': 'james-buchanan',
    'buchanan': 'james-buchanan',
    'abraham lincoln': 'abraham-lincoln',
    'lincoln': 'abraham-lincoln',
    'andrew johnson': 'andrew-johnson',
    'johnson': 'andrew-johnson',
    'ulysses s grant': 'ulysses-s-grant',
    'ulysses s. grant': 'ulysses-s-grant',
    'ulysses grant': 'ulysses-s-grant',
    'grant': 'ulysses-s-grant',
    'rutherford b hayes': 'rutherford-b-hayes',
    'rutherford b. hayes': 'rutherford-b-hayes',
    'rutherford hayes': 'rutherford-b-hayes',
    'hayes': 'rutherford-b-hayes',
    'james a garfield': 'james-a-garfield',
    'james a. garfield': 'james-a-garfield',
    'james garfield': 'james-a-garfield',
    'garfield': 'james-a-garfield',
    'chester a arthur': 'chester-a-arthur',
    'chester a. arthur': 'chester-a-arthur',
    'chester arthur': 'chester-a-arthur',
    'arthur': 'chester-a-arthur',
    'grover cleveland first term': 'grover-cleveland-1st',
    'grover cleveland 1st term': 'grover-cleveland-1st',
    'grover cleveland 1st': 'grover-cleveland-1st',
    'cleveland first term': 'grover-cleveland-1st',
    'cleveland 1st term': 'grover-cleveland-1st',
    'first term': 'grover-cleveland-1st',
    '1st term': 'grover-cleveland-1st',
    'grover cleveland second term': 'grover-cleveland-2nd',
    'grover cleveland 2nd term': 'grover-cleveland-2nd',
    'grover cleveland 2nd': 'grover-cleveland-2nd',
    'cleveland second term': 'grover-cleveland-2nd',
    'cleveland 2nd term': 'grover-cleveland-2nd',
    'second term': 'grover-cleveland-2nd',
    '2nd term': 'grover-cleveland-2nd',
    'grover cleveland': 'grover-cleveland-1st',
    'cleveland': 'grover-cleveland-1st',
    'benjamin harrison': 'benjamin-harrison',
    'harrison': 'william-henry-harrison',
    'william mckinley': 'william-mckinley',
    'mckinley': 'william-mckinley',
    'theodore roosevelt': 'theodore-roosevelt',
    'teddy roosevelt': 'theodore-roosevelt',
    'william howard taft': 'william-howard-taft',
    'william taft': 'william-howard-taft',
    'taft': 'william-howard-taft',
    'woodrow wilson': 'woodrow-wilson',
    'wilson': 'woodrow-wilson',
    'warren g harding': 'warren-g-harding',
    'warren g. harding': 'warren-g-harding',
    'warren harding': 'warren-g-harding',
    'harding': 'warren-g-harding',
    'calvin coolidge': 'calvin-coolidge',
    'coolidge': 'calvin-coolidge',
    'herbert hoover': 'herbert-hoover',
    'hoover': 'herbert-hoover',
    'franklin d roosevelt': 'franklin-d-roosevelt',
    'franklin d. roosevelt': 'franklin-d-roosevelt',
    'franklin delano roosevelt': 'franklin-d-roosevelt',
    'franklin roosevelt': 'franklin-d-roosevelt',
    'fdr': 'franklin-d-roosevelt',
    'harry s truman': 'harry-s-truman',
    'harry s. truman': 'harry-s-truman',
    'harry truman': 'harry-s-truman',
    'truman': 'harry-s-truman',
    'dwight d eisenhower': 'dwight-d-eisenhower',
    'dwight d. eisenhower': 'dwight-d-eisenhower',
    'dwight eisenhower': 'dwight-d-eisenhower',
    'eisenhower': 'dwight-d-eisenhower',
    'john f kennedy': 'john-f-kennedy',
    'john f. kennedy': 'john-f-kennedy',
    'john kennedy': 'john-f-kennedy',
    'kennedy': 'john-f-kennedy',
    'lyndon b johnson': 'lyndon-b-johnson',
    'lyndon b. johnson': 'lyndon-b-johnson',
    'lyndon johnson': 'lyndon-b-johnson',
    'richard m nixon': 'richard-nixon',
    'richard m. nixon': 'richard-nixon',
    'richard nixon': 'richard-nixon',
    'nixon': 'richard-nixon',
    'gerald r ford': 'gerald-ford',
    'gerald r. ford': 'gerald-ford',
    'gerald ford': 'gerald-ford',
    'ford': 'gerald-ford',
    'ronald reagan': 'ronald-reagan',
    'reagan': 'ronald-reagan',
    'george h w bush': 'george-h-w-bush',
    'george h.w. bush': 'george-h-w-bush',
    'george hw bush': 'george-h-w-bush',
    'george bush': 'george-h-w-bush',
    'bush': 'george-h-w-bush',
  };

  static const _atbParkSubjects = <String, String>{
    'hot springs national park': 'hot-springs',
    'hot springs': 'hot-springs',
    'yellowstone national park': 'yellowstone',
    'yellowstone': 'yellowstone',
    'yosemite national park': 'yosemite',
    'yosemite': 'yosemite',
    'grand canyon national park': 'grand-canyon',
    'grand canyon': 'grand-canyon',
    'mount hood national forest': 'mount-hood',
    'mount hood': 'mount-hood',
    'gettysburg national military park': 'gettysburg',
    'gettysburg': 'gettysburg',
    'glacier national park': 'glacier',
    'glacier': 'glacier',
    'olympic national park': 'olympic',
    'olympic': 'olympic',
    'vicksburg national military park': 'vicksburg',
    'vicksburg': 'vicksburg',
    'chickasaw national recreation area': 'chickasaw',
    'chickasaw': 'chickasaw',
    'el yunque national forest': 'el-yunque',
    'el yunque': 'el-yunque',
    'chaco culture national historical park': 'chaco-culture',
    'chaco culture': 'chaco-culture',
    'acadia national park': 'acadia',
    'acadia': 'acadia',
    'hawaii volcanoes national park': 'hawaii-volcanoes',
    'hawaii volcanoes': 'hawaii-volcanoes',
    'denali national park': 'denali',
    'denali': 'denali',
    'white mountain national forest': 'white-mountain',
    'white mountain': 'white-mountain',
    "perry's victory and international peace memorial": 'perrys-victory',
    'perrys victory': 'perrys-victory',
    "perry's victory": 'perrys-victory',
    'great basin national park': 'great-basin',
    'great basin': 'great-basin',
    'fort mchenry national monument': 'fort-mchenry',
    'fort mchenry': 'fort-mchenry',
    'mount rushmore national memorial': 'mount-rushmore',
    'mount rushmore': 'mount-rushmore',
    'great smoky mountains national park': 'great-smoky-mountains',
    'great smoky mountains': 'great-smoky-mountains',
    'shenandoah national park': 'shenandoah',
    'shenandoah': 'shenandoah',
    'arches national park': 'arches',
    'arches': 'arches',
    'great sand dunes national park': 'great-sand-dunes',
    'great sand dunes': 'great-sand-dunes',
    'everglades national park': 'everglades',
    'everglades': 'everglades',
    'homestead national monument': 'homestead',
    'homestead': 'homestead',
    'kisatchie national forest': 'kisatchie',
    'kisatchie': 'kisatchie',
    'blue ridge parkway': 'blue-ridge-parkway',
    'bombay hook national wildlife refuge': 'bombay-hook',
    'bombay hook': 'bombay-hook',
    'saratoga national historical park': 'saratoga',
    'saratoga': 'saratoga',
    'shawnee national forest': 'shawnee',
    'shawnee': 'shawnee',
    'cumberland gap national historical park': 'cumberland-gap',
    'cumberland gap': 'cumberland-gap',
    'harpers ferry national historical park': 'harpers-ferry',
    'harpers ferry': 'harpers-ferry',
    'theodore roosevelt national park': 'theodore-roosevelt-np',
    'theodore roosevelt': 'theodore-roosevelt-np',
    'fort moultrie national monument': 'fort-moultrie',
    'fort moultrie': 'fort-moultrie',
    'effigy mounds national monument': 'effigy-mounds',
    'effigy mounds': 'effigy-mounds',
    'frederick douglass national historic site': 'frederick-douglass',
    'frederick douglass': 'frederick-douglass',
    'ozark national scenic riverways': 'ozark-riverways',
    'ozark riverways': 'ozark-riverways',
    'ellis island national monument': 'ellis-island',
    'ellis island': 'ellis-island',
    'george rogers clark national historical park': 'george-rogers-clark',
    'george rogers clark': 'george-rogers-clark',
    'pictured rocks national lakeshore': 'pictured-rocks',
    'pictured rocks': 'pictured-rocks',
    'apostle islands national lakeshore': 'apostle-islands',
    'apostle islands': 'apostle-islands',
    'voyageurs national park': 'voyageurs',
    'voyageurs': 'voyageurs',
    'cumberland island national seashore': 'cumberland-island',
    'cumberland island': 'cumberland-island',
    'block island national wildlife refuge': 'block-island',
    'block island': 'block-island',
    'lowell national historical park': 'lowell',
    'lowell': 'lowell',
    'american memorial park': 'american-memorial-park',
    'war in the pacific national historical park': 'war-in-the-pacific',
    'war in the pacific': 'war-in-the-pacific',
    'san antonio missions national historical park': 'san-antonio-missions',
    'san antonio missions': 'san-antonio-missions',
    'frank church river of no return wilderness': 'frank-church',
    'frank church': 'frank-church',
    'river of no return': 'frank-church',
    'national park of american samoa': 'national-park-of-american-samoa',
    'weir farm national historical park': 'weir-farm',
    'weir farm': 'weir-farm',
    'salt river bay national historical park': 'salt-river-bay',
    'salt river bay': 'salt-river-bay',
    'marsh-billings-rockefeller national historical park': 'marsh-billings-rockefeller',
    'marsh billings rockefeller': 'marsh-billings-rockefeller',
    'tallgrass prairie national preserve': 'tallgrass-prairie',
    'tallgrass prairie': 'tallgrass-prairie',
    'tuskegee airmen national historic site': 'tuskegee-airmen',
    'tuskegee airmen': 'tuskegee-airmen',
    'tuskegee': 'tuskegee-airmen',
    'crossing the delaware': 'crossing-the-delaware',
    'washington crossing historic park': 'crossing-the-delaware',
  };

  static const _stateQuarterSubjects = <String, String>{
    'alabama': 'alabama', 'alaska': 'alaska', 'arizona': 'arizona',
    'arkansas': 'arkansas', 'california': 'california', 'colorado': 'colorado',
    'connecticut': 'connecticut', 'delaware': 'delaware', 'florida': 'florida',
    'georgia': 'georgia', 'hawaii': 'hawaii', 'idaho': 'idaho',
    'illinois': 'illinois', 'indiana': 'indiana', 'iowa': 'iowa',
    'kansas': 'kansas', 'kentucky': 'kentucky', 'louisiana': 'louisiana',
    'maine': 'maine', 'maryland': 'maryland', 'massachusetts': 'massachusetts',
    'michigan': 'michigan', 'minnesota': 'minnesota', 'mississippi': 'mississippi',
    'missouri': 'missouri', 'montana': 'montana', 'nebraska': 'nebraska',
    'nevada': 'nevada', 'new hampshire': 'new-hampshire', 'new jersey': 'new-jersey',
    'new mexico': 'new-mexico', 'new york': 'new-york',
    'north carolina': 'north-carolina', 'north dakota': 'north-dakota',
    'ohio': 'ohio', 'oklahoma': 'oklahoma', 'oregon': 'oregon',
    'pennsylvania': 'pennsylvania', 'rhode island': 'rhode-island',
    'south carolina': 'south-carolina', 'south dakota': 'south-dakota',
    'tennessee': 'tennessee', 'texas': 'texas', 'utah': 'utah',
    'vermont': 'vermont', 'virginia': 'virginia', 'washington': 'washington',
    'west virginia': 'west-virginia', 'wisconsin': 'wisconsin', 'wyoming': 'wyoming',
    'puerto rico': 'puerto-rico', 'guam': 'guam',
    'us virgin islands': 'us-virgin-islands',
    'u.s. virgin islands': 'us-virgin-islands',
    'american samoa': 'american-samoa',
    'northern mariana islands': 'northern-mariana-islands',
    'northern mariana': 'northern-mariana-islands',
    'district of columbia': 'district-of-columbia',
  };

  static const _womenQuarterSubjects = <String, String>{
    'maya angelou': 'maya-angelou', 'sally ride': 'sally-ride',
    'dr sally ride': 'sally-ride',
    'wilma mankiller': 'wilma-mankiller', 'nina otero warren': 'nina-otero-warren',
    'nina otero-warren': 'nina-otero-warren', 'adelina otero-warren': 'nina-otero-warren',
    'nina otero': 'nina-otero-warren',
    'anna may wong': 'anna-may-wong', 'anna mae wong': 'anna-may-wong',
    'bessie coleman': 'bessie-coleman',
    'edith kanaka ole': 'edith-kanaka-ole',
    "edith kanaka\u02bbole": 'edith-kanaka-ole',
    "edith kanaka\u2018ole": 'edith-kanaka-ole',
    "edith kanaka\u2019ole": 'edith-kanaka-ole',
    'edith kanakaole': 'edith-kanaka-ole',
    'eleanor roosevelt': 'eleanor-roosevelt',
    'jovita idar': 'jovita-idar', 'maria tallchief': 'maria-tallchief',
    'patsy mink': 'patsy-mink', 'patsy takemoto mink': 'patsy-mink',
    'celia cruz': 'celia-cruz',
    'zitkala-sa': 'zitkala-sa', 'zitkala sa': 'zitkala-sa', 'zitkala sha': 'zitkala-sa',
    'mary edwards walker': 'mary-edwards-walker',
    'pauli murray': 'pauli-murray',
    'ida b. wells': 'ida-b-wells', 'ida b wells': 'ida-b-wells',
    'vera rubin': 'vera-rubin',
    'althea gibson': 'althea-gibson',
    'stacey park milbern': 'stacey-park-milbern',
    'juliette gordon low': 'juliette-gordon-low',
  };

  static const _nativeAmericanYears = <String, String>{
    '2009': 'three-sisters',
    '2010': 'great-law-of-peace',
    '2011': 'wampanoag-treaty',
    '2012': 'trade-routes',
    '2013': 'delaware-treaty',
    '2014': 'native-hospitality',
    '2015': 'mohawk-ironworkers',
    '2016': 'code-talkers',
    '2017': 'sequoyah',
    '2018': 'jim-thorpe',
    '2019': 'american-indians-in-space',
    '2020': 'elizabeth-peratrovich',
    '2021': 'native-americans-in-military',
    '2022': 'ely-s-parker',
    '2023': 'maria-tallchief',
    '2024': 'indian-citizenship-act',
    '2025': 'mary-g-ross',
    '2026': 'polly-cooper',
  };

  static const _semiquincentennial2026Subjects = <String, String>{
    'mayflower compact & pilgrim couple': 'mayflower-compact',
    'mayflower compact': 'mayflower-compact',
    'mayflower': 'mayflower-compact',
    'revolutionary war': 'revolutionary-war',
    'declaration of independence': 'declaration-of-independence',
    'u.s. constitution': 'us-constitution',
    'us constitution': 'us-constitution',
    'constitution': 'us-constitution',
    'gettysburg address': 'gettysburg-address',
    'emerging liberty': 'emerging-liberty',
    'liberty over tyranny': 'emerging-liberty',
    '250th anniversary uncirculated coin set': '250th-anniversary',
    '250th anniversary': '250th-anniversary',
  };

  /// Maps denomination/series strings → canonical program slug used as the
  /// Firestore key fragment. Matches the PROGRAM_MAP in build_image_index.py.
  static const _programMap = <String, String>{
    // Lincoln / cents
    'penny':                   'lincoln-cent',
    'pennies':                 'lincoln-cent',
    'cent':                    'lincoln-cent',
    'one cent':                'lincoln-cent',
    'lincoln cent':            'lincoln-cent',
    'lincoln cents':           'lincoln-cent',
    'lincoln-cent':            'lincoln-cent',
    'lincoln penny':           'lincoln-cent',
    'wheat cent':              'lincoln-cent',
    'wheat cents':             'lincoln-cent',
    'wheat penny':             'lincoln-cent',
    'lincoln cent (memorial reverse)': 'lincoln-cent',
    'lincoln penny (union shield)':     'lincoln-cent',
    // Nickels
    'nickel':                  'nickel',
    'nickels':                 'nickel',
    'jefferson nickel':        'jefferson-nickel',
    'jefferson nickels':       'jefferson-nickel',
    'jefferson-nickel':        'jefferson-nickel',
    'buffalo nickel':          'buffalo-nickel',
    'buffalo nickels':         'buffalo-nickel',
    'buffalo-nickel':          'buffalo-nickel',
    // Dimes
    'dime':                    'dime',
    'dimes':                   'dime',
    'mercury dime':            'mercury-dime',
    'mercury dimes':           'mercury-dime',
    'mercury-dime':            'mercury-dime',
    'roosevelt dime':          'dime',
    'roosevelt dimes':         'dime',
    'roosevelt-dimes':         'dime',
    // Quarters
    'quarter':                 'quarter',
    'quarters':                'quarter',
    'quarter dollar':          'quarter',
    'quarter dollar dollar':   'quarter',
    '25c':                     'quarter',
    '25 cents':                'quarter',
    'state quarter':           '50-state-quarters',
    'state quarters':          '50-state-quarters',
    '50 state quarters':       '50-state-quarters',
    '50-state-quarters':       '50-state-quarters',
    'america the beautiful':   'america-the-beautiful',
    'america the beautiful quarters': 'america-the-beautiful',
    'american women quarters': 'american-women-quarters',
    'american innovation':     'american-innovation',
    'washington quarter':      'quarter',
    // Semiquincentennial / America250 — mapped to 'quarter' to align with
    // coin_image_index keys (e.g. 2026_mayflower-compact_quarter_reverse).
    'semiquincentennial':      'quarter',
    'semiquincentennial quarter': 'quarter',
    'semiquincentennial quarters': 'quarter',
    'united states semiquincentennial (250th anniversary)': 'quarter',
    'washington quarters':     'quarter',
    // Sets
    'uncirculated sets':       'uncirculated-sets',
    'uncirculated set':        'uncirculated-sets',
    'mint set':                'uncirculated-sets',
    'mint sets':               'uncirculated-sets',
    // Half dollars
    'half dollar':             'kennedy-half-dollar',
    'half dollars':            'kennedy-half-dollar',
    '50c':                     'kennedy-half-dollar',
    'kennedy half dollar':     'kennedy-half-dollar',
    'kennedy half dollars':    'kennedy-half-dollar',
    'kennedy-half-dollar':     'kennedy-half-dollar',
    'franklin half dollar':    'franklin-half-dollar',
    'franklin half dollars':   'franklin-half-dollar',
    'franklin-half-dollar':    'franklin-half-dollar',
    'walking liberty':         'liberty-walking-half-dollar',
    'liberty walking':         'liberty-walking-half-dollar',
    'walking-liberty':         'liberty-walking-half-dollar',
    'liberty-walking-half-dollar': 'liberty-walking-half-dollar',
    'barber half dollar':      'barber-half-dollar',
    'barber-half-dollar':      'barber-half-dollar',
    'barber quarter':          'barber-quarter',
    'barber-quarter':          'barber-quarter',
    'barber dime':             'barber-dime',
    'barber-dime':             'barber-dime',
    // Dollars
    'dollar':                  'dollar',
    'dollars':                 'dollar',
    'morgan silver dollar':    'morgan-dollar',
    'morgan dollar':           'morgan-dollar',
    'morgan dollars':          'morgan-dollar',
    'morgan-dollar':           'morgan-dollar',
    'peace dollar':            'peace-dollar',
    'peace dollars':           'peace-dollar',
    'peace-dollar':            'peace-dollar',
    'sacagawea':               'native-american-dollar',
    'native american dollar':  'native-american-dollar',
    'presidential dollar':     'presidential-dollars',
    'presidential dollars':    'presidential-dollars',
    'presidential \$1 coin program': 'presidential-dollars',
    'eisenhower':              'eisenhower-dollar',
    'eisenhower dollar':       'eisenhower-dollar',
    'eisenhower-dollar':       'eisenhower-dollar',
    'ike dollar':              'eisenhower-dollar',
    'susan b anthony':         'dollar',
    'susan b. anthony':        'dollar',
    'susan b. anthony dollar': 'dollar',
    // Cents
    'indian head cent':        'indian-head-cent',
    'indian head cents':       'indian-head-cent',
    'indian head penny':       'indian-head-cent',
    'indian-head-cent':        'indian-head-cent',
    'flying eagle':            'flying-eagle-cent',
    'flying eagle cent':       'flying-eagle-cent',
    // American Eagles
    'american eagle silver':   'american-eagle-silver',
    'american silver eagle':   'american-eagle-silver',
    'american silver eagles':  'american-eagle-silver',
    'silver eagle':            'american-eagle-silver',
    'silver eagles':           'american-eagle-silver',
    'american eagle gold':     'american-eagle-gold',
    'american gold eagle':     'american-eagle-gold',
    'gold eagle':              'american-eagle-gold',
    'american eagle platinum': 'american-eagle-platinum',
    'platinum eagle':          'american-eagle-platinum',
    'american eagle palladium':'american-eagle-palladium',
    'palladium eagle':         'american-eagle-palladium',
    // Other
    'saint-gaudens':           'saint-gaudens',
    'saint gaudens':           'saint-gaudens',
    'double eagle':            'saint-gaudens',
    'indian head half eagle':  'saint-gaudens',
    'five dollars (half eagle)': 'saint-gaudens',
    'bicentennial':            'bicentennial',
    'flowing hair':            'flowing-hair',
    'flowing-hair':            'flowing-hair',
    'american liberty':        'american-liberty',
    'commemorative':           'commemorative',
  };

  /// Resolve a coin's denomination + series + subject fields to a canonical
  /// program slug. Subject is checked first so that Morgan vs Peace (both
  /// "Dollar" denomination) resolve correctly.
  static String? _resolveProgram(
      String? denomination, String? series, {String? subject}) {
    // --- Priority 0: inspect Theme/Subject for specific program hints -------
    // This resolves e.g. "2026 Peace Silver Dollar Reverse Proof" → peace-dollar
    // and "2026 Morgan Silver Dollar Reverse Proof" → morgan-dollar, even when
    // denomination is just "Dollar".
    if (subject != null && subject.trim().isNotEmpty) {
      final subj = subject.trim().toLowerCase();
      // Morgan / Peace disambiguation — both have Denomination '$1' or 'Dollar'
      // but need different program slugs for index lookup.
      if (subj.contains('morgan')) return 'morgan-dollar';
      if (subj.contains('peace')) return 'peace-dollar';
      // NOTE: Semiquincentennial / America250 / Mayflower are NOT handled here.
      // They resolve via Priority 1 _programMap ('semiquincentennial quarter' ->
      // 'quarter') so that candidate keys align with the coin_image_index
      // (e.g. 2026_mayflower-compact_quarter_reverse).
    }

    // --- Priority 1: exact match on series, then denomination ---------------
    for (final raw in [series, denomination]) {
      if (raw == null || raw.trim().isEmpty) continue;
      final key = raw.trim().toLowerCase();
      if (_programMap.containsKey(key)) return _programMap[key];
    }

    // --- Priority 2: word-boundary partial match ----------------------------
    // Sort entries by descending key length so "lincoln cent" matches before
    // "cent", and "semiquincentennial" matches before "cent".
    // Uses word-boundary regex to prevent "cent" matching inside
    // "semiquincentennial" or "25 Cents".
    final sortedEntries = _programMap.entries.toList()
      ..sort((a, b) => b.key.length.compareTo(a.key.length));
    for (final raw in [series, denomination]) {
      if (raw == null || raw.trim().isEmpty) continue;
      final key = raw.trim().toLowerCase();
      for (final entry in sortedEntries) {
        // Word-boundary match: entry.key must appear as a whole word in key
        final pattern = RegExp(r'\b' + RegExp.escape(entry.key) + r'\b');
        if (pattern.hasMatch(key)) {
          return entry.value;
        }
      }
    }
    return null;
  }

  /// Program-scoped exact subject match helper. Never uses bidirectional
  /// `entry.key.contains(key)` substring matching.
  static String? _matchSubjectMap(String key, Map<String, String> subjectMap) {
    if (subjectMap.containsKey(key)) return subjectMap[key];
    final sorted = subjectMap.entries.toList()
      ..sort((a, b) => b.key.length.compareTo(a.key.length));
    for (final entry in sorted) {
      final tokenPattern = entry.key
          .split(RegExp(r'\s+'))
          .map(RegExp.escape)
          .join(r'[\s_-]+');
      final re = RegExp(
        r'(?:^|[^a-z0-9])' + tokenPattern + r'(?:$|[^a-z0-9])',
        caseSensitive: false,
      );
      if (re.hasMatch(key)) {
        return entry.value;
      }
    }
    return null;
  }

  /// Resolve a coin's Theme/Subject field to a canonical subject slug used in
  /// the Firestore key for series coins (State Quarters, Presidents, Women, etc.)
  /// Scoped strictly to [program] to prevent cross-program collisions.
  static String? _resolveSubject(String? subject, String? program, {String? year}) {
    if (program == null || !_subjectPrograms.contains(program)) return null;
    if (program == 'native-american-dollar') {
      final y = (year ?? '').trim().replaceFirst(RegExp(r'\.0+$'), '');
      if (y.isNotEmpty && _nativeAmericanYears.containsKey(y)) {
        return _nativeAmericanYears[y];
      }
    }
    if (subject == null || subject.trim().isEmpty) return null;
    final key = subject.trim().toLowerCase();

    if (program == 'presidential-dollars') {
      return _matchSubjectMap(key, _presidentialSubjects);
    }
    if (program == 'america-the-beautiful') {
      return _matchSubjectMap(key, _atbParkSubjects);
    }
    if (program == '50-state-quarters' || program == 'american-innovation') {
      return _matchSubjectMap(key, _stateQuarterSubjects);
    }
    if (program == 'american-women-quarters') {
      return _matchSubjectMap(key, _womenQuarterSubjects);
    }
    if (program == 'quarter' || program == 'semiquincentennial' || program == 'dime') {
      return _matchSubjectMap(key, _semiquincentennial2026Subjects);
    }
    return null;
  }

  /// Build composite Firestore document keys (`{denom}|{program}|{year}|{subject}|{side}`)
  /// for a specific [side] ('obverse' or 'reverse'), plus shared-side wildcard keys
  /// (e.g. `dollar|presidential-dollars|*|shared|reverse`).
  static List<String> _compositeKeysForSide(
    String year,
    String? mint,
    String? program,
    String side, {
    String? subject,
  }) {
    final keys = <String>[];
    if (program == null || program.isEmpty) return keys;
    final denom = _programToDenom[program] ?? program;
    final subj = (subject != null && subject.isNotEmpty) ? subject : 'standard';
    final y = year.trim().replaceFirst(RegExp(r'\.0+$'), '');

    if (y.isNotEmpty) {
      keys.add('$denom|$program|$y|$subj|$side');
      if (subj != 'standard') {
        // Also allow mint-specific composite key if present, without colliding
        if (mint != null && mint.isNotEmpty) {
          keys.add('$denom|$program|$y|$subj|$side|${mint.toUpperCase()}');
        }
      } else if (mint != null && mint.isNotEmpty) {
        keys.add('$denom|$program|$y|standard|$side|${mint.toUpperCase()}');
      }
    }

    // Shared-side wildcard entry (e.g. Presidential $1 Statue of Liberty reverse,
    // ATB / AWQ / 50-State Washington obverse, Native American / Innovation obverse)
    if (_sharedWildcardSides[program] == side) {
      keys.add('$denom|$program|*|shared|$side');
    }

    return keys;
  }

  /// Build all candidate legacy Firestore document keys for a coin, in priority order.
  /// Used as dual-read fallback after composite keys.
  static List<String> _candidateBases(
      String year, String? mint, String? program, {String? subject}) {
    final bases = <String>[];
    if (program == null) return bases;

    // Subject-specific keys have highest priority (e.g. 1999_new-jersey_50-state-quarters)
    if (subject != null) {
      if (mint != null && mint.isNotEmpty) {
        bases.add('${year}_${mint}_${subject}_$program');
      }
      bases.add('${year}_${subject}_$program');
    }

    // Exact program with mint, then without (generic year+program fallbacks)
    if (mint != null && mint.isNotEmpty) {
      bases.add('${year}_${mint}_$program');
    }
    bases.add('${year}_$program');

    // Simpler fallbacks: e.g. lincoln-cent -> cent
    const simpleFallbacks = {
      'lincoln-cent':              'cent',
      'indian-head-cent':          'cent',
      'flying-eagle-cent':         'cent',
      'kennedy-half-dollar':       'dollar',
      'franklin-half-dollar':      'dollar',
      'liberty-walking-half-dollar':'dollar',
      'barber-half-dollar':        'dollar',
      'native-american-dollar':    'dollar',
      'presidential-dollars':      'dollar',
      'morgan-dollar':             'dollar',
      'peace-dollar':              'dollar',
      'eisenhower-dollar':         'dollar',
      '50-state-quarters':         'quarter',
      'american-women-quarters':   'quarter',
      'american-innovation':       'quarter',
      'america-the-beautiful':     'quarter',
      'barber-quarter':            'quarter',
      'jefferson-nickel':          'nickel',
      'buffalo-nickel':            'nickel',
      'mercury-dime':              'dime',
      'barber-dime':               'dime',
    };
    final simple = simpleFallbacks[program];
    if (simple != null) {
      if (mint != null && mint.isNotEmpty) {
        bases.add('${year}_${mint}_$simple');
      }
      bases.add('${year}_$simple');
    }

    // Reverse fallback: simple -> specific programs (quarter -> 50-state-quarters)
    const expandFallbacks = {
      'quarter': ['50-state-quarters', 'america-the-beautiful', 'american-women-quarters', 'american-innovation'],
      'cent':    ['lincoln-cent'],
      'nickel':  ['jefferson-nickel', 'buffalo-nickel'],
      'dime':    ['mercury-dime'],
      'dollar':  ['morgan-dollar', 'peace-dollar', 'native-american-dollar', 'presidential-dollars', 'kennedy-half-dollar'],
    };
    final expanded = expandFallbacks[program];
    if (expanded != null) {
      for (final p in expanded) {
        if (mint != null && mint.isNotEmpty) {
          bases.add('${year}_${mint}_$p');
        }
        bases.add('${year}_$p');
      }
    }

    // Canonical design fallback (e.g. design_peace-dollar, peace-dollar, design_lincoln-cent-memorial)
    bases.add('design_$program');
    bases.add(program);
    if (simple != null) {
      bases.add('design_$simple');
      bases.add(simple);
    }

    return bases;
  }

  /// Fetches obverse + reverse public URLs for a coin from Firestore.
  /// Returns a [CoinImageResult] -- fields are null if no image found.
  /// Never throws; errors are silently swallowed so the UI degrades gracefully.
  ///
  /// Probes composite keys (`{denom}|{program}|{year}|{subject}|{side}` and
  /// shared wildcard keys) first, then falls back to legacy `_candidateBases`
  /// for dual-read compatibility.
  static Future<CoinImageResult> fetchReferenceImages({
    required String year,
    String? mint,
    String? denomination,
    String? series,
    String? subject,   // Theme/Subject field — e.g. 'New Jersey' for state quarters
  }) async {
    final y = year.toString().replaceFirst(RegExp(r'\.0+$'), '');
    if (y == '2026' || y == '2023') {
      final pair = CanonicalMintAssetService.resolve(
        title: [series, subject].whereType<String>().join(' '),
        year: y,
        mintMark: mint,
        denomination: denomination,
      );
      if (pair != null) {
        return CoinImageResult(
          obverseUrl: pair.obverseUrl,
          reverseUrl: pair.reverseUrl,
          attribution: 'U.S. Mint',
          sourceLabel: 'Canonical Mint Asset',
          matchedKey: pair.sku,
        );
      }
    }
    try {
      final program = _resolveProgram(denomination, series, subject: subject);
      if (program == null) return const CoinImageResult();

      // Resolve subject slug (program-scoped)
      final subjectSlug = _resolveSubject(subject, program, year: y);

      final db = FirebaseFirestore.instance;

      // Independently track the best obverse and best reverse found.
      String? bestObvUrl;
      String? bestRevUrl;
      String? bestAttr;
      String? bestLabel;
      String? bestKey;

      // 1. Composite keys (v2 schema)
      final obvCompositeKeys = _compositeKeysForSide(
        y, mint?.toUpperCase(), program, 'obverse', subject: subjectSlug,
      );
      for (final docKey in obvCompositeKeys) {
        if (bestObvUrl != null) break;
        final doc = await db.collection(_collection).doc(docKey).get();
        if (doc.exists) {
          final d = doc.data()?['obverse'] as Map<String, dynamic>?;
          if (d != null) {
            bestObvUrl = d['public_url'] as String?;
            bestAttr  ??= d['attribution'] as String?;
            bestLabel ??= d['source_label'] as String?;
            bestKey   ??= docKey;
          }
        }
      }

      final revCompositeKeys = _compositeKeysForSide(
        y, mint?.toUpperCase(), program, 'reverse', subject: subjectSlug,
      );
      for (final docKey in revCompositeKeys) {
        if (bestRevUrl != null) break;
        final doc = await db.collection(_collection).doc(docKey).get();
        if (doc.exists) {
          final d = doc.data()?['reverse'] as Map<String, dynamic>?;
          if (d != null) {
            bestRevUrl = d['public_url'] as String?;
            bestAttr  ??= d['attribution'] as String?;
            bestLabel ??= d['source_label'] as String?;
            bestKey   ??= docKey;
          }
        }
      }

      if (bestObvUrl != null && bestRevUrl != null) {
        return CoinImageResult(
          obverseUrl:  bestObvUrl,
          reverseUrl:  bestRevUrl,
          attribution: bestAttr,
          sourceLabel: bestLabel,
          matchedKey:  bestKey,
        );
      }

      // 2. Dual-read fallback to legacy keys
      final bases = _candidateBases(
        y, mint?.toUpperCase(), program,
        subject: subjectSlug,
      );

      final bool hasSubject = (subjectSlug != null && subjectSlug.isNotEmpty)
          || _subjectPrograms.contains(program);

      debugPrint('[CIS] fetchReferenceImages: year=$year mint=$mint denom=$denomination series=$series subject=$subject');
      debugPrint('[CIS]   → program=$program subjectSlug=$subjectSlug hasSubject=$hasSubject');

      for (final base in bases) {
        final needsObv = bestObvUrl == null;
        final needsRev = bestRevUrl == null;
        if (!needsObv && !needsRev) break; // both sides resolved

        final isSubjectBase = subjectSlug != null && base.contains(subjectSlug);

        if (needsObv && (!hasSubject || isSubjectBase)) {
          final obvDoc = await db.collection(_collection)
              .doc('${base}_obverse').get();
          if (obvDoc.exists) {
            final d = obvDoc.data()!['obverse'] as Map<String, dynamic>?;
            if (d != null) {
              bestObvUrl = d['public_url'] as String?;
              bestAttr  ??= d['attribution'] as String?;
              bestLabel ??= d['source_label'] as String?;
              bestKey   ??= base;
            }
          }
        }

        // STEAL-GUARD: only accept reverse from subject-containing bases
        // when a subject is known. Generic reverse = honest placeholder.
        if (needsRev && (!hasSubject || isSubjectBase)) {
          final revDoc = await db.collection(_collection)
              .doc('${base}_reverse').get();
          if (revDoc.exists) {
            final d = revDoc.data()!['reverse'] as Map<String, dynamic>?;
            if (d != null) {
              bestRevUrl = d['public_url'] as String?;
              bestAttr  ??= d['attribution'] as String?;
              bestLabel ??= d['source_label'] as String?;
              bestKey   ??= base;
            }
          }
        }
      }

      if (bestObvUrl != null || bestRevUrl != null) {
        debugPrint('[CIS]   → RESULT revUrl=${bestRevUrl ?? "null"} key=$bestKey');
        return CoinImageResult(
          obverseUrl:  bestObvUrl,
          reverseUrl:  bestRevUrl,
          attribution: bestAttr,
          sourceLabel: bestLabel,
          matchedKey:  bestKey,
        );
      }
    } catch (e) {
      // Silent fail -- image lookup is non-critical
    }
    return const CoinImageResult();
  }

  /// Public helper to resolve a coin's denomination + series + subject to a
  /// canonical program slug.
  static String? resolveProgram(
      String? denomination, String? series, {String? subject}) =>
      _resolveProgram(denomination, series, subject: subject);

  // ── @visibleForTesting wrappers ──────────────────────────────────────────
  // Thin wrappers exposing pure-logic statics for MF7 regression tests.
  // These do NOT hit Firestore — only the deterministic resolver/slug logic.

  @visibleForTesting
  static String? testResolveProgram(
      String? denomination, String? series, {String? subject}) =>
      _resolveProgram(denomination, series, subject: subject);

  @visibleForTesting
  static String? testResolveSubject(String? subject, String? program, {String? year}) =>
      _resolveSubject(subject, program, year: year);

  @visibleForTesting
  static List<String> testCandidateBases(
      String year, String? mint, String? program, {String? subject}) =>
      _candidateBases(year, mint, program, subject: subject);

  @visibleForTesting
  static List<String> testCompositeKeys(
      String year, String? mint, String? program, String side, {String? subject}) =>
      _compositeKeysForSide(year, mint, program, side, subject: subject);

  @visibleForTesting
  static String? testProgramToDenom(String? program) =>
      program == null ? null : _programToDenom[program];

  @visibleForTesting
  static Set<String> get testSubjectPrograms => _subjectPrograms;

  @visibleForTesting
  static bool testHasSubject(String? subjectSlug, String? program) =>
      (subjectSlug != null && subjectSlug.isNotEmpty) ||
      _subjectPrograms.contains(program);
}

/// Result object for a coin image lookup.
class CoinImageResult {
  final String? obverseUrl;
  final String? reverseUrl;
  final String? attribution;
  final String? sourceLabel;
  final String? matchedKey;

  const CoinImageResult({
    this.obverseUrl,
    this.reverseUrl,
    this.attribution,
    this.sourceLabel,
    this.matchedKey,
  });

  bool get hasObverse => obverseUrl != null && obverseUrl!.isNotEmpty;
  bool get hasReverse => reverseUrl != null && reverseUrl!.isNotEmpty;
  bool get hasAny     => hasObverse || hasReverse;
}
