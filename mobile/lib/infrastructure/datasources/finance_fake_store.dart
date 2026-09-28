import 'dart:async';

import 'package:finora/domain/facades/finance_facade.dart';
import 'package:finora/domain/models/finance/finance_models.dart';
import 'package:injectable/injectable.dart';

/// Temporary in-memory finance data so every screen works end-to-end.
///
/// Starts as a fresh user (no transactions, budgets, goals or reminders).
/// Set [seedDemoData] to `true` for the filled state from the screenshots.
///
/// TODO: replace with Dio datasources once the endpoints exist.
@LazySingleton(as: FinanceFacade)
class FinanceFakeStore implements FinanceFacade {
  static const seedDemoData = false;

  FinanceFakeStore() {
    if (seedDemoData) _seedDemo();
  }

  final _changes = StreamController<FinanceSnapshot>.broadcast();
  var _id = 0;

  var _isNew = !seedDemoData;
  var _balanceSet = seedDemoData;
  num _startingBalance = seedDemoData ? 12_450_000 : 0;

  final _categories = <Category>[..._defaultCategories];
  final _transactions = <Transaction>[];
  final _goals = <Goal>[];
  final _reminders = <Reminder>[];
  final _accounts = <Account>[..._defaultAccounts];
  final _monthSpent = <String, num>{};

  @override
  FinanceSnapshot get snapshot {
    final reminders = [..._reminders]
      ..sort((a, b) => a.dueDate.compareTo(b.dueDate));
    final data = FinanceSnapshot(
      userName: 'Doston Karimov',
      phone: '+998901234567',
      isNew: _isNew,
      balanceSet: _balanceSet,
      startingBalance: _startingBalance,
      categories: List.unmodifiable(_categories),
      transactions: List.unmodifiable(_transactions),
      goals: List.unmodifiable(_goals),
      reminders: List.unmodifiable(reminders),
      accounts: List.unmodifiable(_accounts),
      monthSpent: Map.unmodifiable(_monthSpent),
    );
    // The server stops treating the user as new once the checklist is done.
    if (_isNew &&
        _balanceSet &&
        _transactions.isNotEmpty &&
        _goals.isNotEmpty &&
        _reminders.isNotEmpty) {
      _isNew = false;
    }
    return data;
  }

  @override
  Stream<FinanceSnapshot> get changes => _changes.stream;

  void _emit() => _changes.add(snapshot);

  String _nextId(String prefix) => '$prefix${++_id}';

  @override
  Future<void> setStartingBalance(
    num amount, {
    BalanceLocation? location,
  }) async {
    _startingBalance = amount;
    _balanceSet = amount > 0;
    _emit();
  }

  @override
  Future<void> addTransaction({
    required String categoryId,
    required num amount,
    String? title,
  }) async {
    final category = _categories.where((e) => e.id == categoryId).firstOrNull;
    _transactions.insert(
      0,
      Transaction(
        id: _nextId('t'),
        title: title ?? category?.name ?? '',
        categoryId: categoryId,
        amount: amount,
        date: DateTime.now(),
      ),
    );
    if (amount < 0) {
      _monthSpent[categoryId] = (_monthSpent[categoryId] ?? 0) - amount;
    }
    _emit();
  }

  @override
  Future<void> saveCategory(Category category) async {
    final i = _categories.indexWhere((e) => e.id == category.id);
    if (i == -1) {
      _categories.add(
        Category(
          id: _nextId('c'),
          name: category.name,
          icon: category.icon,
          color: category.color,
          isIncome: category.isIncome,
          limit: category.limit,
        ),
      );
    } else {
      _categories[i] = category;
    }
    _emit();
  }

  @override
  Future<void> deleteCategory(String id) async {
    _categories.removeWhere((e) => e.id == id);
    _emit();
  }

  @override
  Future<Goal> addGoal({
    required String name,
    required String icon,
    required num target,
    required DateTime due,
    num? autoSave,
  }) async {
    final goal = Goal(
      id: _nextId('g'),
      name: name,
      icon: icon,
      saved: 0,
      target: target,
      due: due,
      autoSave: autoSave,
    );
    _goals.add(goal);
    _emit();
    return goal;
  }

