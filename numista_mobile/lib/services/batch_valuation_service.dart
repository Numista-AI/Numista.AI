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
  }

  void resume() {
    if (_running) return;
    _pauseRequested = false;
    start();
  }

  // ── Internal ───────────────────────────────────────────────────────────────

  Future<void> _run() async {
    final coinsRef = FirebaseFirestore.instance
        .collection(AuthService.coinsPath);

    // Fetch all coins where AI Estimated Value is missing/Pending
    // (photo-scanned coins with ai_value_source == 'photo_scan' are skipped)
    final snap = await coinsRef.get();
    final unvalued = snap.docs.where((d) {
      final data   = d.data();
      final val    = data['AI Estimated Value']?.toString() ?? '';
      final source = data['ai_value_source']?.toString() ?? '';
      // Skip if already photo-scanned (those are more accurate)
      if (source == 'photo_scan') return false;
      // Skip if already has a text estimate
      if (source == 'text_estimator') return false;
      // Process if value is empty or Pending
      return val.isEmpty || val == 'Pending' || val == 'null';
    }).toList();

    final total = unvalued.length;
    int completed = _progress.completed; // resume from last position
    int failed    = _progress.failed;

    _emit(BatchValuationProgress(
      total: total, completed: completed, failed: failed,
      isRunning: true, isPaused: false,
    ));

    if (total == 0) {
      _running = false;
      _emit(BatchValuationProgress(
        total: snap.docs.length, completed: snap.docs.length,
        isRunning: false,
      ));
      return;
    }

    for (final doc in unvalued) {
      if (_pauseRequested) {
        _running = false;
        _emit(_progress.copyWith(isRunning: false, isPaused: true));
        return;
      }

      final data = doc.data();
      final year   = data['Year']?.toString()             ?? '';
      final denom  = data['Denomination']?.toString()     ?? '';
      final mint   = data['Mint Mark']?.toString()        ?? '';
      final cond   = data['Condition']?.toString()        ?? '';
      final series = data['Program/Series']?.toString()   ?? '';
      final metal  = data['Metal Content']?.toString()    ?? '';
      final country = data['Country']?.toString()         ?? 'USA';

      // Build human-readable coin name for the progress display
      final mintStr = mint.isNotEmpty && mint != 'None' ? '-$mint' : '';
      final coinName = [
        if (year.isNotEmpty) '$year$mintStr',
        if (denom.isNotEmpty) denom,
      ].join(' ');

      _emit(_progress.copyWith(
        total: total, isRunning: true, isPaused: false,
        currentCoinName: coinName.trim().isEmpty ? 'Unknown coin' : coinName,
      ));

      try {
        final result = await _callApi(
          year: year, denomination: denom, mintMark: mint,
          condition: cond, programSeries: series,
          metalContent: metal, country: country,
        );

        // Write result back to Firestore immediately
        await coinsRef.doc(doc.id).update({
          'AI Estimated Value': result['estimated_value'] ?? 'Pending',
          'ai_value_source':   'text_estimator',
          'ai_value_basis':    result['basis'] ?? '',
          'ai_value_confidence': result['confidence'] ?? 'LOW',
          'ai_needs_photo':    true,
        });
        completed++;
      } catch (e) {
        debugPrint('[BatchValuation] Error on ${doc.id}: $e');
        failed++;
      }

      _emit(BatchValuationProgress(
        total: total, completed: completed, failed: failed,
        isRunning: true, isPaused: false,
      ));

      // 2-second throttle between API calls
      await Future.delayed(const Duration(seconds: 2));
    }

    _running = false;
    _emit(BatchValuationProgress(
      total: total, completed: completed, failed: failed,
      isRunning: false, isPaused: false,
    ));
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

  void _emit(BatchValuationProgress p) {
    _progress = p;
    if (!_controller.isClosed) _controller.add(p);
  }

  void dispose() => _controller.close();
}
