import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/material.dart';
import '../services/beta_checklist_service.dart';

class BetaChecklistWidget extends StatelessWidget {
  const BetaChecklistWidget({super.key});

  static void showChecklistModal(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) {
        return const BetaChecklistModal();
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<DocumentSnapshot<Map<String, dynamic>>>(
      stream: BetaChecklistService.getChecklistStream(),
      builder: (context, snapshot) {
        int completedCount = 0;
        int skippedCount = 0;

        if (snapshot.hasData && snapshot.data!.exists) {
          final data = snapshot.data!.data();
          if (data != null) {
            completedCount = (data['completed_tasks'] as List?)?.length ?? 0;
            skippedCount = (data['skipped_tasks'] as List?)?.length ?? 0;
          }
        }

        final totalDone = completedCount + skippedCount;
        final totalTasks = BetaChecklistService.allTasks.length;
        final progressPct = (totalDone / totalTasks * 100).toInt();

        return OutlinedButton.icon(
          style: OutlinedButton.styleFrom(
            foregroundColor: Colors.blueAccent,
            side: BorderSide(
              color: progressPct == 100 ? Colors.green : Colors.blueAccent,
            ),
            backgroundColor: progressPct == 100
                ? Colors.green.withValues(alpha: 0.1)
                : Colors.blueAccent.withValues(alpha: 0.05),
          ),
          icon: Icon(
            progressPct == 100 ? Icons.stars : Icons.checklist_rtl,
            color: progressPct == 100 ? Colors.green : Colors.blueAccent,
            size: 18,
          ),
          label: Text(
            'Beta Checklist ($totalDone/$totalTasks — $progressPct%)',
            style: TextStyle(
              color: progressPct == 100 ? Colors.green : Colors.blueAccent,
              fontWeight: FontWeight.bold,
              fontSize: 13,
            ),
          ),
          onPressed: () => showChecklistModal(context),
        );
      },
    );
  }
}

class BetaChecklistModal extends StatelessWidget {
  const BetaChecklistModal({super.key});

