import 'dart:async';

import 'package:finora/domain/facades/finance_facade.dart';
import 'package:finora/domain/models/finance/finance_models.dart';
import 'package:injectable/injectable.dart';

import '../dto/finance_dto.dart';
import '../services/http/api_client.dart';

/// Money data of the signed-in user, kept in memory for every screen.
///
/// [refresh] loads it all; each write calls the API and reloads the parts it
/// affects (balances and budgets are computed by the server).
@LazySingleton(as: FinanceFacade)
class FinanceDatasource implements FinanceFacade {
  static const _pageSize = 100;

  final ApiClient _api;

  FinanceDatasource(this._api);

  final _changes = StreamController<FinanceSnapshot>.broadcast();
  var _snapshot = FinanceSnapshot.empty;
  String? _cursor;

  @override
  FinanceSnapshot get snapshot => _snapshot;

  @override
  Stream<FinanceSnapshot> get changes => _changes.stream;

  void _emit(FinanceSnapshot s) {
    _snapshot = s;
    _changes.add(s);
  }

  @override
  void reset() {
    _cursor = null;
    _emit(FinanceSnapshot.empty);
  }

  @override
  Future<void> refresh() async {
    final results = await Future.wait([
      _api.get('/me'),
      _api.get('/categories'),
      _api.get('/transactions', query: {'limit': _pageSize}),
      _api.get('/goals'),
      _api.get('/reminders'),
      _api.get('/accounts'),
    ]);
    final [me, categories, page, goals, reminders, accounts] = results;

    final onboarding = me['onboarding'] as Map;
    final name = [
      me['first_name'],
      me['last_name'],
    ].whereType<String>().where((e) => e.isNotEmpty).join(' ');
    final cats = _categories(categories);
    _cursor = page['next_cursor'];

    _emit(
      FinanceSnapshot(
        userName: name,
        phone: me['phone_masked'] ?? '',
        isNew: !(onboarding['balance_set'] &&
            onboarding['has_transactions'] &&
            onboarding['has_goals'] &&
            onboarding['has_reminders']),
        balanceSet: onboarding['balance_set'],
        startingBalance: 0,
        categories: cats,
        transactions: _transactions(page['items'], cats),
        goals: [for (final g in goals) goalFromJson(g)],
        reminders: _reminders(reminders),
        accounts: _accounts(accounts),
        monthSpent: _spent(categories),
        transactionCounts: _counts(categories),
        balance: accounts['total'],
        loaded: true,
        hasMoreTransactions: _cursor != null,
      ),
    );
  }

  @override
  Future<void> loadMoreTransactions() async {
    final cursor = _cursor;
    if (cursor == null) return;
    final page = await _api.get(
      '/transactions',
      query: {'limit': _pageSize, 'cursor': cursor},
    );
    _cursor = page['next_cursor'];
    _emit(
      _copy(
        transactions: [
          ..._snapshot.transactions,
          ..._transactions(page['items'], _snapshot.categories),
        ],
        hasMoreTransactions: _cursor != null,
      ),
    );
  }

  @override
  Future<void> setStartingBalance(
    num amount, {
    BalanceLocation? location,
  }) async {
    await _api.post(
      '/onboarding/balance',
      data: {
        'amount': amount,
        'location': (location ?? BalanceLocation.card).name,
      },
    );
    await refresh();
  }

  @override
  Future<void> addTransaction({
    required String categoryId,
    required num amount,
    String? title,
    String? receiptId,
  }) async {
    await _api.post(
      '/transactions',
      idempotent: true,
      data: {
        'type': amount > 0 ? 'income' : 'expense',
        'amount': amount.abs(),
        'category_id': categoryId,
        'title': ?title,
        'receipt_id': ?receiptId,
        'client_created_at': DateTime.now().toUtc().toIso8601String(),
      },
    );
    await refresh();
  }

  @override
  Future<void> saveCategory(Category category) async {
    final exists = _snapshot.category(category.id) != null;
    final data = {
      'name': category.name,
      'icon': category.icon,
      'color': colorToHex(category.color),
      'monthly_limit': category.limit,
    };
    if (exists) {
      await _api.patch('/categories/${category.id}', data: data);
    } else {
      await _api.post(
        '/categories',
        idempotent: true,
        data: {...data, 'type': category.isIncome ? 'income' : 'expense'},
      );
    }
    await _reloadCategories();
  }

  @override
  Future<void> deleteCategory(String id, {String? reassignTo}) async {
    await _api.delete(
      '/categories/$id',
      data: reassignTo == null ? null : {'reassign_to': reassignTo},
    );
    await refresh();
  }

  @override
  Future<Goal> addGoal({
    required String name,
    required String icon,
    required num target,
    required DateTime due,
    num? autoSave,
  }) async {
    final data = await _api.post(
      '/goals',
      idempotent: true,
      data: {
        'name': name,
        'icon': icon,
        'target': target,
        // Last day of the target month.
        'deadline': dateToJson(DateTime(due.year, due.month + 1, 0)),
        'auto_save_monthly': autoSave,
      },
    );
    final goal = goalFromJson(data);
    _emit(_copy(goals: [..._snapshot.goals, goal]));
    return goal;
  }

