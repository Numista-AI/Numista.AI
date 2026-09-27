import 'package:flutter_test/flutter_test.dart';

void main() {
  group('TC-8: Lateral Transfer Sale Financials & Quantity Math', () {
    double parseUnitCost(String costStr) {
      final cleaned = costStr.replaceAll(RegExp(r'[^\d.]'), '');
      return double.tryParse(cleaned) ?? 0.0;
    }

    Map<String, dynamic> calculateSaleFinancials({
      required String unitCostStr,
      required int qtyAvailable,
      required int qtySold,
      required double grossSalePrice,
      required double fees,
    }) {
      expect(qtySold, greaterThanOrEqualTo(1));
      expect(qtySold, lessThanOrEqualTo(qtyAvailable));

      final unitCostNum = parseUnitCost(unitCostStr);
      final unitCostCents = (unitCostNum * 100).round();
      final allocatedCostBasisCents = unitCostCents * qtySold;

      final salePriceCents = (grossSalePrice * 100).round();
      final feesCents = (fees * 100).round();
      final netProceedsCents = salePriceCents - feesCents;
      final realizedProfitCents = netProceedsCents - allocatedCostBasisCents;

      final remainingQty = qtyAvailable - qtySold;

      return {
        'unit_cost_cents': unitCostCents,
        'allocated_cost_basis_cents': allocatedCostBasisCents,
        'allocated_cost_basis_usd': allocatedCostBasisCents / 100.0,
        'sale_price_cents': salePriceCents,
        'fees_cents': feesCents,
        'net_proceeds_cents': netProceedsCents,
        'net_proceeds_usd': netProceedsCents / 100.0,
        'realized_profit_cents': realizedProfitCents,
        'realized_profit_usd': realizedProfitCents / 100.0,
        'remaining_qty': remainingQty,
      };
    }

    test('TC-8a: 2026 Morgan 26XE sell 1 of 2 at \$250 with \$15 fees (Eric case)', () {
      final res = calculateSaleFinancials(
        unitCostStr: '\$169.00',
        qtyAvailable: 2,
        qtySold: 1,
        grossSalePrice: 250.00,
        fees: 15.00,
      );

      expect(res['remaining_qty'], equals(1));
      expect(res['allocated_cost_basis_usd'], equals(169.00));
      expect(res['net_proceeds_usd'], equals(235.00));
      expect(res['realized_profit_usd'], equals(66.00));
      expect(res['realized_profit_cents'], equals(6600));
    });

    test('TC-8b: Zero floating-point rounding drift with odd cents', () {
      final res = calculateSaleFinancials(
        unitCostStr: '\$33.33',
        qtyAvailable: 3,
        qtySold: 2,
        grossSalePrice: 100.00,
        fees: 8.55,
      );

      expect(res['remaining_qty'], equals(1));
      expect(res['unit_cost_cents'], equals(3333));
      expect(res['allocated_cost_basis_cents'], equals(6666));
      expect(res['sale_price_cents'], equals(10000));
      expect(res['fees_cents'], equals(855));
      expect(res['net_proceeds_cents'], equals(9145));
      expect(res['realized_profit_cents'], equals(2479));
      expect(res['realized_profit_usd'], equals(24.79));
    });

    test('TC-8c: Full sale decrements quantity to 0', () {
      final res = calculateSaleFinancials(
        unitCostStr: '\$169.00',
        qtyAvailable: 2,
        qtySold: 2,
        grossSalePrice: 500.00,
        fees: 30.00,
      );

      expect(res['remaining_qty'], equals(0));
      expect(res['allocated_cost_basis_usd'], equals(338.00));
      expect(res['net_proceeds_usd'], equals(470.00));
      expect(res['realized_profit_usd'], equals(132.00));
    });
  });
}
