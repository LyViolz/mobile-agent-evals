enum RestoreState { active, expired, awaitingSync }

/// Store entitlement is authoritative; the app ledger may be stale.
RestoreState restoreState({
  required bool storeHasEntitlement,
  required bool ledgerHasPremium,
}) {
  if (ledgerHasPremium) return RestoreState.active;
  if (storeHasEntitlement) return RestoreState.awaitingSync;
  return RestoreState.expired;
}
