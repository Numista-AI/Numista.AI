"""
test_division.py — Unit tests for the Smart Division partitioning engine.
"""

import unittest
import time
import random
from estate_report_generator import partition_collection_equitably

class TestSmartDivision(unittest.TestCase):

    def setUp(self):
        # Setup common test beneficiaries
        self.heirs = [
            {'id': 'heir_a', 'name': 'Alice'},
            {'id': 'heir_b', 'name': 'Bob'},
            {'id': 'heir_c', 'name': 'Charlie'}
        ]

    def test_basic_greedy_partition(self):
        """Verify that basic greedy partition divides coins equitably."""
        # Simple coins: 100, 80, 50, 40, 30
        coins = [
            {'_doc_id': 'c1', '_fmv': 100.0},
            {'_doc_id': 'c2', '_fmv': 80.0},
            {'_doc_id': 'c3', '_fmv': 50.0},
            {'_doc_id': 'c4', '_fmv': 40.0},
            {'_doc_id': 'c5', '_fmv': 30.0},
        ]
        estate_overrides = {}
        
        # We partition among Alice and Bob (2 heirs)
        heirs_two = self.heirs[:2]
        result = partition_collection_equitably(coins, estate_overrides, heirs_two)
        
        lots = result['heir_lots']
        totals = result['heir_totals']
        
        # Alice and Bob should receive assignments
        self.assertIn('heir_a', lots)
        self.assertIn('heir_b', lots)
        
        # Verify all coins are assigned exactly once
        all_assigned = [c['_doc_id'] for lot in lots.values() for c in lot]
        self.assertEqual(len(all_assigned), 5)
        self.assertEqual(set(all_assigned), {'c1', 'c2', 'c3', 'c4', 'c5'})
        
        # LPT allocation trace:
        # Coins sorted descending: c1(100), c2(80), c3(50), c4(40), c5(30)
        # 1. c1(100) -> heir_a (Totals: A=100, B=0)
        # 2. c2(80) -> heir_b (Totals: A=100, B=80)
        # 3. c3(50) -> heir_b (Totals: A=100, B=130)
        # 4. c4(40) -> heir_a (Totals: A=140, B=130)
        # 5. c5(30) -> heir_b (Totals: A=140, B=160)
        # Let's verify if greedy result matches:
        self.assertEqual(totals['heir_a'], 140.0)
        self.assertEqual(totals['heir_b'], 160.0)

    def test_locked_overrides(self):
        """Verify that locked assignments are respected first, and remaining are partitioned greedily."""
        coins = [
            {'_doc_id': 'c1', '_fmv': 100.0},
            {'_doc_id': 'c2', '_fmv': 80.0},
            {'_doc_id': 'c3', '_fmv': 50.0},
            {'_doc_id': 'c4', '_fmv': 40.0},
            {'_doc_id': 'c5', '_fmv': 30.0},
        ]
        # Lock c5 (30.0) to heir_a
        estate_overrides = {
            'c5': {'assignedHeirId': 'heir_a', 'divisionLocked': True}
        }
        
        heirs_two = self.heirs[:2]
        result = partition_collection_equitably(coins, estate_overrides, heirs_two)
        
        lots = result['heir_lots']
        totals = result['heir_totals']
        
        # Verify c5 is in Alice's lot
        alice_coin_ids = [c['_doc_id'] for c in lots['heir_a']]
        self.assertIn('c5', alice_coin_ids)
        
        # Verify the lock flag is attached to c5 in the output
        c5_in_lot = next(c for c in lots['heir_a'] if c['_doc_id'] == 'c5')
        self.assertTrue(c5_in_lot.get('_division_locked'))
        self.assertEqual(c5_in_lot.get('_assigned_heir_id'), 'heir_a')

        # Run allocation:
        # Preallocated: Alice has c5(30). Totals: A=30, B=0
        # Unlocked sorted descending: c1(100), c2(80), c3(50), c4(40)
        # 1. c1(100) -> heir_b (Totals: A=30, B=100)
        # 2. c2(80) -> heir_a (Totals: A=110, B=100)
        # 3. c3(50) -> heir_b (Totals: A=110, B=150)
        # 4. c4(40) -> heir_a (Totals: A=150, B=150)
        # Let's verify final balanced totals are exactly: A=150, B=150
        self.assertEqual(totals['heir_a'], 150.0)
        self.assertEqual(totals['heir_b'], 150.0)

    def test_unvalued_or_excluded_coins(self):
        """Verify coins with no fmv or marked excluded are handled safely."""
        coins = [
            {'_doc_id': 'c1', '_fmv': 100.0},
            {'_doc_id': 'c2', '_fmv': 0.0},
            {'_doc_id': 'c3', '_fmv': None},
            {'_doc_id': 'c4', '_fmv': 50.0, 'excludeFromReport': True},
        ]
        estate_overrides = {}
        
        heirs_two = self.heirs[:2]
        result = partition_collection_equitably(coins, estate_overrides, heirs_two)
        
        lots = result['heir_lots']
        unassigned = result['unassigned']
        
        # c1 should be assigned.
        # c2 (0.0), c3 (None) should go to unassigned (no value)
        # c4 (excluded) should be skipped entirely
        all_assigned = [c['_doc_id'] for lot in lots.values() for c in lot]
        self.assertEqual(all_assigned, ['c1'])
        
        unassigned_ids = [c['_doc_id'] for c in unassigned]
        self.assertIn('c2', unassigned_ids)
        self.assertIn('c3', unassigned_ids)
        self.assertNotIn('c4', unassigned_ids)

    def test_large_collection_scale_and_performance(self):
        """Verify performance and lot balance scaling for up to 2000 coins."""
        # Generate 2000 mock coins with values between $1 and $500
        random.seed(42)
        coins = []
        for i in range(2000):
            val = round(random.uniform(1.0, 500.0), 2)
            coins.append({
                '_doc_id': f'coin_{i}',
                '_fmv': val,
                'Year': str(random.randint(1800, 2026)),
                'Denomination': 'Cent'
            })
            
        # Lock 10 high-value coins randomly to test locked + large load scaling
        estate_overrides = {}
        for i in range(10):
            coin_idx = random.randint(0, 1999)
            heir_id = random.choice(['heir_a', 'heir_b', 'heir_c'])
            estate_overrides[f'coin_{coin_idx}'] = {
                'assignedHeirId': heir_id,
                'divisionLocked': True
            }

        start_time = time.perf_counter()
        result = partition_collection_equitably(coins, estate_overrides, self.heirs)
        end_time = time.perf_counter()
        
        duration_ms = (end_time - start_time) * 1000
        
        # Verify execution is lightning fast (< 50ms)
        self.assertLess(duration_ms, 50.0, f"Partition took too long: {duration_ms:.2f}ms")
        
        lots = result['heir_lots']
        totals = result['heir_totals']
        
        # Verify all coins (except unassigned) are distributed
        total_assigned_count = sum(len(lot) for lot in lots.values())
        self.assertEqual(total_assigned_count, 2000)
        
        # Verify variance is extremely low for a large randomized sample
        avg_value = sum(totals.values()) / len(self.heirs)
        for hid, total in totals.items():
            pct_diff = abs(total - avg_value) / avg_value * 100
            # With 2000 coins, greedy LPT should balance lots to well under 1% variance
            self.assertLess(pct_diff, 1.0, f"Heir {hid} lot variance {pct_diff:.2f}% exceeds 1%")

if __name__ == '__main__':
    unittest.main()
