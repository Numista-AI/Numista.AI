import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:image_picker/image_picker.dart';
import '../services/auth_service.dart';
import '../services/coin_programs_data.dart';
import '../services/reference_service.dart';
import '../models/program_model.dart';
import '../services/checklist_scan_service.dart';
import '../widgets/scan_result_dialog.dart';
import 'package:uuid/uuid.dart';
import 'package:printing/printing.dart';
import 'package:flutter/services.dart' show rootBundle;
import '../services/checklist_generator_service.dart';
import 'coin_search_screen.dart';

class ProgramManagerScreen extends StatefulWidget {
  const ProgramManagerScreen({super.key});

  @override
  State<ProgramManagerScreen> createState() => _ProgramManagerScreenState();
}

class _ProgramManagerScreenState extends State<ProgramManagerScreen> {
  // Sorting options
  String _sortOrder = "Default (Release Date)";

  // View mode
  CoinProgram? _selectedProgram;

  // Set of coins selected to add to collection
  final Set<String> _selectedToAdd = {};

  // Scan state
  bool _isScanning = false;
  final ImagePicker _imagePicker = ImagePicker();

  int _totalReferenceCount = 2834; // default fallback matching SQLite seeded catalog

  @override
  void initState() {
    super.initState();
    _loadTotalReferenceCount();
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

  bool _isMatch(Map<String, dynamic> coinData, CoinProgram program, String coinName) {
    // ── Denomination guard ────────────────────────────────────────────────────
    // Reject the coin immediately if its denomination is wrong for this program.
    // This prevents, e.g., a Quarter Dollar matching a Presidential Dollar slot,
    // a Penny matching a Lincoln Dollar slot, or a Half Dollar matching a Kennedy
    // Dollar slot.
    final expectedFamily = _expectedDenomFamily(program.name);
    if (!_denominationMatches(coinData, expectedFamily)) return false;

    // ── Program/Series match ──────────────────────────────────────────────────
    final progSeries = (coinData['Program/Series']?.toString() ?? '').toLowerCase();
    final pNameLower = program.name.toLowerCase();
    final themeSub   = (coinData['Theme/Subject']?.toString() ?? '').toLowerCase();
    final cNameLower = coinName.toLowerCase();

    if (progSeries.isNotEmpty &&
        (progSeries.contains(pNameLower) || pNameLower.contains(progSeries))) {
      // Program matches — now check if this specific coin slot matches
      if (themeSub.isNotEmpty &&
          (themeSub.contains(cNameLower) || cNameLower.contains(themeSub))) {
        return true;
      }
      final year = coinData['Year']?.toString() ?? '';
      if (year.isNotEmpty && cNameLower.contains(year)) return true;
    }

    // ── Heuristic fallback (only when program series is also consistent) ──────
    // Removed the unconstrained "if (themeSub.contains(cNameLower)) return true"
    // that caused false positives across different programs/denominations.
    // A theme-only match without a matching program is too broad.

    return false;
  }

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<Map<String, List<CoinProgram>>>(
      stream: ReferenceService.getGroupedProgramsStream(),
      builder: (context, refSnapshot) {
        final allProgramsMap = refSnapshot.data ?? CoinProgramsData.usPrograms;

        return FutureBuilder<QuerySnapshot>(
          future: FirebaseFirestore.instance.collection(AuthService.coinsPath).limit(2000).get(),
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator(color: Color(0xFFF63366)));
            }

            final docs = snapshot.data?.docs ?? [];
            
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
                        totalCount++;
                        bool isMatched = false;
                        for (var doc in docs) {
                          if (_isMatch(doc.data() as Map<String, dynamic>, prog, coin.name)) {
                            isMatched = true;
                            break;
                          }
                        }
                        if (isMatched) collectedCount++;
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
                });
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
      totalCount++;
      bool isMatched = false;
      for (var doc in docs) {
        if (_isMatch(doc.data() as Map<String, dynamic>, program, coin.name)) {
          isMatched = true;
          break;
        }
      }
      if (isMatched) collectedCount++;
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
                  foregroundColor: const Color(0xFF31333F),
                  side: const BorderSide(color: Color(0xFFE2E6E9)),
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
              // ── Scan Checklist Button ──────────────────────────────────
              _isScanning
                  ? const SizedBox(
                      width: 160,
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(
                              strokeWidth: 2.5,
                              color: Color(0xFF2563EB),
                            ),
                          ),
                          SizedBox(width: 10),
                          Text('Scanning…',
                              style: TextStyle(
                                  color: Color(0xFF2563EB),
                                  fontWeight: FontWeight.w600)),
                        ],
                      ),
                    )
                  : ElevatedButton.icon(
                      onPressed: () => _startScan(program),
                      icon: const Icon(Icons.document_scanner, size: 16),
                      label: const Text('Scan Checklist'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF2563EB),
                        foregroundColor: Colors.white,
                        elevation: 0,
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8)),
                      ),
                    ),
              const SizedBox(width: 12),
              // ── Print Checklist Button ─────────────────────────────────
              ElevatedButton.icon(
                onPressed: () async {
                  Uint8List? logoBytes;
                  try {
                    final data = await rootBundle.load('assets/logo_owl.png');
                    logoBytes = data.buffer.asUint8List();
                  } catch (e) {
                    // ignore
                  }
                  final bytes = await ChecklistGeneratorService.generateChecklist(
                      program,
                      logoBytes: logoBytes);
                  await Printing.layoutPdf(
                    onLayout: (format) => bytes,
                    name: '${program.name}_Checklist.pdf',
                  );
                },
                icon: const Icon(Icons.print, size: 16),
                label: const Text('Print Checklist'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFF63366),
                  foregroundColor: Colors.white,
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
                border: Border.all(color: const Color(0xFFD4A843).withAlpha(60)),
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
                          color: Color(0xFF475569),
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
          const Text('Program Checklist', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
          const SizedBox(height: 16),
          
          // Checklist Build
          Container(
            decoration: BoxDecoration(
              color: Colors.white,
              border: Border.all(color: const Color(0xFFE2E6E9)),
              borderRadius: BorderRadius.circular(8),
            ),
            child: ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: program.coins.length,
              separatorBuilder: (context, index) => const Divider(height: 1, color: Color(0xFFE2E6E9)),
              itemBuilder: (context, index) {
                final coin = program.coins[index];
                final coinName = coin.name;
                final isPending = coinName.contains("Pending");
                
                // Search for match
                QueryDocumentSnapshot? matchedDoc;
                for (var doc in docs) {
                  if (_isMatch(doc.data() as Map<String, dynamic>, program, coinName)) {
                    matchedDoc = doc;
                    break;
                  }
                }
                
                if (matchedDoc != null) {
                  // Found
                  final data = matchedDoc.data() as Map<String, dynamic>;
                  return ListTile(
                    contentPadding: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
                    leading: const Icon(Icons.check_circle, color: Color(0xFF10B981)),
                    title: Text(coinName, style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
                    subtitle: Text('Found match: ${data["Year"] ?? ""} ${data["Denomination"] ?? ""} - Grade: ${data["Condition"] ?? "Ungraded"}', style: const TextStyle(color: Color(0xFF64748B), fontSize: 13)),
                  );
                } else if (isPending) {
                  // Unreleased
                  return ListTile(
                    contentPadding: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
                    leading: const Icon(Icons.calendar_today, color: Color(0xFFF59E0B)),
                    title: Text(coinName, style: const TextStyle(fontStyle: FontStyle.italic, color: Color(0xFFD97706))),
                  );
                } else {
                  // Missing - allow adding to collection
                  final isSelectedToAdd = _selectedToAdd.contains(coinName);
                  return CheckboxListTile(
                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                    controlAffinity: ListTileControlAffinity.leading,
                    activeColor: const Color(0xFF3B82F6),
                    value: isSelectedToAdd,
                    onChanged: (bool? value) {
                      setState(() {
                        if (value == true) {
                          _selectedToAdd.add(coinName);
                        } else {
                          _selectedToAdd.remove(coinName);
                        }
                      });
                    },
                    title: Text(coinName, style: const TextStyle(color: Color(0xFF475569))),
                  );
                }
              },
            ),
          ),
          
          if (_selectedToAdd.isNotEmpty) ...[
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _addSelectedCoins,
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

  // ── Scan checklist via camera or gallery ──────────────────────────────────
  Future<void> _startScan(CoinProgram program) async {
    final user = AuthService.currentUser;
    if (user == null) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
              content: Text('Please sign in to use checklist scanning.'),
              backgroundColor: Colors.red),
        );
      }
      return;
    }

    // Let user choose: camera or photo library
    final source = await _showImageSourceSheet();
    if (source == null) return; // user dismissed

    final picked = await _imagePicker.pickImage(
      source: source,
      imageQuality: 90,   // good quality, reasonable size
      maxWidth: 3000,     // don't send gigantic files
    );
    if (picked == null) return; // user cancelled

    setState(() => _isScanning = true);

    try {
      final userId = user.email ?? user.uid;
      final result = await ChecklistScanService.scanChecklist(
        imageFile: File(picked.path),
        programId: program.id,
        userId: userId,
      );

      if (!mounted) return;

      if (result.success) {
        // Show the result dialog; returns true = done, false = scan another
        final done = await ScanResultDialog.show(
          context,
          result: result,
          programName: program.name,
        );
        // If they want to scan another page, re-trigger immediately
        if (done != true && mounted) {
          _startScan(program);
        }
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Scan failed: ${result.errorMessage}'),
            backgroundColor: const Color(0xFFEF4444),
            duration: const Duration(seconds: 6),
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isScanning = false);
    }
  }

  /// Bottom sheet to pick camera vs. photo library.
  Future<ImageSource?> _showImageSourceSheet() async {
    return showModalBottomSheet<ImageSource>(
      context: context,
      shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Scan Checklist',
                  style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF0F172A))),
              const SizedBox(height: 6),
              Text('Choose your checklist image source',
                  style: TextStyle(color: Colors.grey.shade600, fontSize: 13)),
              const SizedBox(height: 20),
              ListTile(
                leading: Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: const Color(0xFFEFF6FF),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(Icons.camera_alt_rounded,
                      color: Color(0xFF2563EB)),
                ),
                title: const Text('Take a Photo',
                    style: TextStyle(fontWeight: FontWeight.w600)),
                subtitle: const Text('Use your camera to photograph the checklist'),
                onTap: () => Navigator.pop(ctx, ImageSource.camera),
              ),
              const SizedBox(height: 8),
              ListTile(
                leading: Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF0FDF4),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(Icons.photo_library_rounded,
                      color: Color(0xFF10B981)),
                ),
                title: const Text('Choose from Library',
                    style: TextStyle(fontWeight: FontWeight.w600)),
                subtitle: const Text('Pick an existing photo from your gallery'),
                onTap: () => Navigator.pop(ctx, ImageSource.gallery),
              ),
              const SizedBox(height: 8),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _addSelectedCoins() async {
    if (_selectedProgram == null || _selectedToAdd.isEmpty) return;
    
    final batch = FirebaseFirestore.instance.batch();
    
    for (String coinName in _selectedToAdd) {
      final docRef = FirebaseFirestore.instance.collection(AuthService.coinsPath).doc(const Uuid().v4());
      
      // Attempt rudimentary parsing of year/denomination based on name
      String parsedYear = "";
      final yearMatch = RegExp(r'\b(17|18|19|20)\d{2}\b').firstMatch(coinName);
      if (yearMatch != null) {
        parsedYear = yearMatch.group(0)!;
      } else {
        final progYearMatch = RegExp(r'\b(17|18|19|20)\d{2}\b').firstMatch(_selectedProgram!.years);
        if (progYearMatch != null) parsedYear = progYearMatch.group(0)!;
      }
      
      String parsedDenom = "";
      final lowerName = coinName.toLowerCase();
      if (lowerName.contains("penny") || lowerName.contains("cent")) parsedDenom = "1c";
      if (lowerName.contains("nickel")) parsedDenom = "5c";
      if (lowerName.contains("dime")) parsedDenom = "10c";
      if (lowerName.contains("quarter")) parsedDenom = "25c";
      if (lowerName.contains("half")) parsedDenom = "50c";
      if (lowerName.contains("dollar") || lowerName.contains("\$1")) parsedDenom = "\$1";

      batch.set(docRef, {
        'Program/Series': _selectedProgram!.name,
        'Theme/Subject': coinName,
        'Year': parsedYear,
        'Denomination': parsedDenom,
        'Condition': 'Ungraded',
        'AI Estimated Value': 'Pending',
        'Cost': '\$0.00',
        'deep_dive_status': 'PENDING',
        'inventoryStatus': 'UNCHECKED',
        'timestamp': FieldValue.serverTimestamp(),
      });
    }

    try {
      await batch.commit();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Successfully added ${_selectedToAdd.length} coins!'), backgroundColor: Colors.green),
        );
        setState(() {
          _selectedToAdd.clear();
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
           SnackBar(content: Text('Error adding coins: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }
}