  @override
  Future<Goal> moveGoalMoney(String goalId, num amount) async {
    final data = await _api.post(
      '/goals/$goalId/${amount < 0 ? 'withdrawals' : 'deposits'}',
      idempotent: true,
      data: {'amount': amount.abs()},
    );
    final goal = goalFromJson(data);
    _replaceGoal(goal);
    // Money moved from / to an account.
    await _reloadAccounts();
    return goal;
  }

  @override
  Future<List<GoalEntry>> goalHistory(String goalId) async {
    final page = await _api.get('/goals/$goalId/history', query: {'limit': 100});
    return [for (final e in page['items']) goalEntryFromJson(e)];
  }

  @override
  Future<void> setGoalAutoSave(String goalId, num? amount) async {
    final data = await _api.patch(
      '/goals/$goalId',
      data: {'auto_save_monthly': amount},
    );
    _replaceGoal(goalFromJson(data));
  }

  @override
  Future<num> deleteGoal(String goalId) async {
    final data = await _api.delete('/goals/$goalId');
    _emit(
      _copy(goals: _snapshot.goals.where((g) => g.id != goalId).toList()),
    );
    await _reloadAccounts();
    return data?['returned_amount'] ?? 0;
  }

  @override
  Future<void> addReminder(Reminder reminder) async {
    final data = await _api.post(
      '/reminders',
      idempotent: true,
      data: {
        'title': reminder.title,
        'category_id': reminder.categoryId,
        'amount': reminder.amount,
        'due_date': dateToJson(reminder.dueDate),
        'repeat': reminderRepeatToJson(reminder.repeat),
      },
    );
    _emit(_copy(reminders: _sortReminders([..._snapshot.reminders, reminderFromJson(data)])));
  }

  @override
  Future<void> setReminderEnabled(String id, bool enabled) async {
    final data = await _api.patch('/reminders/$id', data: {'enabled': enabled});
    final updated = reminderFromJson(data);
    _emit(
      _copy(
        reminders: [
          for (final r in _snapshot.reminders) r.id == id ? updated : r,
        ],
      ),
    );
  }

  @override
  Future<void> setAccountFrozen(String id, bool frozen) async {
    await _api.post('/accounts/$id/${frozen ? 'freeze' : 'unfreeze'}');
    await _reloadAccounts();
  }

  // Partial reloads

  Future<void> _reloadAccounts() async {
    final accounts = await _api.get('/accounts');
    _emit(_copy(accounts: _accounts(accounts), balance: accounts['total']));
  }

  Future<void> _reloadCategories() async {
    final categories = await _api.get('/categories');
    _emit(
      _copy(
        categories: _categories(categories),
        monthSpent: _spent(categories),
        transactionCounts: _counts(categories),
      ),
    );
  }

  void _replaceGoal(Goal goal) => _emit(
    _copy(goals: [for (final g in _snapshot.goals) g.id == goal.id ? goal : g]),
  );

  // Mapping

  static List<Category> _categories(List<dynamic> json) => [
    for (final c in json) categoryFromJson(c),
  ];

  static Map<String, num> _spent(List<dynamic> json) => {
    for (final c in json)
      if ((c['spent'] ?? 0) > 0) c['id'] as String: c['spent'] as num,
  };

  static Map<String, int> _counts(List<dynamic> json) => {
    for (final c in json) c['id'] as String: c['transactions_count'] ?? 0,
  };

  static List<Transaction> _transactions(
    List<dynamic> json,
    List<Category> categories,
  ) => [
    for (final t in json)
      transactionFromJson(
        t,
        fallbackTitle:
            categories.where((c) => c.id == t['category_id']).firstOrNull?.name ??
            '',
      ),
  ];

  static List<Reminder> _reminders(List<dynamic> json) =>
      _sortReminders([for (final r in json) reminderFromJson(r)]);

  static List<Reminder> _sortReminders(List<Reminder> items) =>
      items..sort((a, b) => a.dueDate.compareTo(b.dueDate));

  static List<Account> _accounts(Map<String, dynamic> json) => [
    for (final (i, a) in (json['items'] as List).indexed) accountFromJson(a, i),
  ];

  FinanceSnapshot _copy({
    List<Category>? categories,
    List<Transaction>? transactions,
    List<Goal>? goals,
    List<Reminder>? reminders,
    List<Account>? accounts,
    Map<String, num>? monthSpent,
    Map<String, int>? transactionCounts,
    num? balance,
    bool? hasMoreTransactions,
  }) {
    final s = _snapshot;
    return FinanceSnapshot(
      userName: s.userName,
      phone: s.phone,
      isNew: s.isNew,
      balanceSet: s.balanceSet,
      startingBalance: s.startingBalance,
      categories: categories ?? s.categories,
      transactions: transactions ?? s.transactions,
      goals: goals ?? s.goals,
      reminders: reminders ?? s.reminders,
      accounts: accounts ?? s.accounts,
      monthSpent: monthSpent ?? s.monthSpent,
      transactionCounts: transactionCounts ?? s.transactionCounts,
      balance: balance ?? s.balance,
      loaded: s.loaded,
      hasMoreTransactions: hasMoreTransactions ?? s.hasMoreTransactions,
    );
  }
}