  @override
  Future<Goal> moveGoalMoney(String goalId, num amount) async {
    final i = _goals.indexWhere((e) => e.id == goalId);
    final goal = _goals[i];
    final updated = goal.copyWith(
      saved: goal.saved + amount,
      history: [GoalEntry(amount, DateTime.now()), ...goal.history],
    );
    _goals[i] = updated;
    _emit();
    return updated;
  }

  @override
  Future<void> setGoalAutoSave(String goalId, num? amount) async {
    final i = _goals.indexWhere((e) => e.id == goalId);
    _goals[i] = _goals[i].copyWith(autoSave: () => amount);
    _emit();
  }

  @override
  Future<void> deleteGoal(String goalId) async {
    _goals.removeWhere((e) => e.id == goalId);
    _emit();
  }

  @override
  Future<void> addReminder(Reminder reminder) async {
    _reminders.add(
      Reminder(
        id: _nextId('r'),
        title: reminder.title,
        categoryId: reminder.categoryId,
        amount: reminder.amount,
        dueDate: reminder.dueDate,
        repeat: reminder.repeat,
        notify: reminder.notify,
      ),
    );
    _emit();
  }

  @override
  Future<void> setReminderEnabled(String id, bool enabled) async {
    final i = _reminders.indexWhere((e) => e.id == id);
    _reminders[i] = _reminders[i].copyWith(enabled: enabled);
    _emit();
  }

  @override
  Future<void> setAccountFrozen(String id, bool frozen) async {
    final i = _accounts.indexWhere((e) => e.id == id);
    _accounts[i] = _accounts[i].copyWith(frozen: frozen);
    _emit();
  }

  // Seed data (docs/screens/*.md)

  static const _defaultCategories = [
    Category(
      id: 'groceries',
      name: 'Groceries',
      icon: 'shopping-cart',
      color: 0xFF10B981,
    ),
    Category(
      id: 'food',
      name: 'Food & drinks',
      icon: 'utensils',
      color: 0xFFF59E0B,
    ),
    Category(
      id: 'transport',
      name: 'Transport',
      icon: 'car',
      color: 0xFF3B82F6,
    ),
    Category(id: 'bills', name: 'Bills', icon: 'receipt', color: 0xFF8B5CF6),
    Category(
      id: 'health',
      name: 'Health',
      icon: 'heart-pulse',
      color: 0xFFEF4444,
    ),
    Category(
      id: 'shopping',
      name: 'Shopping',
      icon: 'shopping-bag',
      color: 0xFFEC4899,
    ),
    Category(id: 'housing', name: 'Housing', icon: 'house', color: 0xFF14B8A6),
    Category(
      id: 'subscriptions',
      name: 'Subscriptions',
      icon: 'repeat',
      color: 0xFF6366F1,
    ),
    Category(
      id: 'salary',
      name: 'Salary',
      icon: 'briefcase',
      color: 0xFF10B981,
      isIncome: true,
    ),
    Category(
      id: 'transfer',
      name: 'Transfer',
      icon: 'arrow-down-left',
      color: 0xFF0EA5E9,
      isIncome: true,
    ),
  ];

  static const _defaultAccounts = [
    Account(
      id: 'a1',
      bank: 'Kapitalbank',
      network: 'UZCARD',
      last4: '4821',
      expiry: '08/29',
      balance: 14_250_000,
      color: 0xFF064E3B,
      monthlyLimit: 10_000_000,
      isMain: true,
    ),
    Account(
      id: 'a2',
      bank: 'Hamkorbank',
      network: 'HUMO',
      last4: '7730',
      expiry: '11/28',
      balance: 5_400_000,
      color: 0xFF1E293B,
      monthlyLimit: 5_000_000,
    ),
    Account(
      id: 'a3',
      bank: 'TBC Bank',
      network: 'VISA',
      last4: '1094',
      expiry: '03/30',
      balance: 4_000_000,
      color: 0xFF4C1D95,
      monthlyLimit: 8_000_000,
    ),
    Account(id: 'cash', bank: 'Cash', balance: 1_200_000, color: 0xFFB45309),
  ];

