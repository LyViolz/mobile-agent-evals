import 'package:entitlement_fixture/restore_state.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('stale ledger does not restore an expired store entitlement', () {
    expect(restoreState(storeHasEntitlement: false, ledgerHasPremium: true), RestoreState.expired);
  });
  test('active store entitlement waits for ledger sync', () {
    expect(restoreState(storeHasEntitlement: true, ledgerHasPremium: false), RestoreState.awaitingSync);
  });
  test('matching active sources restore access', () {
    expect(restoreState(storeHasEntitlement: true, ledgerHasPremium: true), RestoreState.active);
  });
  test('matching inactive sources remain expired', () {
    expect(restoreState(storeHasEntitlement: false, ledgerHasPremium: false), RestoreState.expired);
  });
}
