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
import '../services/set_expansion_helper.dart';


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

  // ── Coin collection cache (Part 2a/2b) ──────────────────────────────────
  // State-local, 60-second TTL. Cache survives remounts within the same
  // State lifetime but is cleared on widget disposal (hot restart, full nav).
  // DESIGN CHOICE (C-1 option b): cache is State-local only; writes on other
  // screens do not cross-invalidate within the TTL window. This is a
  // documented trade-off. Ticket B's programs_progress approach eliminates it.
  List<QueryDocumentSnapshot>? _cachedCoinDocs;
  DateTime? _cacheTimestamp;
  static const Duration _cacheTtl = Duration(seconds: 60);

  /// The Future started in initState() so it runs in parallel with the
  /// programs StreamBuilder rather than waiting for it to emit first.
  /// Typed as `List<QueryDocumentSnapshot>` so cache and live paths are uniform.
  Future<List<QueryDocumentSnapshot>>? _coinsFuture;

  @override
  void initState() {
    super.initState();
    _loadTotalReferenceCount();
    _loadProgramPreferences();
    _preloadPdfAssets();
    _startCoinsFetch();
  }

  /// Kick off the coins fetch immediately. Uses the 60-second state-local
  /// cache when still fresh; otherwise fires a new Firestore read.
  void _startCoinsFetch() {
    final authUser = FirebaseAuth.instance.currentUser;
    final isRealUser = authUser != null && !authUser.isAnonymous;

    if (!isRealUser && GuestSeedService.isBrowseDemoMode) {
      _coinsFuture = GuestSeedService.getDemoCoinsFuture()
          .then((snap) => snap.docs);
      return;
    }

    // Serve from cache if still fresh — resolves immediately, no network hit.
    if (_cachedCoinDocs != null &&
        _cacheTimestamp != null &&
        DateTime.now().difference(_cacheTimestamp!) < _cacheTtl) {
      _coinsFuture = Future.value(_cachedCoinDocs!);
      return;
    }

    // TODO Ticket B: remove limit(2000) after programsProgressAggregator
    // is confirmed live on all users. Until then, collections > 2,000 coins
    // will show program completion bars capped at 2,000 documents.
    _coinsFuture = FirebaseFirestore.instance
        .collection(AuthService.coinsPath)
        .limit(2000)
        .get()
        .then((snap) {
          // Populate the state-local cache on a live fetch.
          _cachedCoinDocs = snap.docs;
          _cacheTimestamp = DateTime.now();
          return snap.docs;
        });
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

  // ---------------------------------------------------------------------------
  // Goal Filter Helpers — PROGRAM_GOAL_PROGRESS
  // ---------------------------------------------------------------------------
  // Goal keys stored in _programGoals (from DropdownMenuItem value: confirmed
  // in live file): 'Full Master Set' | 'Circulation Only' | 'Standard Set'.
  // Long display text ('Full Master Set (All Varieties)' etc.) is child: Text only.
  //
  // Variety ID taxonomy from coin_programs_data.dart + master registry.
  // ---------------------------------------------------------------------------

  /// Returns true if [variety] counts toward [goal].
  /// Empty variety.id (variety-less coin slots) always count.
  bool _goalAllowsVariety(ChecklistVariety variety, String goal) {
    final id = variety.id.toUpperCase().trim();
    if (id.isEmpty) return true; // variety-less slots (single denomination, no mint split)

    switch (goal) {
      // ── Circulation Only: P and D business strikes only ─────────────────
      case 'Circulation Only':
        return _isCirculationVariety(id);

      // ── Standard Set: P, D, and S clad proofs ───────────────────────────
      case 'Standard Set':
        if (_isCirculationVariety(id)) return true;
        // S clad proof only — NOT silver proof, NOT satin, NOT bullion
        return id == 'S-CLAD' ||            // 50 State Quarters, DC Territories, ATB
               id == 'S-PROOF' ||           // WJNS, America250, most modern programs
               id.startsWith('S-PROOF-');   // compound: S-PROOF-T1, S-PROOF-T2 (Ike)

      // ── Full Master Set: everything counts (existing behaviour) ─────────
      case 'Full Master Set':
      default:
        return true;
    }
  }

  /// True for P and D business-strike variety ids.
  /// Explicit allowlist — does NOT include P-SATIN, P-REVERSE-PROOF,
  /// P-PROOF-CONG, or P-VDB (all Full Master only).
  bool _isCirculationVariety(String id) {
    if (id == 'P' || id == 'D') return true;                                             // bare (WJNS, Innovation, Trump, classic)
    if (id == 'P-UNC' || id == 'D-UNC') return true;                                    // uncirculated (50SQ, ATB, America250)
    if (id == 'P-T1' || id == 'P-T2' || id == 'D-T1' || id == 'D-T2') return true;    // type splits (Morgan, Ike)
    if (id.startsWith('P-PRIVY-') || id.startsWith('D-PRIVY-')) return true;            // privy P/D (America250)
    return false;
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

  // _expectedDenomFamily, _denominationMatches, and _isMatch have been removed.
  // All callers now use SlotResolver.isMatch() — the same function that drives
  // the PDF banner and grid. One clerk, one count, everywhere.

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<Map<String, List<CoinProgram>>>(
      stream: ReferenceService.getGroupedProgramsStream(),
      builder: (context, refSnapshot) {
        final allProgramsMap = refSnapshot.data ?? CoinProgramsData.usPrograms;

        return FutureBuilder<List<QueryDocumentSnapshot>>(
          // _coinsFuture was started in initState() — it runs in parallel with
          // the StreamBuilder above rather than waiting for it to emit first.
          // Cache path resolves immediately with no network round-trip.
          future: _coinsFuture,
          builder: (context, snapshot) {
            // ── Show skeleton while waiting ──────────────────────────────
            if (snapshot.connectionState == ConnectionState.waiting) {
              return _buildSkeletonGrid(allProgramsMap);
            }

            // Cache population is handled inside _startCoinsFetch's .then().
            final docs = snapshot.data ?? [];

            
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
                        final varieties = coin.varieties.isEmpty
                            ? [const ChecklistVariety(id: '', label: '')]
                            : coin.varieties;
                        totalCount += varieties.length;
                        for (var variety in varieties) {
                          bool owned = false;
                          for (var doc in docs) {
                            final data = doc.data() as Map<String, dynamic>;
                            if (SlotResolver.isMatch(data, prog, coin) &&
                                SlotResolver.matchesVariety(data, variety)) {
                              owned = true;
                              break;
                            }
                          }
                          if (owned) collectedCount++;
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
  // ── Skeleton Loader (Part 1) ─────────────────────────────────────────────
  //
  // Shown during FutureBuilder ConnectionState.waiting.
  // Program names are sourced from CoinProgramsData.usPrograms — the local
  // static fallback (last synced 2026-08-26). No network call is needed.
  // If a program exists in Firestore but not in the local list, it will
  // "pop in" after data loads — documented, acceptable trade-off.
  Widget _buildSkeletonGrid(Map<String, List<CoinProgram>> programsMap) {
    // Use local static data so names are available immediately.
    final localMap = CoinProgramsData.usPrograms;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(32.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── Header (same as real view) ──────────────────────────────────
          const Text(
            'US Mint Coin Programs',
            style: TextStyle(
              fontSize: 32,
              fontWeight: FontWeight.w900,
              fontStyle: FontStyle.italic,
              color: Color(0xFF31333F),
            ),
          ),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: const Color(0xFF3B82F6),
              borderRadius: BorderRadius.circular(6),
            ),
            child: const Text(
              'PROGRAM MANAGER',
              style: TextStyle(
                color: Colors.white,
                fontSize: 10,
                fontWeight: FontWeight.w700,
                letterSpacing: 0.5,
              ),
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Track your progress on official US Mint series.',
            style: TextStyle(color: Color(0xFF64748B), fontSize: 14),
          ),
          const SizedBox(height: 16),

          // ── Option B loading banner ─────────────────────────────────────
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            decoration: BoxDecoration(
              color: const Color(0xFFF8FAFC),
              border: Border.all(color: const Color(0xFFE2E8F0)),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Row(
              children: [
                Icon(Icons.info_outline_rounded,
                    size: 16, color: Color(0xFF64748B)),
                SizedBox(width: 8),
                Text(
                  'Loading collection data \u2014 first visit may take 3\u20135 seconds',
                  style: TextStyle(
                    fontSize: 13,
                    color: Color(0xFF64748B),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // ── Skeleton category sections ──────────────────────────────────
          ...localMap.entries.map((entry) {
            final programs = entry.value;
            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Divider(color: Color(0xFFE2E6E9)),
                const SizedBox(height: 16),
                // Category heading — ghosted
                Container(
                  height: 20,
                  width: 220,
                  decoration: BoxDecoration(
                    color: const Color(0xFFE2E8F0),
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
                const SizedBox(height: 16),
                GridView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 3,
                    crossAxisSpacing: 16,
                    mainAxisSpacing: 16,
                    childAspectRatio: 1.4,
                  ),
                  itemCount: programs.length,
                  itemBuilder: (context, index) {
                    final prog = programs[index];
                    return _buildSkeletonCard(prog.name, prog.years);
                  },
                ),
                const SizedBox(height: 32),
              ],
            );
          }),
        ],
      ),
    );
  }

  /// A single skeleton card — shows ghosted program name + year in real text,
  /// grey shimmer blocks for progress stats.
  Widget _buildSkeletonCard(String name, String years) {
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
          // Ghosted program name
          Text(
            name,
            style: const TextStyle(
              fontWeight: FontWeight.w700,
              fontSize: 16,
              color: Color(0xFFCBD5E1), // ghost — same position, lighter colour
            ),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 4),
          // Ghosted year range
          Text(
            years,
            style: const TextStyle(fontSize: 12, color: Color(0xFFE2E8F0)),
          ),
          const Spacer(),
          // Grey shimmer — progress text row
          Container(
            height: 12,
            width: double.infinity,
            decoration: BoxDecoration(
              color: const Color(0xFFE2E8F0),
              borderRadius: BorderRadius.circular(4),
            ),
          ),
          const SizedBox(height: 8),
          // Grey shimmer — progress bar
          Container(
            height: 6,
            width: double.infinity,
            decoration: BoxDecoration(
              color: const Color(0xFFE2E8F0),
              borderRadius: BorderRadius.circular(4),
            ),
          ),
          const SizedBox(height: 6),
          // Grey shimmer — advancement text
          Container(
            height: 10,
            width: 180,
            decoration: BoxDecoration(
              color: const Color(0xFFE2E8F0),
              borderRadius: BorderRadius.circular(4),
            ),
          ),
          const SizedBox(height: 10),
          // Grey shimmer — button
          Container(
            height: 36,
            width: double.infinity,
            decoration: BoxDecoration(
              color: const Color(0xFFF1F5F9),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: const Color(0xFFE2E8F0)),
            ),
          ),
        ],
      ),
    );
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
    // Expand set parents into virtual children so set members match program slots.
    final rawMaps  = docs.map((d) => d.data() as Map<String, dynamic>).toList();
    final rawIds   = docs.map((d) => d.id).toList();
    final expanded = expandCollection(rawMaps, rawIds);
    final coinPool = expanded.allItems; // parents + virtual set children

    final goal = _programGoals[program.id] ?? 'Full Master Set';

    int collectedCount = 0;
    int totalCount = 0;
    for (var coin in program.coins) {
      if (coin.name.contains("Pending")) continue;
      final varieties = coin.varieties.isEmpty
          ? [const ChecklistVariety(id: '', label: '')]
          : coin.varieties;
      for (var variety in varieties) {
        if (!_goalAllowsVariety(variety, goal)) continue; // skip out-of-goal slots
        totalCount++;                                      // only in-goal slots
        bool owned = false;
        for (final data in coinPool) {
          if (SlotResolver.isMatch(data, program, coin) &&
              SlotResolver.matchesVariety(data, variety)) {
            owned = true;
            break;
          }
        }
        if (owned) collectedCount++;
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

                                // Variety-level ownership check — uses coinPool
                                // (expanded.allItems) so virtual set children
                                // (e.g. 2002-S proof quarters) resolve correctly.
                                // Loop A (banner) already uses coinPool; Loop B
                                // must match the same source.
                                bool isOwned = false;
                                for (final data in coinPool) {
                                  if (SlotResolver.isMatch(data, program, coin) &&
                                      SlotResolver.matchesVariety(data, variety)) {
                                    isOwned = true;
                                    break;
                                  }
                                }

                                if (isOwned) {
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
        final rawMaps  = (docs ?? []).map((d) => d.data() as Map<String, dynamic>).toList();
        final rawIds   = (docs ?? []).map((d) => d.id).toList();
        final expanded = expandCollection(rawMaps, rawIds);
        inventoryMap = SlotResolver.resolveProgramInventory(
          program: program,
          coins: expanded.allItems, // virtual set children included
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
