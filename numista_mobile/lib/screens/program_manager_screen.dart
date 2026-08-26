import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../services/auth_service.dart';
import '../services/coin_programs_data.dart';
import '../services/reference_service.dart';
import '../models/program_model.dart';
import 'package:uuid/uuid.dart';
import 'package:printing/printing.dart';
import 'package:flutter/services.dart' show rootBundle;
import '../services/checklist_generator_service.dart';
import 'coin_search_screen.dart';
import '../services/guest_seed_service.dart';
import '../widgets/morgan_guide_flow.dart';
import '../utils/slot_resolver.dart';


class ProgramManagerScreen extends StatefulWidget {
  final String? initialProgramId;
  const ProgramManagerScreen({super.key, this.initialProgramId});

  @override
  State<ProgramManagerScreen> createState() => _ProgramManagerScreenState();
}

class _ProgramManagerScreenState extends State<ProgramManagerScreen> {
  // Sorting options
  String _sortOrder = "Default (Release Date)";

  // View mode
  CoinProgram? _selectedProgram;
  String _selectedMintFilter = "ALL";
  String _selectedFinishFilter = "ALL";

  // Set of coins selected to add to collection
  final Set<String> _selectedToAdd = {};

  /// Guards the Add Selected Coins button against double-tap / concurrent writes.
  bool _isSavingCoins = false;

  // Program preferences cache: programId -> goal ("Full Master Set", "Circulation / Business Strikes Only", "Standard Set")
  final Map<String, String> _programGoals = {};
  final Map<String, bool> _programManualComplete = {};

  int _totalReferenceCount = 2834; // default fallback matching SQLite seeded catalog

  // PDF Pre-cache
  Uint8List? _cachedLogoBytes;
  Uint8List? _cachedFontBytes;
  Uint8List? _cachedBoldFontBytes;
  Map<String, Uint8List>? _cachedMintMarkDiagrams;
  bool _assetsPreloaded = false;

  // PDF Generation State per Program
  String? _generatingProgramId;

  @override
  void initState() {
    super.initState();
    _loadTotalReferenceCount();
    _loadProgramPreferences();
    _preloadPdfAssets();
  }

  Future<void> _preloadPdfAssets() async {
    if (_assetsPreloaded) return;
    try {
      // Logo
      try {
        final logoData = await rootBundle.load('assets/logo_owl.png');
        _cachedLogoBytes = logoData.buffer.asUint8List();
      } catch (_) {}

      // Fonts
      try {
        final fontData = await rootBundle.load('assets/fonts/Roboto-Regular.ttf');
        _cachedFontBytes = fontData.buffer.asUint8List();
        final boldData = await rootBundle.load('assets/fonts/Roboto-Bold.ttf');
        _cachedBoldFontBytes = boldData.buffer.asUint8List();
      } catch (_) {}

      // Diagrams
      const diagramTypes = ['EDGE','OBVERSE_PORTRAIT','OBVERSE_DATE',
                            'REVERSE_EAGLE','REVERSE_LOWER','REVERSE_UPPER','MIXED','NONE'];
      final diagrams = <String, Uint8List>{};
      for (final type in diagramTypes) {
        try {
          final data = await rootBundle.load('assets/mint_mark_diagrams/$type.png');
          diagrams[type] = data.buffer.asUint8List();
        } catch (_) {}
      }
      _cachedMintMarkDiagrams = diagrams;
      _assetsPreloaded = true;
    } catch (e) {
      debugPrint('Error preloading PDF assets: $e');
    }
  }

  Future<void> _loadProgramPreferences() async {
    try {
      final userEmail = AuthService.userEmail;
      if (userEmail.isEmpty) return;
      final snap = await FirebaseFirestore.instance
          .collection('users')
          .doc(userEmail)
          .collection('program_preferences')
          .get();

      final goals = <String, String>{};
      final completes = <String, bool>{};

      for (var doc in snap.docs) {
        final d = doc.data();
        if (d['goal'] != null) goals[doc.id] = d['goal'] as String;
        if (d['is_manually_completed'] != null) {
          completes[doc.id] = d['is_manually_completed'] as bool;
        }
      }

      if (mounted) {
        setState(() {
          _programGoals.addAll(goals);
          _programManualComplete.addAll(completes);
        });
      }
    } catch (e) {
      debugPrint('Error loading program preferences: $e');
    }
  }

  Future<void> _saveProgramPreference(String programId, {String? goal, bool? isManuallyCompleted}) async {
    try {
      final userEmail = AuthService.userEmail;
      if (userEmail.isEmpty) return;

      final docRef = FirebaseFirestore.instance
          .collection('users')
          .doc(userEmail)
          .collection('program_preferences')
          .doc(programId);

      final updateData = <String, dynamic>{};
      if (goal != null) {
        updateData['goal'] = goal;
        _programGoals[programId] = goal;
      }
      if (isManuallyCompleted != null) {
        updateData['is_manually_completed'] = isManuallyCompleted;
        _programManualComplete[programId] = isManuallyCompleted;
      }

      setState(() {});

      await docRef.set(updateData, SetOptions(merge: true));
    } catch (e) {
      debugPrint('Error saving program preference: $e');
    }
  }

  Future<void> _loadTotalReferenceCount() async {
    try {
      final snap = await FirebaseFirestore.instance
          .collection('coins_reference')
          .count()
          .get();
      if (mounted && snap.count != null) {
        setState(() {
          _totalReferenceCount = snap.count!;
        });
      }
    } catch (e) {
      debugPrint('Error fetching total reference count: $e');
    }
  }


  /// Returns the denomination family expected for a given program name.
  /// e.g. "Presidential Dollars" → "dollar", "50 State Quarters" → "quarter"
  String _expectedDenomFamily(String programName) {
    final lower = programName.toLowerCase();
    if (lower.contains('dollar'))      return 'dollar';
    if (lower.contains('half'))        return 'half';
    if (lower.contains('quarter'))     return 'quarter';
    if (lower.contains('dime'))        return 'dime';
    if (lower.contains('nickel'))      return 'nickel';
    if (lower.contains('cent') || lower.contains('penny')) return 'cent';
    return ''; // unknown — don't filter
  }

