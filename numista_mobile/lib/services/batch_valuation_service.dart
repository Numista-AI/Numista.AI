// batch_valuation_service.dart
//
// Estimates AI value for all unvalued coins in the user's collection using
// text-only Gemini calls (no photos required).
//
// Usage:
//   BatchValuationService.instance.start(userEmail);
//   BatchValuationService.instance.progressStream.listen((p) { ... });
//   BatchValuationService.instance.pause();
//   BatchValuationService.instance.resume();

import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:http/http.dart' as http;
import '../constants.dart';
import 'auth_service.dart';


// ── Progress model ────────────────────────────────────────────────────────────

class BatchValuationProgress {
  final int total;
  final int completed;
  final int failed;
  final bool isRunning;
  final bool isPaused;
  final String? currentCoinName;

  const BatchValuationProgress({
    this.total       = 0,
    this.completed   = 0,
    this.failed      = 0,
    this.isRunning   = false,
    this.isPaused    = false,
    this.currentCoinName,
  });

  bool get isDone      => !isRunning && !isPaused && completed + failed >= total && total > 0;
  bool get notStarted  => total == 0 && !isRunning;
  int  get remaining   => (total - completed - failed).clamp(0, total);
  double get pct       => total == 0 ? 0.0 : (completed + failed) / total;

  /// "847 of 4,366 estimated"
  String get label {
    if (total == 0) return 'Not started';
    if (isDone)     return 'All $total estimated';
    return '$completed of $total estimated';
  }

  /// Rough time remaining string, e.g. "~2 hrs 14 min remaining"
  String get etaLabel {
    if (!isRunning || remaining == 0) return '';
    final seconds = remaining * 2; // 2 sec per coin
    if (seconds < 120)  return '~${seconds}s remaining';
    if (seconds < 3600) return '~${(seconds / 60).round()} min remaining';
    final hrs = seconds ~/ 3600;
    final mins = (seconds % 3600) ~/ 60;
    return '~$hrs hr${hrs > 1 ? 's' : ''} $mins min remaining';
  }

  BatchValuationProgress copyWith({
    int? total, int? completed, int? failed,
    bool? isRunning, bool? isPaused, String? currentCoinName,
  }) => BatchValuationProgress(
    total:           total           ?? this.total,
    completed:       completed       ?? this.completed,
    failed:          failed          ?? this.failed,
    isRunning:       isRunning       ?? this.isRunning,
    isPaused:        isPaused        ?? this.isPaused,
    currentCoinName: currentCoinName ?? this.currentCoinName,
  );
}

// ── Service ───────────────────────────────────────────────────────────────────

class BatchValuationService {
  BatchValuationService._();
  static final instance = BatchValuationService._();

  // Broadcast stream so multiple widgets can listen simultaneously
  final _controller = StreamController<BatchValuationProgress>.broadcast();
  Stream<BatchValuationProgress> get progressStream => _controller.stream;

  BatchValuationProgress _progress = const BatchValuationProgress();
  BatchValuationProgress get current => _progress;

  bool _pauseRequested = false;
  bool _running        = false;


  // ── Public API ─────────────────────────────────────────────────────────────

  /// Start (or resume) the batch valuation for the current user's collection.
  /// Safe to call multiple times — ignored if already running.
  Future<void> start() async {
    if (_running) return;
    _running        = true;
    _pauseRequested = false;
    await _run();
  }

  void pause() {
    _pauseRequested = true;
    _emit(_progress.copyWith(isPaused: true, isRunning: false));
    _persistProgress();  // save immediately on pause
  }

  void resume() {
    if (_running) return;
    _pauseRequested = false;
    start();
  }

  /// Restore previously saved progress from Firestore.
  /// Call this in initState of any screen that shows the valuation badge.
  /// Emits a BatchValuationProgress with isPaused=true if there is meaningful
  /// in-progress state — this makes the Resume banner appear immediately.
  Future<void> restoreFromFirestore() async {
    final userEmail = AuthService.userEmail;
    if (userEmail.isEmpty) return;
    try {
      final doc = await FirebaseFirestore.instance
          .collection('users').doc(userEmail)
          .collection('meta').doc('valuation_state')
          .get();
      if (!doc.exists) return;
      final data      = doc.data()!;
      final completed = (data['completed'] as num?)?.toInt() ?? 0;
      final failed    = (data['failed']    as num?)?.toInt() ?? 0;
      final total     = (data['total']     as num?)?.toInt() ?? 0;
      // Only restore if there is meaningful unfinished work
      if (total > 0 && (completed + failed) < total) {
        _emit(BatchValuationProgress(
          total:     total,
          completed: completed,
          failed:    failed,
          isRunning: false,
          isPaused:  true,   // treat as paused so Resume banner shows
        ));
      }
    } catch (e) {
      debugPrint('[BatchValuation] Failed to restore progress: $e');
    }
  }


