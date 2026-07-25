import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

// ─── Step Model ───────────────────────────────────────────────────────────────
// A single step in any wizard track. Keep it data-only so tracks are easy
// to define as plain const lists and re-use across the app.

class WizardStep {
  final String id;
  final String title;

  /// The over-the-shoulder guidance message. Write it like you're standing
  /// next to someone who's smart but new to the software.
  final String message;

  /// Label on the primary action button.
  final String buttonLabel;

  /// If set, the app's main content area switches to this route when the
  /// step is shown (so the user doesn't have to find it themselves).
  final String? targetRoute;

  /// Whether to automatically navigate when the step is shown.
  final bool autoNavigate;

  const WizardStep({
    required this.id,
    required this.title,
    required this.message,
    required this.buttonLabel,
    this.targetRoute,
    this.autoNavigate = false,
  });
}

// ─── State Snapshot ───────────────────────────────────────────────────────────

class WizardState {
  final int stepIndex;
  final int totalSteps;
  final WizardStep step;
  final bool isLastStep;
  final String trackId;

  const WizardState({
    required this.stepIndex,
    required this.totalSteps,
    required this.step,
    required this.isLastStep,
    required this.trackId,
  });
}

// ─── Step Definitions ─────────────────────────────────────────────────────────
// Written in a warm, conversational, non-condescending tone.
// Think: standing over your aunt's shoulder, gently saying "Now look at this…"

const List<WizardStep> _guestSteps = [
  WizardStep(
    id: 'welcome',
    title: "Welcome to Numista.AI! 👋",
    message:
        "Hi there! I'm your personal guide. You have 100 demo items already loaded "
        "and ready to explore across Coins, Currency, and World items. "
        "Tap 'Let's Start' whenever you're ready — there's no rush!",
    buttonLabel: "Let's Start →",
  ),
  WizardStep(
    id: 'collection',
    title: "Your Collection & AI Values 🪙",
    message:
        "This is your collection dashboard. I've pre-loaded 100 items for you — "
        "Silver Eagles, Morgans, Lincoln Cents, Banknotes, and World Gold. "
        "Notice the green values next to each coin? Numista.AI estimated the "
        "value of every single one automatically!",
    buttonLabel: "Show Me My Collection →",
    targetRoute: 'My Collection',
    autoNavigate: true,
  ),
  WizardStep(
    id: 'programs',
    title: "Coin Programs & Checklists 🏅",
    message:
        "Notice the 50 State Quarters and 2026 Semiquincentennial coins? "
        "This screen tracks complete coin sets — showing what you have and "
        "what you're still looking for. Perfect for completing a series!",
    buttonLabel: "Explore Coin Programs →",
    targetRoute: 'Coin Programs',
    autoNavigate: true,
  ),
  WizardStep(
    id: 'add_coins',
    title: "Add Coins Hub & 7 Entry Methods 📤",
    message:
        "Ready to add your own coins? Numista.AI offers 7 powerful entry methods: "
        "Quick Camera, Upload Files/PDFs, Manual Entry, Add by SKU, PCGS/NGC Cert Lookup, "
        "Roll/Batch Entry, and World/Mint Sets!",
    buttonLabel: "Explore Add Coins →",
    targetRoute: 'Add New Coins',
    autoNavigate: true,
  ),
  WizardStep(
    id: 'complete',
    title: "Wishlist & You're All Set! 🎉",
    message:
        "Track wanted items on your Wishlist with real-time eBay pricing. "
        "Feel free to explore your demo collection. When you're ready to track "
        "your real collection, create a free account — your progress comes with you!",
    buttonLabel: "Start Exploring →",
    targetRoute: 'My Wishlist',
    autoNavigate: true,
  ),
];

// ─── Service ──────────────────────────────────────────────────────────────────

class WizardService {
  WizardService._(); // private — use static API only

  // Extend here when adding new wizard tracks to other parts of the app.
  static const Map<String, List<WizardStep>> _tracks = {
    'guest': _guestSteps,
  };

  // Reactive state — the overlay listens to this notifier.
  static final ValueNotifier<WizardState?> state = ValueNotifier(null);

  static int _stepIndex = 0;
  static String _trackId = 'guest';

  // Callback supplied by BaseLayout so the wizard can navigate the main view.
  static Function(String route)? _onNavigate;

  // ── Public API ─────────────────────────────────────────────────────────────

  /// Start a wizard track. [onNavigate] lets the wizard switch the main
  /// content area without the user having to find the nav item themselves.
  static Future<void> start(
    String trackId, {
    Function(String route)? onNavigate,
  }) async {
    final steps = _tracks[trackId];
    if (steps == null || steps.isEmpty) return;

    _trackId = trackId;
    _onNavigate = onNavigate;

    final prefs = await SharedPreferences.getInstance();
    _stepIndex = prefs.getInt('wizard_${trackId}_step') ?? 0;

    // Already completed — don't re-show.
    if (_stepIndex >= steps.length) return;

    _emit();
  }

  /// Register (or update) the navigation callback after the widget mounts.
  static void setNavigateCallback(Function(String route) callback) {
    _onNavigate = callback;
  }

  /// Advance one step. Navigates the content area if the step requests it.
  static Future<void> nextStep() async {
    final steps = _tracks[_trackId] ?? [];
    if (_stepIndex >= steps.length - 1) {
      await dismiss(completed: true);
      return;
    }
    _stepIndex++;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt('wizard_${_trackId}_step', _stepIndex);

    final step = steps[_stepIndex];
    if (step.autoNavigate && step.targetRoute != null) {
      _onNavigate?.call(step.targetRoute!);
    }
    _emit();
  }

  /// Dismiss the wizard. Pass [completed: true] to mark it done permanently.
  static Future<void> dismiss({bool completed = false}) async {
    if (completed) {
      final steps = _tracks[_trackId] ?? [];
      final prefs = await SharedPreferences.getInstance();
      await prefs.setInt('wizard_${_trackId}_step', steps.length);
    }
    state.value = null;
  }

  /// Reset the wizard so it shows from the beginning next time (dev/testing).
  static Future<void> reset(String trackId) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('wizard_${trackId}_step');
    state.value = null;
  }

  /// The route the current step wants highlighted in the nav, if any.
  static String? get highlightedRoute => state.value?.step.targetRoute;

  static bool get isActive => state.value != null;

  // ── Internal ───────────────────────────────────────────────────────────────

  static void _emit() {
    final steps = _tracks[_trackId] ?? [];
    if (_stepIndex >= steps.length) return;
    state.value = WizardState(
      stepIndex: _stepIndex,
      totalSteps: steps.length,
      step: steps[_stepIndex],
      isLastStep: _stepIndex == steps.length - 1,
      trackId: _trackId,
    );
  }
}