  /// Returns true only if the coin document's Denomination is consistent with
  /// the expected denomination family for the given program.
  bool _denominationMatches(Map<String, dynamic> coinData, String expectedFamily) {
    if (expectedFamily.isEmpty) return true; // no constraint
    final denom = (coinData['Denomination']?.toString() ?? '').toLowerCase();
    switch (expectedFamily) {
      case 'dollar':
        // Accept: "dollar", "$1", "1 dollar", "presidential dollar", etc.
        // Reject: "quarter dollar" (which contains "dollar" but is a quarter),
        //         "half dollar", "quarter"
        if (denom.contains('quarter dollar')) return false;
        if (denom.contains('half dollar'))    return false;
        return denom.contains('dollar') || denom.contains('\$1') ||
               denom == '1' || denom.contains('1 dollar');
      case 'half':
        return denom.contains('half') || denom.contains('50c') || denom.contains('50¢');
      case 'quarter':
        // Reject "quarter dollar" only if we already know it's a quarter program
        return denom.contains('quarter') || denom.contains('25c') || denom.contains('25¢');
      case 'dime':
        return denom.contains('dime') || denom.contains('10c') || denom.contains('10¢');
      case 'nickel':
        return denom.contains('nickel') || denom.contains('5c') || denom.contains('5¢');
      case 'cent':
        return denom.contains('cent') || denom.contains('penny') ||
               denom.contains('1c') || denom.contains('1¢');
      default:
        return true;
    }
  }

