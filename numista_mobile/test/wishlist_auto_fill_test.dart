import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/models/coin_model.dart';
import 'package:numista_ai/models/program_model.dart';
import 'package:numista_ai/screens/wishlist_screen.dart';
import 'package:numista_ai/services/wishlist_service.dart';
import 'package:numista_ai/utils/program_goal_helper.dart';

void main() {
  final sampleProgram = CoinProgram(
    id: '50state',
    name: '50 State Quarters',
    url: '',
    years: '1999-2008',
    category: 'Quarter',
    mintMarkLocations: 'Reverse',
    coins: [
      ProgramCoin(
        id: 'delaware',
        name: 'Delaware',
        year: '1999',
        varieties: const [
          ChecklistVariety(id: 'P-UNC', label: 'P Unc'),
          ChecklistVariety(id: 'D-UNC', label: 'D Unc'),
          ChecklistVariety(id: 'S-CLAD', label: 'S Clad Proof'),
          ChecklistVariety(id: 'S-SILVER', label: 'S Silver Proof'),
        ],
      ),
      ProgramCoin(
        id: 'pennsylvania',
        name: 'Pennsylvania',
        year: '1999',
        varieties: const [
          ChecklistVariety(id: 'P-UNC', label: 'P Unc'),
          ChecklistVariety(id: 'D-UNC', label: 'D Unc'),
          ChecklistVariety(id: 'S-CLAD', label: 'S Clad Proof'),
        ],
      ),
    ],
  );

  group('ProgramGoalHelper & Wishlist Auto-Fill', () {
    test(
        'defaults to P & D Circulation Only and expands S Proofs under Full Master Set',
        () {
      final ownedDelawareP = [
        {
          'Year': '1999',
          'mint': 'Philadelphia',
          'mint_mark': 'P',
          'Denomination': 'Quarter',
          'Program/Series': '50 State Quarters',
          'Theme/Subject': 'Delaware',
        },
      ];

      final groupsPd = WishlistService.computeAutoMissingPrograms(
        allProgramsMap: {
          'Quarters': [sampleProgram]
        },
        expandedCoins: ownedDelawareP,
        programPreferences: const {},
        wishlistPrefs: const WishlistAutoFillPrefs(),
        userHash: 'abc123',
      );

      expect(groupsPd.length, 1);
      final slotKeysPd =
          groupsPd.first.missingSlots.map((s) => s.slotKey).toSet();
      expect(slotKeysPd, {
        '50state_delaware_D-UNC',
        '50state_pennsylvania_P-UNC',
        '50state_pennsylvania_D-UNC',
      });
      expect(slotKeysPd.contains('50state_delaware_S-CLAD'), isFalse);

      final groupsMaster = WishlistService.computeAutoMissingPrograms(
        allProgramsMap: {
          'Quarters': [sampleProgram]
        },
        expandedCoins: ownedDelawareP,
        programPreferences: const {},
        wishlistPrefs: const WishlistAutoFillPrefs(
          goalOverrides: {'50state': 'Full Master Set'},
        ),
        userHash: 'abc123',
      );
      final slotKeysMaster =
          groupsMaster.first.missingSlots.map((s) => s.slotKey).toSet();
      expect(slotKeysMaster.contains('50state_delaware_S-CLAD'), isTrue);
      expect(slotKeysMaster.contains('50state_delaware_S-SILVER'), isTrue);
      expect(
        ProgramGoalHelper.describeVarietyForSenior(
          const ChecklistVariety(id: 'P-UNC', label: 'P Unc'),
        ),
        'P Mint (Philadelphia)',
      );
    });

    test(
        'dismissed_slots permanently hides deleted slot and adding coin removes slot automatically',
        () {
      final owned = [
        {
          'Year': '1999',
          'mint': 'Philadelphia',
          'mint_mark': 'P',
          'Denomination': 'Quarter',
          'Program/Series': '50 State Quarters',
          'Theme/Subject': 'Delaware',
        },
      ];

      final afterDismiss = WishlistService.computeAutoMissingPrograms(
        allProgramsMap: {
          'Quarters': [sampleProgram]
        },
        expandedCoins: owned,
        programPreferences: const {},
        wishlistPrefs:
            const WishlistAutoFillPrefs(dismissedSlots: {'50state_delaware_D-UNC'}),
        userHash: 'abc123',
      );
      expect(
        afterDismiss.first.missingSlots
            .any((s) => s.slotKey == '50state_delaware_D-UNC'),
        isFalse,
      );

      final afterGotIt = WishlistService.computeAutoMissingPrograms(
        allProgramsMap: {
          'Quarters': [sampleProgram]
        },
        expandedCoins: [
          ...owned,
          {
            'Year': '1999',
            'mint': 'Denver',
            'mint_mark': 'D',
            'Denomination': 'Quarter',
            'Program/Series': '50 State Quarters',
            'Theme/Subject': 'Pennsylvania',
          },
        ],
        programPreferences: const {},
        wishlistPrefs: const WishlistAutoFillPrefs(),
        userHash: 'abc123',
      );
      expect(
        afterGotIt.first.missingSlots
            .any((s) => s.slotKey == '50state_pennsylvania_D-UNC'),
        isFalse,
      );
    });
  });

  group('WishlistScreen Senior Accessibility Widget Tests', () {
    testWidgets(
        'renders senior daylight UI >=18px text and >=56px ElevatedButton touch targets at 390x844',
        (tester) async {
      tester.view.physicalSize = const Size(390, 844);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      final sampleGroups = [
        AutoFilledProgramGroup(
          program: sampleProgram,
          effectiveGoal: ProgramGoalHelper.defaultAutoFillGoal,
          ownedCount: 1,
          targetCount: 4,
          hiddenSlotCount: 1,
          missingSlots: [
            MissingProgramSlot(
              slotKey: '50state_delaware_D-UNC',
              program: sampleProgram,
              coinSlot: sampleProgram.coins.first,
              variety: const ChecklistVariety(id: 'D-UNC', label: 'D Unc'),
              mintMark: 'D',
              varietyLabel: 'D Mint (Denver)',
              ebayQuery: '1999 D 50 State Quarters Delaware Uncirculated coin',
              ebayUrl:
                  'https://www.ebay.com/sch/i.html?_nkw=1999+D+Delaware&campid=5339148752&mkrid=711-53200-19255-0',
            ),
          ],
        ),
      ];

      final manualItems = [
        WishlistItem(
          id: 'wish_1',
          type: 'individual',
          coin: CoinModel(
            id: 'c1',
            year: '1921',
            mint: 'Philadelphia',
            mintMark: 'P',
            denomination: 'Dollar',
            themeSubject: 'Morgan Silver Dollar',
          ),
          timestamp: DateTime(2026, 11, 14),
        ),
      ];

      await tester.pumpWidget(
        MaterialApp(
          home: WishlistScreen(
            isGuestForTest: false,
            initialPrefsForTest: const WishlistAutoFillPrefs(
              dismissedSlots: {'50state_pennsylvania_P-UNC'},
              lastRecipientEmail: 'eric@example.com',
              savedRecipientEmails: ['eric@example.com'],
            ),
            initialAutoGroupsForTest: sampleGroups,
            initialManualItemsForTest: manualItems,
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Send My Wish List to Family'), findsOneWidget);
      expect(find.text('50 State Quarters'), findsOneWidget);
      expect(find.text('D Mint (Denver)'), findsOneWidget);
      expect(find.text('Restore Hidden Coins / Programs'), findsOneWidget);

      for (final text in tester.widgetList<Text>(find.byType(Text))) {
        expect((text.style?.fontSize ?? 18.0) >= 18.0, isTrue);
      }
      for (final btn
          in tester.widgetList<ElevatedButton>(find.byType(ElevatedButton))) {
        expect(tester.getSize(find.byWidget(btn)).height >= 56.0, isTrue);
      }
    });
  });
}
