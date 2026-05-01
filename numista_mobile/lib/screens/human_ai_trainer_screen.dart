import 'package:flutter/material.dart';

/// Human AI Trainer Review Board
/// Full implementation in Session 3. Placeholder screen for navigation wiring.
class HumanAiTrainerScreen extends StatelessWidget {
  const HumanAiTrainerScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.how_to_vote_outlined, size: 64, color: Color(0xFF1565C0)),
          SizedBox(height: 20),
          Text(
            'Human AI Trainer Review Board',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
          ),
          SizedBox(height: 12),
          Text(
            'Help improve Numista.AI by reviewing coin grades,\nvalues, and identifications assigned by the AI.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 15, color: Color(0xFF64748B), height: 1.5),
          ),
          SizedBox(height: 32),
          Text(
            'Coming in Session 3 — Community HITL implementation',
            style: TextStyle(fontSize: 12, color: Color(0xFF94A3B8)),
          ),
        ],
      ),
    );
  }
}