  Future<void> _run() async {
    final coinsRef = FirebaseFirestore.instance
        .collection(AuthService.coinsPath);
    final currencyRef = FirebaseFirestore.instance
        .collection(AuthService.currencyPath);

    // 1. Fetch unvalued coins
    final coinsSnap = await coinsRef.get();
    final List<_ValuationTask> tasks = [];

    for (final doc in coinsSnap.docs) {
      final data   = doc.data();
      final status = data['ai_value_status']?.toString() ?? '';
      
      // Skip only items that have completed valuation
      if (status == 'valued') continue;

      final year   = data['Year']?.toString()             ?? '';
      final denom  = data['Denomination']?.toString()     ?? '';
      final mint   = data['Mint Mark']?.toString()        ?? '';
      final cond   = data['Condition']?.toString()        ?? '';
      final series = data['Program/Series']?.toString()   ?? '';
      final metal  = data['Metal Content']?.toString()    ?? '';
      final country = data['Country']?.toString()         ?? 'USA';
      final isSet  = data['is_set'] == true || denom.toLowerCase() == 'set' || data['item_type'] == 'set';

      final mintStr = mint.isNotEmpty && mint != 'None' ? '-$mint' : '';
      final coinName = [
        if (year.isNotEmpty) '$year$mintStr',
        if (series.isNotEmpty && isSet) series else if (denom.isNotEmpty) denom,
      ].join(' ').trim();

      tasks.add(_ValuationTask(
        collection: 'coins',
        docId: doc.id,
        itemType: isSet ? 'set' : 'coin',
        name: coinName.isEmpty ? 'Unknown item' : coinName,
        year: year,
        denomination: denom,
        condition: cond,
        country: country,
        details: 'Program: $series, Metal: $metal',
        extraData: {
          'mint_mark': mint,
          'program_series': series,
          'metal_content': metal,
          'is_set': isSet,
        },
      ));
    }

    // 2. Fetch unvalued currency/banknotes
    final currencySnap = await currencyRef.get();
    for (final doc in currencySnap.docs) {
      final data = doc.data();
      final status = data['ai_value_status']?.toString() ?? '';
      if (status == 'valued') continue;

      final year   = data['Year']?.toString()             ?? '';
      final denom  = data['Denomination']?.toString()     ?? '';
      final cond   = data['Condition']?.toString()        ?? '';
      final country = data['Country']?.toString()         ?? 'USA';
      final desc   = data['Description']?.toString()       ?? '';
      final issuer = data['Series/Issuer']?.toString()     ?? '';
      final notes  = data['Personal Notes']?.toString()    ?? '';

      final name = desc.isNotEmpty ? desc : '$denom Banknote';

      tasks.add(_ValuationTask(
        collection: 'currency',
        docId: doc.id,
        itemType: 'banknote',
        name: name,
        year: year,
        denomination: denom,
        condition: cond,
        country: country,
        details: 'Issuer/Series: $issuer. Notes: $notes',
      ));
    }

    final total = tasks.length;
    int completed = _progress.completed; // resume from last position
    int failed    = _progress.failed;

    _emit(BatchValuationProgress(
      total: total, completed: completed, failed: failed,
      isRunning: true, isPaused: false,
    ));

    if (total == 0) {
      _running = false;
      final totalItemsCount = coinsSnap.docs.length + currencySnap.docs.length;
      _emit(BatchValuationProgress(
        total: totalItemsCount, completed: totalItemsCount,
        isRunning: false,
      ));
      return;
    }

    for (final task in tasks) {
      if (_pauseRequested) {
        _running = false;
        _emit(_progress.copyWith(isRunning: false, isPaused: true));
        return;
      }

      _emit(_progress.copyWith(
        total: total, isRunning: true, isPaused: false,
        currentCoinName: task.name,
      ));

      final docRef = FirebaseFirestore.instance
          .collection(AuthService.coinsPath)
          .doc(task.docId);

      try {
        // Step 1: Transition status to in_progress before issuing network request
        await docRef.set({
          'ai_value_status': 'in_progress',
        }, SetOptions(merge: true));

        Map<String, dynamic> result;
        if (task.collection == 'coins') {
          final ed = task.extraData ?? {};
          result = await _callApi(
            year: task.year,
            denomination: task.denomination,
            mintMark: ed['mint_mark'] ?? '',
            condition: task.condition,
            programSeries: ed['program_series'] ?? '',
            metalContent: ed['metal_content'] ?? '',
            country: task.country,
          );
        } else {
          result = await _callGeneralApi(
            itemType: task.itemType,
            name: task.name,
            year: task.year,
            denomination: task.denomination,
            condition: task.condition,
            country: task.country,
            details: task.details,
          );
        }

        // Step 2: Persist canonical status and values
        final status = result['ai_value_status']?.toString() ?? 'valued';
        final payload = <String, dynamic>{
          'ai_value_status':    status,
          'ai_estimated_value': result['estimated_value'] ?? 'Pending',
          'ai_value_source':    result['source'] ?? 'text_estimator',
          'ai_value_basis':     result['basis'] ?? '',
          'ai_value_confidence': result['confidence'] ?? 'LOW',
          'ai_needs_photo':     result['needs_photo'] ?? true,
          'ai_value_as_of':     DateTime.now().toUtc().toIso8601String(),
        };

        if (result['numeric_median'] != null) {
          payload['estimated_value'] = (result['numeric_median'] as num).toDouble();
        }
        if (result['low'] != null) {
          payload['ai_value_low'] = (result['low'] as num).toDouble();
        }
        if (result['high'] != null) {
          payload['ai_value_high'] = (result['high'] as num).toDouble();
        }

        await docRef.set(payload, SetOptions(merge: true));
        completed++;
      } catch (e) {
        debugPrint('[BatchValuation] Error on task (${task.collection}/${task.docId}): $e');
        try {
          await docRef.set({
            'ai_value_status': 'failed',
            'ai_value_error':  e.toString(),
          }, SetOptions(merge: true));
        } catch (_) {}
        failed++;
      }

      _emit(BatchValuationProgress(
        total: total, completed: completed, failed: failed,
        isRunning: true, isPaused: false,
      ));
      // Persist progress so the Resume banner survives a page refresh
      _persistProgress();

      // 2-second throttle between API calls
      await Future.delayed(const Duration(seconds: 2));
    }

    _running = false;
    _emit(BatchValuationProgress(
      total: total, completed: completed, failed: failed,
      isRunning: false, isPaused: false,
    ));
    // All done — clear persisted state so Resume banner doesn't reappear
    clearPersisted();
  }

