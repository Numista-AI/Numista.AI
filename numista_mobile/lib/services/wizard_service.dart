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
        "Hi there! I'm your personal guide — think of me as someone sitting "
        "right next to you. You have 100 real coins already loaded and ready "
        "to explore. I'll walk you through everything, one step at a time. "
        "Tap 'Let's Start' whenever you're ready — there's no rush!",
    buttonLabel: "Let's Start →",
  ),
  WizardStep(
    id: 'collection',
    title: "Your Coin Collection 🪙",
    message:
        "This is where all your coins live. I've loaded 100 coins for you — "
        "Silver Eagles, Mercury Dimes, Morgan Dollars, State Quarters, and "
        "more. See those green dollar amounts next to each coin? Numista.AI's "
        "AI estimated the value of every single one automatically. Pretty "
        "handy, right?",
    buttonLabel: "Show Me My Collection →",
    targetRoute: 'My Collection',
    autoNavigate: true,
  ),
  WizardStep(
    id: 'programs',
    title: "Coin Programs & Sets 🏅",
    message:
        "Notice the 50 State Quarters and the brand-new 2026 "
        "Semiquincentennial coins in your collection? This screen tracks "
        "complete coin sets — it shows you which coins you already have "
        "and which ones you're still looking for. Great for collectors who "
        "love completing a series!",
    buttonLabel: "Explore Coin Programs →",
    targetRoute: 'Coin Programs',
    autoNavigate: true,
  ),
  WizardStep(
    id: 'wishlist',
    title: "My Wishlist & eBay Tracking 💛",
    message:
        "See a coin you'd love to own someday? Add it to your Wishlist. "
        "Numista.AI will search eBay for matching listings in real time and "
        "show you what they're selling for — so you know exactly what to "
        "look for and what a fair price looks like. No more guessing!",
    buttonLabel: "See My Wishlist →",
    targetRoute: 'My Wishlist',
    autoNavigate: true,
  ),
  WizardStep(
    id: 'add_coins',
    title: "Adding Your Own Coins 📤",
    message:
        "Ready to try adding a coin? You have four options: type one in by "
        "hand, upload a photo, import a spreadsheet, or scan with our "
        "microscope attachment. Any coin you add here gets reviewed by our "
        "volunteer community — real people who help make the AI smarter for "
        "everyone!",
    buttonLabel: "Try Adding a Coin →",
    targetRoute: 'Add New Coins',
    autoNavigate: true,
  ),
  WizardStep(
    id: 'complete',
    title: "You're All Set! 🎉",
    message:
        "Great job! You've seen the highlights of Numista.AI. Feel free to "
        "keep exploring your demo collection at your own pace. And when "
        "you're ready to track your real coins, just create a free account "
        "— everything you've done in this session comes along with you. "
        "Nothing gets lost!",
    buttonLabel: "Create My Free Account →",
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