  void _seedDemo() {
    final now = DateTime.now();
    DateTime at(int daysAgo, int h, int m) =>
        DateTime(now.year, now.month, now.day - daysAgo, h, m);
    DateTime inDays(int d) => DateTime(now.year, now.month, now.day + d);

    _transactions.addAll([
      Transaction(
        id: 'd1',
        title: 'Korzinka',
        categoryId: 'groceries',
        amount: -186_400,
        date: at(0, 14, 20),
      ),
      Transaction(
        id: 'd2',
        title: 'Acme LLC',
        categoryId: 'salary',
        amount: 12_500_000,
        date: at(0, 9, 0),
      ),
      Transaction(
        id: 'd3',
        title: 'Evos',
        categoryId: 'food',
        amount: -64_000,
        date: at(1, 20, 45),
      ),
      Transaction(
        id: 'd4',
        title: 'Yandex Go',
        categoryId: 'transport',
        amount: -28_500,
        date: at(1, 18, 10),
      ),
      Transaction(
        id: 'd5',
        title: 'Aziz Rahimov',
        categoryId: 'transfer',
        amount: 500_000,
        date: at(1, 12, 30),
      ),
      Transaction(
        id: 'd6',
        title: 'Uzmobile',
        categoryId: 'bills',
        amount: -50_000,
        date: at(4, 10, 5),
      ),
      Transaction(
        id: 'd7',
        title: 'Oxy Pharm',
        categoryId: 'health',
        amount: -89_000,
        date: at(4, 8, 40),
      ),
      Transaction(
        id: 'd8',
        title: 'Uzum Market',
        categoryId: 'shopping',
        amount: -349_000,
        date: at(5, 21, 15),
      ),
    ]);

    const limits = {
      'groceries': 2_500_000,
      'food': 800_000,
      'transport': 600_000,
      'shopping': 1_500_000,
    };
    for (var i = 0; i < _categories.length; i++) {
      final limit = limits[_categories[i].id];
      if (limit != null) {
        _categories[i] = _categories[i].copyWith(limit: () => limit);
      }
    }
    _monthSpent.addAll({
      'groceries': 1_840_000,
      'food': 920_000,
      'shopping': 1_150_000,
      'transport': 460_000,
      'bills': 610_000,
      'health': 320_000,
    });

    _goals.addAll([
      Goal(
        id: 'g-emergency',
        name: 'Emergency fund',
        icon: 'shield-check',
        saved: 12_000_000,
        target: 30_000_000,
        due: DateTime(now.year + 1, 12),
        autoSave: 1_000_000,
        history: [
          GoalEntry(1_000_000, DateTime(now.year, 9, 1)),
          GoalEntry(1_000_000, DateTime(now.year, 8, 1)),
          GoalEntry(2_500_000, DateTime(now.year, 7, 14)),
          GoalEntry(1_000_000, DateTime(now.year, 7, 1)),
        ],
      ),
      Goal(
        id: 'g-macbook',
        name: 'New MacBook',
        icon: 'laptop',
        saved: 6_200_000,
        target: 18_000_000,
        due: DateTime(now.year + 1, 3),
      ),
      Goal(
        id: 'g-trip',
        name: 'Samarkand trip',
        icon: 'plane',
        saved: 3_100_000,
        target: 5_000_000,
        due: DateTime(now.year + 1, 6),
      ),
    ]);

    _reminders.addAll([
      Reminder(
        id: 'r-el',
        title: 'Electricity',
        categoryId: 'bills',
        amount: 142_000,
        dueDate: inDays(1),
      ),
      Reminder(
        id: 'r-net',
        title: 'Internet · Uzonline',
        categoryId: 'subscriptions',
        amount: 99_000,
        dueDate: inDays(3),
      ),
      Reminder(
        id: 'r-rent',
        title: 'Rent',
        categoryId: 'housing',
        amount: 4_500_000,
        dueDate: inDays(7),
      ),
      Reminder(
        id: 'r-gym',
        title: 'Gym membership',
        categoryId: 'health',
        amount: 250_000,
        dueDate: inDays(12),
        enabled: false,
      ),
      Reminder(
        id: 'r-car',
        title: 'Car insurance',
        categoryId: 'transport',
        amount: 1_200_000,
        dueDate: inDays(48),
        repeat: ReminderRepeat.yearly,
      ),
    ]);
  }
}