  @override
  Widget build(BuildContext context) {
    final mediaQuery = MediaQuery.of(context);

    return Container(
      margin: EdgeInsets.only(
        top: 60,
        left: 16,
        right: 16,
        bottom: mediaQuery.viewInsets.bottom + 16,
      ),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.blueAccent.withValues(alpha: 0.3)),
        boxShadow: const [
          BoxShadow(
            color: Colors.black54,
            blurRadius: 20,
            offset: Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.blueAccent.withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Icon(Icons.playlist_add_check_circle,
                        color: Colors.blueAccent, size: 24),
                  ),
                  const SizedBox(width: 12),
                  Text(
                    '20-Point Beta Checklist',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                ],
              ),
              IconButton(
                icon: const Icon(Icons.close, color: Colors.grey),
                onPressed: () => Navigator.of(context).pop(),
              ),
            ],
          ),
          const SizedBox(height: 16),

          // Streamed Progress Bar
          StreamBuilder<DocumentSnapshot<Map<String, dynamic>>>(
            stream: BetaChecklistService.getChecklistStream(),
            builder: (context, snapshot) {
              List<String> completedTasks = [];
              List<String> skippedTasks = [];

              if (snapshot.hasData && snapshot.data!.exists) {
                final data = snapshot.data!.data();
                if (data != null) {
                  completedTasks =
                      List<String>.from(data['completed_tasks'] ?? []);
                  skippedTasks =
                      List<String>.from(data['skipped_tasks'] ?? []);
                }
              }

              final totalDone = completedTasks.length + skippedTasks.length;
              final totalTasks = BetaChecklistService.allTasks.length;
              final double progressRatio = (totalDone / totalTasks).clamp(0.0, 1.0);

              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Progress: $totalDone / $totalTasks Tasks (${(progressRatio * 100).toInt()}%)',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 14,
                        ),
                      ),
                      if (progressRatio == 1.0)
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: Colors.green.withValues(alpha: 0.2),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: const Text(
                            '🎉 100% Complete!',
                            style: TextStyle(
                              color: Colors.green,
                              fontWeight: FontWeight.bold,
                              fontSize: 12,
                            ),
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(6),
                    child: LinearProgressIndicator(
                      value: progressRatio,
                      minHeight: 10,
                      backgroundColor: Colors.white10,
                      valueColor: AlwaysStoppedAnimation<Color>(
                        progressRatio == 1.0
                            ? Colors.green
                            : Colors.blueAccent,
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Tasks List
                  SizedBox(
                    height: mediaQuery.size.height * 0.55,
                    child: ListView.separated(
                      itemCount: BetaChecklistService.allTasks.length,
                      separatorBuilder: (_, __) => const Divider(
                          color: Colors.white12, height: 1),
                      itemBuilder: (context, index) {
                        final task = BetaChecklistService.allTasks[index];
                        final isDone = completedTasks.contains(task.id);
                        final isSkipped = skippedTasks.contains(task.id);

                        return Container(
                          padding: const EdgeInsets.symmetric(
                              vertical: 8, horizontal: 4),
                          child: Row(
                            children: [
                              // Checkbox
                              Checkbox(
                                activeColor: Colors.blueAccent,
                                value: isDone,
                                onChanged: (val) {
                                  BetaChecklistService.toggleTaskCompleted(
                                      task.id, val ?? false);
                                },
                              ),
                              const SizedBox(width: 8),

                              // Text details
                              Expanded(
                                child: Column(
                                  crossAxisAlignment:
                                      CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      children: [
                                        Expanded(
                                          child: Text(
                                            task.title,
                                            style: TextStyle(
                                              color: isDone
                                                  ? Colors.grey
                                                  : Colors.white,
                                              fontWeight: FontWeight.w600,
                                              decoration: isDone
                                                  ? TextDecoration.lineThrough
                                                  : null,
                                            ),
                                          ),
                                        ),
                                        if (task.isAutoDetectable)
                                          Container(
                                            margin: const EdgeInsets.only(
                                                left: 6),
                                            padding:
                                                const EdgeInsets.symmetric(
                                                    horizontal: 6, vertical: 2),
                                            decoration: BoxDecoration(
                                              color: Colors.blue.withValues(
                                                  alpha: 0.15),
                                              borderRadius:
                                                  BorderRadius.circular(4),
                                            ),
                                            child: const Text(
                                              'Auto',
                                              style: TextStyle(
                                                  color: Colors.lightBlueAccent,
                                                  fontSize: 10),
                                            ),
                                          ),
                                      ],
                                    ),
                                    const SizedBox(height: 2),
                                    Text(
                                      task.description,
                                      style: TextStyle(
                                        color: Colors.grey.shade400,
                                        fontSize: 12,
                                      ),
                                    ),
                                  ],
                                ),
                              ),

                              // N/A Skip option for hardware tasks
                              if (task.supportsSkip)
                                TextButton(
                                  style: TextButton.styleFrom(
                                    padding: const EdgeInsets.symmetric(
                                        horizontal: 8),
                                    minimumSize: Size.zero,
                                    tapTargetSize:
                                        MaterialTapTargetSize.shrinkWrap,
                                  ),
                                  onPressed: () {
                                    BetaChecklistService.toggleTaskSkipped(
                                        task.id, !isSkipped);
                                  },
                                  child: Text(
                                    isSkipped ? 'Skipped (N/A)' : 'N/A Skip',
                                    style: TextStyle(
                                      color: isSkipped
                                          ? Colors.orange
                                          : Colors.grey,
                                      fontSize: 11,
                                      fontWeight: isSkipped
                                          ? FontWeight.bold
                                          : FontWeight.normal,
                                    ),
                                  ),
                                ),
                            ],
                          ),
                        );
                      },
                    ),
                  ),
                ],
              );
            },
          ),
        ],
      ),
    );
  }
}
