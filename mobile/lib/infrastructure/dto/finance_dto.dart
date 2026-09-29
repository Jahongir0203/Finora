/// JSON → domain models for the finance endpoints (docs/backend/openapi.json).
library;

import 'package:finora/domain/models/finance/finance_models.dart';

typedef Json = Map<String, dynamic>;

/// `#10B981` → `0xFF10B981`.
int colorFromHex(String? hex, {int fallback = 0xFF94A3B8}) {
  final v = int.tryParse((hex ?? '').replaceFirst('#', ''), radix: 16);
  return v == null ? fallback : 0xFF000000 | v;
}

/// `0xFF10B981` → `#10B981`.
String colorToHex(int color) =>
    '#${(color & 0xFFFFFF).toRadixString(16).padLeft(6, '0').toUpperCase()}';

/// `2026-09-29`.
String dateToJson(DateTime d) =>
    '${d.year.toString().padLeft(4, '0')}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';

/// `YYYY-MM-DD` as a local calendar date.
DateTime dateFromJson(String s) {
  final d = DateTime.parse(s);
  return DateTime(d.year, d.month, d.day);
}

Category categoryFromJson(Json j) => Category(
  id: j['id'],
  name: j['name'],
  icon: j['icon'],
  color: colorFromHex(j['color']),
  isIncome: j['type'] == 'income',
  limit: j['monthly_limit'],
);

/// Signed amount: income positive, expense (and outgoing transfer) negative.
num signedAmount(Json j) {
  final amount = j['amount'] as num;
  return switch (j['type']) {
    'income' => amount,
    'transfer' => j['direction'] == 'in' ? amount : -amount,
    _ => -amount,
  };
}

Transaction transactionFromJson(Json j, {String fallbackTitle = ''}) =>
    Transaction(
      id: j['id'],
      title: (j['title'] as String?)?.isNotEmpty == true
          ? j['title']
          : fallbackTitle,
      categoryId: j['category_id'],
      amount: signedAmount(j),
      date: DateTime.parse(j['occurred_at']).toLocal(),
    );

Goal goalFromJson(Json j) {
  final deadline = j['deadline'] as String?;
  final created = DateTime.parse(j['created_at']).toLocal();
  return Goal(
    id: j['id'],
    name: j['name'],
    icon: j['icon'],
    saved: j['saved'],
    target: j['target'],
    // No deadline: show the ETA month, or a year from creation.
    due: deadline != null
        ? dateFromJson(deadline)
        : _etaMonth(j['plan']?['eta_months'], created),
    autoSave: j['auto_save_monthly'],
  );
}

DateTime _etaMonth(int? months, DateTime created) {
  final now = DateTime.now();
  return months == null
      ? DateTime(created.year + 1, created.month)
      : DateTime(now.year, now.month + months);
}

GoalEntry goalEntryFromJson(Json j) => GoalEntry(
  j['kind'] == 'withdraw' ? -(j['amount'] as num) : j['amount'] as num,
  DateTime.parse(j['created_at']).toLocal(),
);

const _repeats = {
  'once': ReminderRepeat.once,
  'weekly': ReminderRepeat.weekly,
  'monthly': ReminderRepeat.monthly,
  'yearly': ReminderRepeat.yearly,
};

Reminder reminderFromJson(Json j) => Reminder(
  id: j['id'],
  title: j['title'],
  categoryId: j['category_id'],
  amount: j['amount'],
  dueDate: dateFromJson(j['next_due_date']),
  repeat: _repeats[j['repeat']] ?? ReminderRepeat.monthly,
  enabled: j['enabled'] ?? true,
);

String reminderRepeatToJson(ReminderRepeat r) => r.name;

/// Card colors when the server has none.
const _accountColors = [0xFF064E3B, 0xFF1E293B, 0xFF4C1D95];
const _cashColor = 0xFFB45309;

Account accountFromJson(Json j, int index) {
  final isCash = j['type'] == 'cash';
  return Account(
    id: j['id'],
    bank: (j['bank_name'] as String?) ?? j['name'],
    network: isCash ? null : j['network'],
    last4: j['last4'],
    expiry: j['expiry'],
    balance: j['balance'],
    color: colorFromHex(
      j['color'],
      fallback: isCash
          ? _cashColor
          : _accountColors[index % _accountColors.length],
    ),
    monthlyLimit: j['monthly_limit'],
    frozen: j['frozen'] ?? false,
    isMain: j['is_default'] ?? false,
  );
}
