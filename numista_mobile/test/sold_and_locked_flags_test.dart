import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/models/coin_model.dart';
import 'package:numista_ai/utils/sold_item.dart';

void main() {
  test('Sold is keyed on status, never on transferStatus', () {
    expect(isSoldItem({'status': 'sold', 'transferStatus': 'pending'}), isTrue, reason: 'a Sold item in a buyer transfer stays Sold');
    expect(isSoldItem({'transferStatus': 'sold'}), isFalse);
    expect(isSoldItem({}), isFalse);
    expect(isSoldItem({'status': 'active'}), isFalse);
  });

  test('locked flag', () {
    expect(isLockedItem({'locked_pending_upgrade': true}), isTrue);
    expect(isLockedItem({'locked_pending_upgrade': false}), isFalse);
    expect(isLockedItem({}), isFalse);
  });

  test('CoinModel reads the flags but never writes them back', () {
    final coin = CoinModel.fromMap({'status': 'sold', 'locked_pending_upgrade': true, 'transferStatus': 'sold'}, 'c1');
    expect(coin.isSold, isTrue);
    expect(coin.isLocked, isTrue);
    final written = coin.toFirestore();
    expect(written.containsKey('locked_pending_upgrade'), isFalse);
    expect(written['status'], isNot('sold'));
  });

  test('a normal coin is neither sold nor locked', () {
    final coin = CoinModel.fromMap({'transferStatus': 'none'}, 'c2');
    expect(coin.isSold, isFalse);
    expect(coin.isLocked, isFalse);
  });
}