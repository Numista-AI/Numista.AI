import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/utils/review_field_keys.dart';

void main() {
  group('ReviewFieldKeys.extractInitialReviewValues', () {
    test('populates all 18 fields from mixed PascalCase and snake_case keys', () {
      final data = <String, dynamic>{
        'year': '2021',
        'Denomination': 'Dollar',
        'mint_mark': 'W',
        'country': 'USA',
        'program_series': 'Morgan Dollar',
        'theme_subject': '100th Anniversary',
        'variety': 'VAM-1',
        'condition': 'MS-70',
        'strike_type': 'Uncirculated',
        'metal_content': '99.9% Silver',
        'Cost': 85.0,
        'allocated_fees': 9.95,
        'purchase_date': '2026-10-01',
        'retailer': 'US Mint',
        'invoice_number': 'INV-99',
        'retailer_item_num': '21XE',
        'storage_location': 'Safe 1',
        'qty': 2,
      };

      final values = ReviewFieldKeys.extractInitialReviewValues(data);
      expect(values.length, 18);
      expect(values['Year'], '2021');
      expect(values['Denomination'], 'Dollar');
      expect(values['Mint Mark'], 'W');
      expect(values['Country'], 'USA');
      expect(values['Program/Series'], 'Morgan Dollar');
      expect(values['Theme/Subject'], '100th Anniversary');
      expect(values['Variety'], 'VAM-1');
      expect(values['Condition'], 'MS-70');
      expect(values['Strike Type'], 'Uncirculated');
      expect(values['Metal Content'], '99.9% Silver');
      expect(values['Purchase Cost'], '85.0');
      expect(values['Fee'], '9.95');
      expect(values['Purchase Date'], '2026-10-01');
      expect(values['Retailer/Website'], 'US Mint');
      expect(values['Retailer Invoice #'], 'INV-99');
      expect(values['Retailer Item No.'], '21XE');
      expect(values['Storage Location'], 'Safe 1');
      expect(values['Quantity'], '2');
    });

    test('defaults Country to USA, Quantity to 1, Fee to empty, missing Cost to empty', () {
      final values = ReviewFieldKeys.extractInitialReviewValues({});
      expect(values['Country'], 'USA');
      expect(values['Quantity'], '1');
      expect(values['Fee'], '');
      expect(values['Purchase Cost'], '');
    });
  });

  group('ReviewFieldKeys.buildDirtyReviewQueueUpdates', () {
    test('returns empty map when no fields changed', () {
      final initial = ReviewFieldKeys.extractInitialReviewValues({
        'Year': '2021',
        'Condition': 'MS-65',
      });
      final current = Map<String, String>.from(initial);

      final updates = ReviewFieldKeys.buildDirtyReviewQueueUpdates(
        initialValues: initial,
        currentValues: current,
      );
      expect(updates, isEmpty);
    });

    test('single-field edit emits ONLY that field and its snake_case alias', () {
      final initial = ReviewFieldKeys.extractInitialReviewValues({
        'Year': '2021',
        'Condition': 'MS-63',
        'Denomination': 'Dollar',
      });
      final current = Map<String, String>.from(initial)
        ..['Condition'] = 'MS-65';

      final updates = ReviewFieldKeys.buildDirtyReviewQueueUpdates(
        initialValues: initial,
        currentValues: current,
      );
      expect(updates, {'Condition': 'MS-65', 'condition': 'MS-65'});
    });

    test('Purchase Cost edit syncs all 4 cost keys and clearing sets 0.0', () {
      final initial = ReviewFieldKeys.extractInitialReviewValues({
        'Cost': '10.00',
      });
      final edited = Map<String, String>.from(initial)
        ..['Purchase Cost'] = r'$25.50';

      final editUpdates = ReviewFieldKeys.buildDirtyReviewQueueUpdates(
        initialValues: initial,
        currentValues: edited,
      );
      expect(editUpdates, {
        'cost': 25.5,
        'Cost': 25.5,
        'Purchase Cost': 25.5,
        'cost_basis': 25.5,
      });

      final cleared = Map<String, String>.from(initial)
        ..['Purchase Cost'] = '';
      final clearUpdates = ReviewFieldKeys.buildDirtyReviewQueueUpdates(
        initialValues: initial,
        currentValues: cleared,
      );
      expect(clearUpdates, {
        'cost': 0.0,
        'Cost': 0.0,
        'Purchase Cost': 0.0,
        'cost_basis': 0.0,
      });
    });

    test('Fee clearing emits 0.0 for allocated_fees and shipping_fee', () {
      final initial = ReviewFieldKeys.extractInitialReviewValues({
        'allocated_fees': 9.95,
      });
      final cleared = Map<String, String>.from(initial)..['Fee'] = '';

      final updates = ReviewFieldKeys.buildDirtyReviewQueueUpdates(
        initialValues: initial,
        currentValues: cleared,
      );
      expect(updates, {'allocated_fees': 0.0, 'shipping_fee': 0.0});
    });

    test('Year+Mint auto-split applies when Mint Mark is empty', () {
      final initial = ReviewFieldKeys.extractInitialReviewValues({
        'Year': '2006',
        'Mint Mark': '',
      });
      final current = Map<String, String>.from(initial)..['Year'] = '2006d';

      final updates = ReviewFieldKeys.buildDirtyReviewQueueUpdates(
        initialValues: initial,
        currentValues: current,
      );
      expect(updates, {
        'Year': '2006',
        'year': '2006',
        'Mint Mark': 'D',
        'mint_mark': 'D',
      });
    });

    test('Retailer Item No. emits only retailer_item_num (no dotted key)', () {
      final initial = ReviewFieldKeys.extractInitialReviewValues({});
      final current = Map<String, String>.from(initial)
        ..['Retailer Item No.'] = 'AB.12';

      final updates = ReviewFieldKeys.buildDirtyReviewQueueUpdates(
        initialValues: initial,
        currentValues: current,
      );
      expect(updates, {'retailer_item_num': 'AB.12'});
      expect(updates.containsKey('Retailer Item No.'), isFalse);
    });
  });

  group('ReviewFieldKeys.validateDirtyReviewInputs', () {
    test('rejects invalid Purchase Cost, Fee, and Quantity', () {
      final initial = ReviewFieldKeys.extractInitialReviewValues({});

      expect(
        ReviewFieldKeys.validateDirtyReviewInputs(
          initialValues: initial,
          currentValues: Map<String, String>.from(initial)
            ..['Purchase Cost'] = 'abc',
        ),
        isNotNull,
      );

      expect(
        ReviewFieldKeys.validateDirtyReviewInputs(
          initialValues: initial,
          currentValues: Map<String, String>.from(initial)..['Fee'] = '-1',
        ),
        isNotNull,
      );

      expect(
        ReviewFieldKeys.validateDirtyReviewInputs(
          initialValues: initial,
          currentValues: Map<String, String>.from(initial)..['Quantity'] = '0',
        ),
        isNotNull,
      );

      expect(
        ReviewFieldKeys.validateDirtyReviewInputs(
          initialValues: initial,
          currentValues: Map<String, String>.from(initial)
            ..['Purchase Cost'] = r'$12.50'
            ..['Fee'] = '2.50'
            ..['Quantity'] = '3',
        ),
        isNull,
      );
    });
  });
}