  bool _isMatch(Map<String, dynamic> coinData, CoinProgram program, ProgramCoin coinSlot) {
    final denom      = (coinData['Denomination']?.toString() ?? '').toLowerCase();
    final progSeries = (coinData['Program/Series']?.toString() ?? '').trim();
    final themeSub   = (coinData['Theme/Subject']?.toString() ?? '').trim().toLowerCase();
    final title      = (coinData['Title']?.toString() ?? coinData['name']?.toString() ?? coinData['official_title']?.toString() ?? '').trim().toLowerCase();
    final year       = coinData['Year']?.toString() ?? '';
    final cNameLower = coinSlot.name.toLowerCase();
    final slotYear   = coinSlot.year ?? '';

    // ── 1. Check Multi-coin Mint / Uncirculated Set Matching ─────────────────────────
    if (denom == 'set' || progSeries.toLowerCase().contains('uncirculated set') || progSeries.toLowerCase().contains('proof set')) {
      final setContents = coinData['SetContents'] as List? ?? coinData['set_coins'] as List? ?? [];
      final setStr = '${setContents.join(" ")} $themeSub $title';
      if (setStr.trim().isNotEmpty) {
        if (cNameLower.isNotEmpty && setStr.contains(cNameLower)) return true;
      }
      return false;
    }

    // ── 2. Denomination Guard for Single Coins ────────────────────────────────
    final expectedFamily = _expectedDenomFamily(program.name);
    if (!_denominationMatches(coinData, expectedFamily)) return false;

    // ── 3. Program/Series Alignment Check ─────────────────────────────────────
    bool isSeriesMatched = program.matchesDbSeries(progSeries);
    if (!isSeriesMatched) {
      if (program.id == '2026_semiquincentennial_currency' &&
          (progSeries.toLowerCase().contains('2026') || progSeries.toLowerCase().contains('america250') || progSeries.toLowerCase().contains('semiquincentennial'))) {
        isSeriesMatched = true;
      } else if (program.id == '2026_semiquincentennial_collectibles') {
        // Constituent products span multiple Program/Series values:
        // Peace Dollar, American Silver Eagle, American Gold Buffalo,
        // American Innovation $1, United States Semiquincentennial, 2026 collectibles.
        // None of these contain the program display name, so we accept any of them.
        const collectibleSeries = {
          'peace dollar', 'american silver eagle', 'american gold buffalo',
          'american gold eagle', 'american innovation',
          '2026 collectible', 'numismatic collectible',
        };
        final psLower = progSeries.toLowerCase();
        if (collectibleSeries.any((s) => psLower.contains(s))) {
          isSeriesMatched = true;
        }
      } else if (program.id == 'washington_quarters_classic' &&
          (progSeries.toLowerCase().contains('washington') || progSeries.toLowerCase().contains('quarter'))) {
        isSeriesMatched = true;
      }
    }
    if (!isSeriesMatched) return false;

    // ── 4. Multi-design vs Single-design Matching Rules ──────────────────────
    const multiDesignProgramIds = {
      'fifty_state_quarters', 'presidential_dollars', 'america_the_beautiful_quarters',
      'american_women_quarters', 'american_innovation_dollars', '2026_semiquincentennial_currency',
      'lincoln_bicentennial_cents_2009', 'dc_territories_quarters'
    };

    if (multiDesignProgramIds.contains(program.id) || program.name.contains('50 State') || program.name.contains('Presidential') || program.name.contains('America the Beautiful')) {
      // Require design match
      if (cNameLower.isNotEmpty && ((themeSub.isNotEmpty && (themeSub.contains(cNameLower) || cNameLower.contains(themeSub))) ||
                                    (title.isNotEmpty && (title.contains(cNameLower) || cNameLower.contains(title))))) {
        if (slotYear.isEmpty || year.isEmpty || slotYear == year) {
          return true;
        }
      }
      if (cNameLower.contains('lowell') && themeSub.contains('lowell')) return true;
      if (cNameLower.contains('mayflower') && themeSub.contains('mayflower')) return true;
      return false;
    }

    // ── 4b. Collectibles program: match coin's Program/Series to slot name ──────
    // The collectibles program spans products from different series (Peace Dollar,
    // American Silver Eagle, American Gold Buffalo, American Innovation $1, etc.).
    // The year==year fallback below would paint ALL 19 slots for any 2026 coin.
    // Instead, require that the coin's Program/Series maps to the specific slot name,
    // AND that the coin's Variety/Strike Type matches the slot's finish.
    if (program.id == '2026_semiquincentennial_collectibles') {
      if (cNameLower.isEmpty) return false;
      final psLower = progSeries.toLowerCase();
      final variety = (coinData['Variety']?.toString() ?? coinData['variety']?.toString() ?? '').toLowerCase();
      final strikeType = (coinData['Strike Type']?.toString() ?? coinData['strike_type']?.toString() ?? '').toLowerCase();
      final finishHint = '$variety $strikeType'.trim();

      // ── Step 1: Series must map to this slot's product ──
      bool slotSeriesMatch = false;
      if (psLower.contains('peace dollar') && cNameLower.contains('peace')) { slotSeriesMatch = true; }
      if (psLower.contains('morgan') && cNameLower.contains('morgan')) { slotSeriesMatch = true; }
      if (psLower.contains('american silver eagle') && cNameLower.contains('silver') && cNameLower.contains('eagle')) { slotSeriesMatch = true; }
      if (psLower.contains('american gold eagle') && cNameLower.contains('gold') && cNameLower.contains('eagle') && !cNameLower.contains('buffalo')) { slotSeriesMatch = true; }
      if (psLower.contains('american buffalo') && cNameLower.contains('buffalo')) { slotSeriesMatch = true; }
      if (psLower.contains('american innovation') && cNameLower.contains('innovation')) { slotSeriesMatch = true; }
      if ((psLower.contains('semiquincentennial') || psLower.contains('america250')) &&
          (cNameLower.contains('trump') || cNameLower.contains('semiquincentennial') || cNameLower.contains('president'))) { slotSeriesMatch = true; }
      if (!slotSeriesMatch) { return false; }

      // ── Step 2: Finish must match slot name ──
      // A "Reverse Proof" coin must not match an "Enhanced Uncirculated" slot, etc.
      final slotIsRP    = cNameLower.contains('reverse proof');
      final slotIsEU    = cNameLower.contains('enhanced uncirculated') || cNameLower.contains('enhanced unc');
      final slotIsCong  = cNameLower.contains('congratulations');
      final coinIsRP    = finishHint.contains('reverse proof') || finishHint.contains('reverse-proof');
      final coinIsEU    = finishHint.contains('enhanced') || finishHint.contains(' eu');
      final coinIsCong  = finishHint.contains('congratulations') || finishHint.contains('cong');

      if (slotIsRP   && !coinIsRP)   { return false; }
      if (slotIsEU   && !coinIsEU)   { return false; }
      if (slotIsCong && !coinIsCong) { return false; }
      // If coin IS an RP/EU/Cong, it should not match a non-matching slot
      if (coinIsRP   && !slotIsRP)   { return false; }
      if (coinIsEU   && !slotIsEU)   { return false; }
      if (coinIsCong && !slotIsCong) { return false; }

      return slotYear.isEmpty || year.isEmpty || slotYear == year;
    }

    // Single-design series (Roosevelt Dimes, Morgan, Peace, SBA, Sacagawea, etc.)
    if (slotYear.isNotEmpty && year.isNotEmpty) {
      return slotYear == year;
    }

    if (cNameLower.isNotEmpty && ((themeSub.isNotEmpty && (themeSub.contains(cNameLower) || cNameLower.contains(themeSub))) ||
                                  (title.isNotEmpty && (title.contains(cNameLower) || cNameLower.contains(title))))) {
      return true;
    }

    return false;
  }

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<Map<String, List<CoinProgram>>>(
      stream: ReferenceService.getGroupedProgramsStream(),
      builder: (context, refSnapshot) {
        final allProgramsMap = refSnapshot.data ?? CoinProgramsData.usPrograms;

        // Auth-primary gate: a real non-anonymous Firebase user always reads
        // from Firestore, regardless of the in-memory demo flag. The demo
        // branch is only reached when there is no authenticated user.
        final authUser = FirebaseAuth.instance.currentUser;
        final isRealUser = authUser != null && !authUser.isAnonymous;

        return FutureBuilder<QuerySnapshot>(
          future: (!isRealUser && GuestSeedService.isBrowseDemoMode)
              ? GuestSeedService.getDemoCoinsFuture()
              : FirebaseFirestore.instance.collection(AuthService.coinsPath).limit(2000).get(),
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator(color: Color(0xFFF63366)));
            }

            final docs = snapshot.data?.docs ?? [];
            
            if (_selectedProgram == null && widget.initialProgramId != null) {
              for (final entry in allProgramsMap.entries) {
                for (final prog in entry.value) {
                  if (prog.id == widget.initialProgramId) {
                    _selectedProgram = prog;
                    break;
                  }
                }
                if (_selectedProgram != null) break;
              }
            }
            
            // Single Program View Mode
            if (_selectedProgram != null) {
              return _buildProgramDetailView(docs, _selectedProgram!);
            }

            // Grid Overview Mode
            return SingleChildScrollView(
              padding: const EdgeInsets.all(32.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // ... Header code remains the same ...
                  const Text(
                    'US Mint Coin Programs',
                    style: TextStyle(fontSize: 32, fontWeight: FontWeight.w900, fontStyle: FontStyle.italic, color: Color(0xFF31333F)),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(color: const Color(0xFF3B82F6), borderRadius: BorderRadius.circular(6)),
                    child: const Text('PROGRAM MANAGER', style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.w700, letterSpacing: 0.5)),
                  ),
                  const SizedBox(height: 8),
                  const Text('Track your progress on official US Mint series.', style: TextStyle(color: Color(0xFF64748B), fontSize: 14)),
                  const SizedBox(height: 24),
                  
                  // Sorting Dropdown
                  Container(
                    width: 250,
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                    decoration: BoxDecoration(color: Colors.white, border: Border.all(color: const Color(0xFFE2E6E9)), borderRadius: BorderRadius.circular(6)),
                    child: DropdownButtonHideUnderline(
                      child: DropdownButton<String>(
                        value: _sortOrder,
                        isExpanded: true,
                        icon: const Icon(Icons.sort, color: Color(0xFF5A5C69), size: 18),
                        items: ["Default (Release Date)", "Newest Release", "Oldest Release", "Most Complete", "Least Complete"]
                            .map((e) => DropdownMenuItem(value: e, child: Text(e, style: const TextStyle(fontSize: 14, color: Color(0xFF31333F)))))
                            .toList(),
                        onChanged: (v) {
                          if (v != null) setState(() => _sortOrder = v);
                        },
                      ),
                    ),
                  ),
                  
                  const SizedBox(height: 32),
                  
                  // Render Categories
                  ...allProgramsMap.entries.map((entry) {
                    final categoryName = entry.key;
                    final programsList = List<CoinProgram>.from(entry.value);
                    
                    // Calculate completion stats for sorting
                    final List<Map<String, dynamic>> enrichedPrograms = programsList.map((prog) {
                      int collectedCount = 0;
                      int totalCount = 0;

                      for (var coin in prog.coins) {
                        if (coin.name.contains("Pending")) continue;
                        final slotCount = coin.varieties.isEmpty ? 1 : coin.varieties.length;
                        totalCount += slotCount;
                        for (var doc in docs) {
                          if (_isMatch(doc.data() as Map<String, dynamic>, prog, coin)) {
                            // Count matched varieties rather than matched year rows
                            collectedCount += slotCount;
                            break;
                          }
                        }
                      }

                      if (totalCount == 0) totalCount = 1;
                      double pct = (collectedCount / totalCount) * 100;

                      return {
                        'program': prog,
                        'collectedCount': collectedCount,
                        'totalCount': totalCount,
                        'pct': pct,
                      };
                    }).toList();
                    
                    // Sort Logic
                    if (_sortOrder == "Most Complete") {
                      enrichedPrograms.sort((a, b) => (b['pct'] as double).compareTo(a['pct'] as double));
                    } else if (_sortOrder == "Least Complete") {
                      enrichedPrograms.sort((a, b) => (a['pct'] as double).compareTo(b['pct'] as double));
                    } else if (_sortOrder == "Newest Release") {
                      enrichedPrograms.sort((a, b) => _getStartYear((b['program'] as CoinProgram).years).compareTo(_getStartYear((a['program'] as CoinProgram).years)));
                    } else if (_sortOrder == "Oldest Release") {
                      enrichedPrograms.sort((a, b) => _getStartYear((a['program'] as CoinProgram).years).compareTo(_getStartYear((b['program'] as CoinProgram).years)));
                    }
                    
                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Divider(color: Color(0xFFE2E6E9)),
                        const SizedBox(height: 16),
                        Text(categoryName, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xFF31333F))),
                        const SizedBox(height: 16),
                        GridView.builder(
                          shrinkWrap: true,
                          physics: const NeverScrollableScrollPhysics(),
                          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                            crossAxisCount: 3,
                            crossAxisSpacing: 16,
                            mainAxisSpacing: 16,
                            childAspectRatio: 1.4, // Adjusted for typical desktop card proportions
                          ),
                          itemCount: enrichedPrograms.length,
                          itemBuilder: (context, index) {
                            final data = enrichedPrograms[index];
                            final prog = data['program'] as CoinProgram;
                            
                            return _buildProgramCard(prog, data['collectedCount'] as int, data['totalCount'] as int, data['pct'] as double);
                          },
                        ),
                        const SizedBox(height: 32),
                      ],
                    );
                  }),
                ],
              ),
            );
          },
        );
      },
    );
  }

  int _getStartYear(String years) {
    final start = RegExp(r'\d{4}').firstMatch(years);
    if (start != null) {
      return int.tryParse(start.group(0) ?? '0') ?? 0;
    }
    return 0;
  }

  Widget _buildProgramCard(CoinProgram program, int collected, int total, double pct) {
    final programOverallAdvancement = _totalReferenceCount > 0 ? (collected / _totalReferenceCount) * 100 : 0.0;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border.all(color: const Color(0xFFE2E6E9)),
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.03),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Text(
                  program.name,
                  style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 16, color: Color(0xFF0F172A)),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(width: 8),
              // Dummy link icon indicating official US mint page
              const Icon(Icons.link, color: Color(0xFFCBD5E1), size: 18),
            ],
          ),
          const SizedBox(height: 4),
          Text(program.years, style: const TextStyle(fontSize: 12, color: Color(0xFF64748B))),
          const Spacer(),
          
          // Progress text
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('${pct.toStringAsFixed(0)}%', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF3B82F6))),
              Text('$collected / $total Collected', style: const TextStyle(fontSize: 12, color: Color(0xFF64748B))),
            ],
          ),
          const SizedBox(height: 8),
          
          // Progress bar
          LinearProgressIndicator(
            value: total > 0 ? (collected / total) : 0,
            backgroundColor: const Color(0xFFE2E8F0),
            valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF3B82F6)),
            borderRadius: BorderRadius.circular(4),
            minHeight: 6,
          ),
          const SizedBox(height: 6),
          Text(
            'Advances overall record by ${programOverallAdvancement.toStringAsFixed(2)}%',
            style: const TextStyle(fontSize: 10, color: Color(0xFF64748B), fontWeight: FontWeight.w500),
          ),
          const SizedBox(height: 10),
          
          SizedBox(
            width: double.infinity,
            child: OutlinedButton(
              onPressed: () {
                setState(() {
                  _selectedProgram = program;
                  _selectedMintFilter = "ALL";
                  _selectedFinishFilter = "ALL";
                });
                _tryAdvanceMorganProgramSelect();
              },
              style: OutlinedButton.styleFrom(
                foregroundColor: const Color(0xFF0F172A),
                side: const BorderSide(color: Color(0xFFE2E8F0)),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
              ),
              child: const Text('View Checklist'),
            ),
          )
        ],
      ),
    );
  }

  // --------------------------------------------------------------------------
  // Detail View Methods
  // --------------------------------------------------------------------------

  Widget _buildProgramDetailView(List<QueryDocumentSnapshot> docs, CoinProgram program) {
    int collectedCount = 0;
    int totalCount = 0;
    for (var coin in program.coins) {
      if (coin.name.contains("Pending")) continue;
      final slotCount = coin.varieties.isEmpty ? 1 : coin.varieties.length;
      totalCount += slotCount;
      for (var doc in docs) {
        if (_isMatch(doc.data() as Map<String, dynamic>, program, coin)) {
          collectedCount += slotCount;
          break;
        }
      }
    }
    final pct = totalCount > 0 ? (collectedCount / totalCount) * 100 : 0.0;
    final programOverallAdvancement = _totalReferenceCount > 0 ? (collectedCount / _totalReferenceCount) * 100 : 0.0;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(32.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Nav Row
          Row(
            children: [
              OutlinedButton.icon(
                onPressed: () => setState(() {
                  _selectedProgram = null;
                  _selectedToAdd.clear();
                }),
                icon: const Icon(Icons.arrow_back, size: 16),
                label: const Text('Back'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: const Color(0xFF0F172A),
                  side: const BorderSide(color: Color(0xFFCBD5E1)),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                ),
              ),
              const SizedBox(width: 24),
              Expanded(
                child: Text(
                  program.name,
                  style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
                ),
              ),
              // ── Print Checklist Button ─────────────────────────────────
              ElevatedButton.icon(
                onPressed: _generatingProgramId == program.id
                    ? null
                    : () => _showPrintOptionsDialog(context, program, docs, downloadOnly: false),
                icon: _generatingProgramId == program.id
                    ? const SizedBox(
                        width: 14,
                        height: 14,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Icon(Icons.print, size: 16),
                label: Text(_generatingProgramId == program.id ? 'Generating…' : 'Print Checklist'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFF63366),
                  foregroundColor: Colors.white,
                  elevation: 0,
                ),
              ),
              const SizedBox(width: 8),
              // ── Download PDF Button ────────────────────────────────────
              OutlinedButton.icon(
                onPressed: _generatingProgramId == program.id
                    ? null
                    : () => _showPrintOptionsDialog(context, program, docs, downloadOnly: true),
                icon: const Icon(Icons.download_rounded, size: 16),
                label: const Text('Download PDF'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: const Color(0xFF2563EB),
                  side: const BorderSide(color: Color(0xFF2563EB)),
                  elevation: 0,
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          
          // Program History Card — Coin Reference Search
          GestureDetector(
            onTap: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => CoinSearchScreen(
                  initialQuery: _selectedProgram?.name ?? '',
                ),
              ),
            ),
            child: Container(
              padding: const EdgeInsets.all(20),
              width: double.infinity,
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF0F172A), Color(0xFF1E293B)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  Container(
                    width: 44, height: 44,
                    decoration: BoxDecoration(
                      color: const Color(0xFFD4A843).withAlpha(25),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Icon(Icons.auto_awesome_rounded,
                        color: Color(0xFFD4A843), size: 22),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('AI Coin Reference Search',
                            style: TextStyle(
                                color: Colors.white,
                                fontSize: 15,
                                fontWeight: FontWeight.bold)),
                        const SizedBox(height: 3),
                        Text(
                          'Search 1,900+ coins from this program in the Vertex AI reference library',
                          style: TextStyle(
                              color: Colors.white.withAlpha(150), fontSize: 12, height: 1.4),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 10),
                  const Icon(Icons.chevron_right_rounded,
                      color: Color(0xFFD4A843), size: 22),
                ],
              ),
            ),
          ),
          
          // Collection Goal Selector & Manual Complete Toggle Card
          const SizedBox(height: 24),
          Container(
            padding: const EdgeInsets.all(20),
            width: double.infinity,
            decoration: BoxDecoration(
              color: Colors.white,
              border: Border.all(color: const Color(0xFFE2E6E9)),
              borderRadius: BorderRadius.circular(12),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withAlpha(8),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Row(
              children: [
                const Icon(Icons.tune_rounded, color: Color(0xFF3B82F6), size: 24),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Set Collection Goal & Completion',
                        style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
                      ),
                      const SizedBox(height: 2),
                      const Text(
                        'Choose what type of collection you are building to customize completion stats.',
                        style: TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 16),
                // Goal Dropdown
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF8FAFC),
                    border: Border.all(color: const Color(0xFFCBD5E1)),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: DropdownButtonHideUnderline(
                    child: DropdownButton<String>(
                      value: _programGoals[program.id] ?? 'Full Master Set',
                      items: const [
                        DropdownMenuItem(
                          value: 'Full Master Set',
                          child: Text('Full Master Set (All Varieties)', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                        ),
                        DropdownMenuItem(
                          value: 'Circulation Only',
                          child: Text('Circulation / Business Strikes Only (P & D)', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                        ),
                        DropdownMenuItem(
                          value: 'Standard Set',
                          child: Text('Standard Set (P, D, S Clad Proofs)', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                        ),
                      ],
                      onChanged: (val) {
                        if (val != null) {
                          _saveProgramPreference(program.id, goal: val);
                        }
                      },
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                // Manual Complete Switch
                Row(
                  children: [
                    Switch(
                      value: _programManualComplete[program.id] ?? false,
                      activeThumbColor: const Color(0xFF10B981),
                      onChanged: (val) {
                        _saveProgramPreference(program.id, isManuallyCompleted: val);
                      },
                    ),
                    const SizedBox(width: 6),
                    Text(
                      _programManualComplete[program.id] == true ? 'Goal Met ✓' : 'Mark Complete',
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.bold,
                        color: _programManualComplete[program.id] == true ? const Color(0xFF10B981) : const Color(0xFF475569),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // Program Progress Dashboard Banner
          const SizedBox(height: 24),
          Container(
            padding: const EdgeInsets.all(20),
            width: double.infinity,
            decoration: BoxDecoration(
              color: Colors.white,
              border: Border.all(color: const Color(0xFFE2E6E9)),
              borderRadius: BorderRadius.circular(12),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.03),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Row(
              children: [
                // Sub-progress ring
                SizedBox(
                  width: 64,
                  height: 64,
                  child: Stack(
                    fit: StackFit.expand,
                    children: [
                      CircularProgressIndicator(
                        value: totalCount > 0 ? collectedCount / totalCount : 0,
                        strokeWidth: 6,
                        backgroundColor: const Color(0xFFE2E8F0),
                        valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF3B82F6)),
                      ),
                      Center(
                        child: Text(
                          '${pct.toStringAsFixed(0)}%',
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF0F172A),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 20),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Program Progress: $collectedCount of $totalCount Collected',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF0F172A),
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        'You have completed ${pct.toStringAsFixed(0)}% of ${program.name}, '
                        'advancing overall U.S. Currency System of Record completion by ${programOverallAdvancement.toStringAsFixed(2)}%.',
                        style: const TextStyle(
                          fontSize: 12,
                          color: Color(0xFF64748B),
                          height: 1.4,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 32),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Program Checklist', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
              if (_selectedMintFilter != 'ALL' || _selectedFinishFilter != 'ALL')
                TextButton.icon(
                  onPressed: () => setState(() {
                    _selectedMintFilter = 'ALL';
                    _selectedFinishFilter = 'ALL';
                  }),
                  icon: const Icon(Icons.clear_all, size: 16),
                  label: const Text('Reset Filters', style: TextStyle(fontSize: 12)),
                ),
            ],
          ),
          const SizedBox(height: 16),


          // Checklist Build
          Builder(
            builder: (context) {
              final filteredCoins = program.coins.where((coin) {
                final cName = coin.name.toUpperCase();
                // 1. Mint Mark Filter
                if (_selectedMintFilter != 'ALL') {
                  final m = _selectedMintFilter;
                  if (m == 'P' && !cName.contains('-P') && !cName.contains(' (P)') && (cName.contains('-D') || cName.contains('-S') || cName.contains('-W') || cName.contains('-O') || cName.contains('-CC'))) {
                    return false;
                  }
                  if (m != 'P' && !cName.contains('-$m') && !cName.contains(' ($m)')) {
                    return false;
                  }
                }
                // 2. Finish Filter
                if (_selectedFinishFilter == 'BUSINESS') {
                  if (cName.contains('PROOF') || cName.contains('SPECIAL') || cName.contains('SATIN') || cName.contains('REVERSE')) {
                    return false;
                  }
                } else if (_selectedFinishFilter == 'PROOF') {
                  if (!cName.contains('PROOF') && !cName.contains('SPECIAL') && !cName.contains('SATIN') && !cName.contains('REVERSE')) {
                    return false;
                  }
                }
                return true;
              }).toList();

              if (filteredCoins.isEmpty) {
                return Container(
                  padding: const EdgeInsets.all(32),
                  width: double.infinity,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    border: Border.all(color: const Color(0xFFE2E6E9)),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Column(
                    children: [
                      const Icon(Icons.filter_alt_off, size: 40, color: Color(0xFF94A3B8)),
                      const SizedBox(height: 12),
                      Text(
                        'No coins found matching active filters\n(Mint: $_selectedMintFilter, Finish: $_selectedFinishFilter)',
                        textAlign: TextAlign.center,
                        style: const TextStyle(color: Color(0xFF64748B), fontSize: 13, height: 1.5),
                      ),
                      const SizedBox(height: 12),
                      OutlinedButton(
                        onPressed: () => setState(() {
                          _selectedMintFilter = 'ALL';
                          _selectedFinishFilter = 'ALL';
                        }),
                        child: const Text('Clear Active Filters'),
                      ),
                    ],
                  ),
                );
              }

              return Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  border: Border.all(color: const Color(0xFFE2E6E9)),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: ListView.separated(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: filteredCoins.length,
                  separatorBuilder: (context, index) =>
                      const Divider(height: 1, color: Color(0xFFE2E6E9)),
                  itemBuilder: (context, index) {
                    final coin = filteredCoins[index];
                    final varieties = coin.varieties.isNotEmpty
                        ? coin.varieties
                        : [ChecklistVariety(id: '', label: coin.name)];

                    return Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.center,
                        children: [
                          // Year label — fixed width so variety chips align across rows
                          SizedBox(
                            width: 44,
                            child: Text(
                              coin.year ?? '',
                              style: const TextStyle(
                                fontWeight: FontWeight.w600,
                                fontSize: 13,
                                color: Color(0xFF0F172A),
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          // Design / state name — shown when meaningful (non-empty and not just the year)
                          if (coin.name.isNotEmpty && coin.name != (coin.year ?? ''))
                            ConstrainedBox(
                              constraints: const BoxConstraints(maxWidth: 180),
                              child: Text(
                                coin.name,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(
                                  fontSize: 13,
                                  fontWeight: FontWeight.w500,
                                  color: Color(0xFF475569),
                                ),
                              ),
                            ),
                          if (coin.name.isNotEmpty && coin.name != (coin.year ?? ''))
                            const SizedBox(width: 10),
                          // Variety chips — wrap to next line if too many
                          Expanded(
                            child: Wrap(
                              spacing: 6,
                              runSpacing: 4,
                              crossAxisAlignment: WrapCrossAlignment.center,
                              children: varieties.map((variety) {
                                final coinName =
                                    '${coin.year ?? ''}||${variety.id}||${coin.name}';
                                // Abbreviate long labels for compact display
                                final chipLabel = variety.label == 'No Mint Mark'
                                    ? 'NMM'
                                    : variety.label.isEmpty
                                        ? coin.name
                                        : variety.label;
                                final isPending =
                                    coin.name.contains('Pending') ||
                                    variety.label.contains('Pending');

                                // Variety-level ownership check
                                QueryDocumentSnapshot? matchedDoc;
                                for (var doc in docs) {
                                  final data =
                                      doc.data() as Map<String, dynamic>;
                                  if (_isMatch(data, program, coin)) {
                                    final docMint = (data['Mint Mark'] ?? '')
                                        .toString()
                                        .toUpperCase();
                                    final vId = variety.id.toUpperCase();
                                    final mintOk = vId == 'P' || vId == ''
                                        ? docMint.isEmpty || docMint == 'P'
                                        : docMint == vId ||
                                            vId.startsWith(docMint);
                                    if (mintOk) {
                                      matchedDoc = doc;
                                      break;
                                    }
                                  }
                                }

                                if (matchedDoc != null) {
                                  // ── Owned ──────────────────────────────
                                  return Container(
                                    padding: const EdgeInsets.symmetric(
                                        horizontal: 7, vertical: 3),
                                    decoration: BoxDecoration(
                                      color: const Color(0xFFD1FAE5),
                                      borderRadius: BorderRadius.circular(4),
                                    ),
                                    child: Row(
                                      mainAxisSize: MainAxisSize.min,
                                      children: [
                                        const Icon(Icons.check,
                                            size: 11,
                                            color: Color(0xFF10B981)),
                                        const SizedBox(width: 3),
                                        Text(chipLabel,
                                            style: const TextStyle(
                                              fontSize: 12,
                                              color: Color(0xFF065F46),
                                              fontWeight: FontWeight.w500,
                                            )),
                                      ],
                                    ),
                                  );
                                } else if (isPending) {
                                  // ── Pending / Unreleased ───────────────
                                  return Container(
                                    padding: const EdgeInsets.symmetric(
                                        horizontal: 7, vertical: 3),
                                    decoration: BoxDecoration(
                                      color: const Color(0xFFFEF3C7),
                                      borderRadius: BorderRadius.circular(4),
                                    ),
                                    child: Text(chipLabel,
                                        style: const TextStyle(
                                          fontSize: 12,
                                          color: Color(0xFFD97706),
                                          fontStyle: FontStyle.italic,
                                        )),
                                  );
                                } else {
                                  // ── Missing — selectable ───────────────
                                  final isSelected =
                                      _selectedToAdd.contains(coinName);
                                  return GestureDetector(
                                    onTap: () {
                                      setState(() {
                                        if (isSelected) {
                                          _selectedToAdd.remove(coinName);
                                        } else {
                                          _selectedToAdd.add(coinName);
                                        }
                                      });
                                      _tryAdvanceMorganCoinsChecked();
                                    },
                                    child: Row(
                                      mainAxisSize: MainAxisSize.min,
                                      children: [
                                        SizedBox(
                                          width: 20,
                                          height: 20,
                                          child: Checkbox(
                                            value: isSelected,
                                            onChanged: (bool? value) {
                                              setState(() {
                                                if (value == true) {
                                                  _selectedToAdd.add(coinName);
                                                } else {
                                                  _selectedToAdd
                                                      .remove(coinName);
                                                }
                                              });
                                              _tryAdvanceMorganCoinsChecked();
                                            },
                                            activeColor:
                                                const Color(0xFF3B82F6),
                                            materialTapTargetSize:
                                                MaterialTapTargetSize
                                                    .shrinkWrap,
                                            visualDensity:
                                                VisualDensity.compact,
                                          ),
                                        ),
                                        const SizedBox(width: 3),
                                        Text(chipLabel,
                                            style: const TextStyle(
                                              fontSize: 12,
                                              color: Color(0xFF475569),
                                            )),
                                      ],
                                    ),
                                  );
                                }
                              }).toList(),
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              );
            },
          ),


          
          if (_selectedToAdd.isNotEmpty) ...[
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _isSavingCoins ? null : _addSelectedCoins,
                icon: const Icon(Icons.add_task),
                label: Text('Add ${_selectedToAdd.length} Selected Coins to Wishlist / Collection'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  backgroundColor: const Color(0xFF3B82F6),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              "ℹ️ Safely adding items directly to your Firestore collection tracker.",
              style: TextStyle(color: Color(0xFF64748B), fontSize: 13),
              textAlign: TextAlign.center,
            ),
          ],
        ],
      ),
    );
  }

  Future<void> _handlePrintChecklist(
    CoinProgram program, {
    bool downloadOnly = false,
    bool personalized = false,
    List<QueryDocumentSnapshot>? docs,
  }) async {
    if (_generatingProgramId != null) return;

    setState(() {
      _generatingProgramId = program.id;
    });

    Uint8List? pdfBytes;

    try {
      if (!_assetsPreloaded) {
        await _preloadPdfAssets();
      }

      if (program.coins.isEmpty) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Unable to print: This program contains no coin definitions.'),
              backgroundColor: Colors.orange,
            ),
          );
        }
        return;
      }

      Map<String, SlotMatchResult>? inventoryMap;
      String? userEmail;
      String? snapshotId;
      int distinctOwned = 0;
      int totalOwned = 0;

      if (personalized) {
        userEmail = AuthService.currentUser?.email ?? 'Authenticated Collector';
        final coinList = (docs ?? []).map((d) => d.data() as Map<String, dynamic>).toList();
        inventoryMap = SlotResolver.resolveProgramInventory(
          program: program,
          coins: coinList,
        );
        distinctOwned = inventoryMap.values.where((r) => r.isOwned).length;
        totalOwned = inventoryMap.values.where((r) => r.isOwned).fold<int>(0, (acc, r) => acc + r.quantity);

        final totalProgramSlots = program.coins.fold<int>(0, (acc, c) => acc + (c.varieties.isEmpty ? 1 : c.varieties.length));
        snapshotId = SlotResolver.generateSnapshotId(
          collectorEmail: userEmail,
          programId: program.id,
          totalSlots: totalProgramSlots,
          resolvedSlots: inventoryMap,
          timestampUtc: DateTime.now().toUtc(),
        );
      }

      pdfBytes = await ChecklistGeneratorService.generateChecklist(
        program,
        logoBytes: _cachedLogoBytes,
        mintMarkDiagrams: _cachedMintMarkDiagrams,
        ttfFontBytes: _cachedFontBytes,
        ttfBoldFontBytes: _cachedBoldFontBytes,
        resolvedInventory: inventoryMap,
        collectorEmail: userEmail,
        snapshotId: snapshotId,
        distinctOwnedSlots: distinctOwned,
        totalOwnedItems: totalOwned,
      );

      final safeName = program.name
          .replaceAll(RegExp(r'[^\w\s-]'), '')
          .replaceAll(RegExp(r'\s+'), '_');
      final fileSuffix = personalized ? 'Collection_Progress' : 'Checklist';

      if (downloadOnly) {
        await Printing.sharePdf(
          bytes: pdfBytes,
          filename: '${safeName}_$fileSuffix.pdf',
        );
      } else {
        await Printing.layoutPdf(
          onLayout: (format) async => pdfBytes!,
          name: '${safeName}_$fileSuffix.pdf',
        );
      }
    } catch (e, stack) {
      debugPrint('Error during checklist printing: $e\n$stack');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to generate PDF checklist: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _generatingProgramId = null;
        });
      }
    }
  }

  void _showPrintOptionsDialog(
    BuildContext context,
    CoinProgram program,
    List<QueryDocumentSnapshot> docs, {
    required bool downloadOnly,
  }) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1E293B),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        title: Row(
          children: [
            Icon(
              downloadOnly ? Icons.download_rounded : Icons.print,
              color: const Color(0xFF38BDF8),
            ),
            const SizedBox(width: 10),
            Text(
              downloadOnly ? 'Download PDF Checklist' : 'Print Program Checklist',
              style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
            ),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              program.name,
              style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 13),
            ),
            const SizedBox(height: 16),
            // Option 1: Personalized Collection Progress
            InkWell(
              onTap: () {
                Navigator.pop(ctx);
                _handlePrintChecklist(program, downloadOnly: downloadOnly, personalized: true, docs: docs);
              },
              borderRadius: BorderRadius.circular(8),
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFF0F172A),
                  border: Border.all(color: const Color(0xFF2563EB), width: 1.5),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.check_circle_outline, color: Color(0xFF38BDF8), size: 28),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: const [
                          Text(
                            'My Collection Progress',
                            style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14),
                          ),
                          SizedBox(height: 3),
                          Text(
                            'Pre-filled with your checkmarks, verified grades, cert numbers, and completion %',
                            style: TextStyle(color: Color(0xFF94A3B8), fontSize: 11),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12),
            // Option 2: Blank Master Checklist
            InkWell(
              onTap: () {
                Navigator.pop(ctx);
                _handlePrintChecklist(program, downloadOnly: downloadOnly, personalized: false, docs: docs);
              },
              borderRadius: BorderRadius.circular(8),
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFF0F172A),
                  border: Border.all(color: const Color(0xFF334155)),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.checklist_rtl_rounded, color: Color(0xFF94A3B8), size: 28),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: const [
                          Text(
                            'Blank Master Checklist',
                            style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14),
                          ),
                          SizedBox(height: 3),
                          Text(
                            'Clean blank checklist template for manual handwritten logging or AI scanning',
                            style: TextStyle(color: Color(0xFF94A3B8), fontSize: 11),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel', style: TextStyle(color: Color(0xFF94A3B8))),
          ),
        ],
      ),
    );
  }

  Future<void> _addSelectedCoins() async {
    if (_selectedProgram == null || _selectedToAdd.isEmpty) return;
    if (_isSavingCoins) return;
    setState(() => _isSavingCoins = true);

    // One idempotency key per button press. A second call with the same key
    // within 60 s returns the cached result without writing extra documents.
    final idempotencyKey = const Uuid().v4();

    // Build slot payloads from the pipe-delimited key: "YEAR||VARIETY_ID||SERIES_NAME"
    final List<Map<String, String>> slots = [];
    for (final coinName in _selectedToAdd) {
      final parts = coinName.split('||');
      final parsedYear    = parts.isNotEmpty ? parts[0] : '';
      final varietyId     = parts.length > 1 ? parts[1] : '';
      final seriesName    = parts.length > 2 ? parts[2] : coinName;

      // Derive denomination from series name (same logic as before, now on seriesName)
      String parsedDenom = '';
      final lowerName = seriesName.toLowerCase();
      if (lowerName.contains('penny') || lowerName.contains('cent')) parsedDenom = '1c';
      if (lowerName.contains('nickel')) parsedDenom = '5c';
      if (lowerName.contains('dime'))   parsedDenom = '10c';
      if (lowerName.contains('quarter')) parsedDenom = '25c';
      if (lowerName.contains('half'))    parsedDenom = '50c';
      if (lowerName.contains('dollar') || lowerName.contains(r'$1')) parsedDenom = r'$1';

      // Derive mint mark from variety_id.
      // Single-letter IDs (D, S, W, O, CC) are mint marks.
      // Compound IDs starting with a mint letter (S-PROOF, S-SILVER-PROOF, D-T1) → first segment.
      // P and empty string → no mint mark on the coin face.
      String parsedMint = '';
      if (varietyId.isNotEmpty && varietyId != 'P') {
        final firstSegment = varietyId.split('-').first;
        if (RegExp(r'^[A-Z]{1,2}$').hasMatch(firstSegment) && firstSegment != 'P') {
          parsedMint = firstSegment;
        }
      }

      slots.add({
        'coin_name':    seriesName,
        'year':         parsedYear,
        'mint_mark':    parsedMint,
        'denomination': parsedDenom,
        'variety_id':   varietyId,
      });
    }


    try {
      const baseUrl = 'https://numista-backend-568985927038.us-central1.run.app';
      final response = await http.post(
        Uri.parse('$baseUrl/api/checklist/add_coins'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'idempotency_key': idempotencyKey,
          'program_id':      _selectedProgram!.id,
          'program_name':    _selectedProgram!.name,
          'user_email':      AuthService.userEmail,
          'slots':           slots,
        }),
      );

      if (!mounted) return;

      if (response.statusCode == 200) {
        final body = jsonDecode(response.body) as Map<String, dynamic>;
        final duplicateWarning = body['duplicate_warning'] as bool? ?? false;
        final coinsWritten    = body['coins_written'] as int? ?? 0;

        // Show dismissible duplicate-details banner if server detected a match.
        // Grade and variety are NOT checked — this fires only on
        // program_id + year + mint_mark. The write always completes.
        if (duplicateWarning && mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: const Text(
                'One or more of these coins may already be in your collection '
                '(same year & mint). The coins were added — tap to dismiss.',
              ),
              backgroundColor: const Color(0xFFF59E0B),
              duration: const Duration(seconds: 6),
              action: SnackBarAction(
                label: 'Dismiss',
                textColor: Colors.white,
                onPressed: () =>
                    ScaffoldMessenger.of(context).hideCurrentSnackBar(),
              ),
            ),
          );
        }

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Successfully added $coinsWritten coin${coinsWritten == 1 ? '' : 's'}!'),
            backgroundColor: Colors.green,
          ),
        );
        _tryAdvanceMorganCoinsCommitted();
        setState(() { _selectedToAdd.clear(); });
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error adding coins (${response.statusCode}): ${response.body}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Network error adding coins: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isSavingCoins = false);
    }
  }



  void _tryAdvanceMorganProgramSelect() {
    final gs = MorganGuideService.current.value;
    if (gs != null &&
        gs.guide.id == 'guide_programs' &&
        gs.step == 0) {
      MorganGuideService.next();
    }
  }

  void _tryAdvanceMorganCoinsChecked() {
    final gs = MorganGuideService.current.value;
    if (gs != null &&
        gs.guide.id == 'guide_programs' &&
        gs.step == 1 &&
        _selectedToAdd.isNotEmpty) {
      MorganGuideService.next();
    }
  }

  void _tryAdvanceMorganCoinsCommitted() {
    final gs = MorganGuideService.current.value;
    if (gs != null &&
        gs.guide.id == 'guide_programs' &&
        gs.step == 2) {
      MorganGuideService.next();
    }
  }
}