  Future<Map<String, dynamic>> _callApi({
    required String year,
    required String denomination,
    required String mintMark,
    required String condition,
    required String programSeries,
    required String metalContent,
    required String country,
  }) async {
    final response = await http.post(
      Uri.parse('$kApiBaseUrl/api/estimate_value_text'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'year':           year,
        'denomination':   denomination,
        'mint_mark':      mintMark,
        'condition':      condition,
        'program_series': programSeries,
        'metal_content':  metalContent,
        'country':        country,
      }),
    ).timeout(const Duration(seconds: 30));

    if (response.statusCode != 200) {
      throw Exception('API ${response.statusCode}: ${response.body}');
    }
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> _callGeneralApi({
    required String itemType,
    required String name,
    required String year,
    required String denomination,
    required String condition,
    required String country,
    required String details,
  }) async {
    final response = await http.post(
      Uri.parse('$kApiBaseUrl/api/estimate_value_general'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'item_type':    itemType,
        'name':         name,
        'year':         year,
        'denomination': denomination,
        'condition':    condition,
        'country':      country,
        'details':      details,
      }),
    ).timeout(const Duration(seconds: 30));

    if (response.statusCode != 200) {
      throw Exception('API ${response.statusCode}: ${response.body}');
    }
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  void _emit(BatchValuationProgress p) {
    _progress = p;
    if (!_controller.isClosed) _controller.add(p);
  }

  // ── Firestore persistence ─────────────────────────────────────────────────

  /// Saves current progress to Firestore so it survives a page refresh.
  Future<void> _persistProgress() async {
    final userEmail = AuthService.userEmail;
    if (userEmail.isEmpty) return;
    try {
      await FirebaseFirestore.instance
          .collection('users').doc(userEmail)
          .collection('meta').doc('valuation_state')
          .set({
            'completed':  _progress.completed,
            'failed':     _progress.failed,
            'total':      _progress.total,
            'updatedAt':  FieldValue.serverTimestamp(),
          });
    } catch (e) {
      debugPrint('[BatchValuation] Failed to persist progress: $e');
    }
  }

  /// Removes the persisted state document — called when valuation finishes.
  Future<void> clearPersisted() async {
    final userEmail = AuthService.userEmail;
    if (userEmail.isEmpty) return;
    try {
      await FirebaseFirestore.instance
          .collection('users').doc(userEmail)
          .collection('meta').doc('valuation_state')
          .delete();
    } catch (e) {
      debugPrint('[BatchValuation] Failed to clear persisted state: $e');
    }
  }

  void dispose() => _controller.close();
}

class _ValuationTask {
  final String collection; // 'coins' or 'currency'
  final String docId;
  final String itemType;
  final String name;
  final String year;
  final String denomination;
  final String condition;
  final String country;
  final String details;
  final Map<String, dynamic>? extraData;

  _ValuationTask({
    required this.collection,
    required this.docId,
    required this.itemType,
    required this.name,
    required this.year,
    required this.denomination,
    required this.condition,
    required this.country,
    required this.details,
    this.extraData,
  });
}

