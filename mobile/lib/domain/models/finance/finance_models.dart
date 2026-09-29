/// Money data shared by every signed-in screen.
///
/// Amounts are UZS without tiyin. Colors are ARGB ints and icons are Lucide
/// names (see `CategoryIcons`), so the models stay free of Flutter types.
library;

class Category {
  final String id;
  final String name;

  /// Lucide icon name, e.g. `shopping-cart`.
  final String icon;
  final int color;
  final bool isIncome;

  /// Monthly budget. `null` = no limit.
  final num? limit;

  const Category({
    required this.id,
    required this.name,
    required this.icon,
    required this.color,
    this.isIncome = false,
    this.limit,
  });

  Category copyWith({
    String? name,
    String? icon,
    int? color,
    num? Function()? limit,
  }) => Category(
    id: id,
    name: name ?? this.name,
    icon: icon ?? this.icon,
    color: color ?? this.color,
    isIncome: isIncome,
    limit: limit == null ? this.limit : limit(),
  );
}

class Transaction {
  final String id;
  final String title;
  final String categoryId;

  /// Positive = income, negative = expense.
  final num amount;
  final DateTime date;

  const Transaction({
    required this.id,
    required this.title,
    required this.categoryId,
    required this.amount,
    required this.date,
  });

  bool get isIncome => amount > 0;
}

class GoalEntry {
  /// Positive = deposit, negative = withdrawal.
  final num amount;
  final DateTime date;

  const GoalEntry(this.amount, this.date);
}

class Goal {
  final String id;
  final String name;

  /// Lucide icon name.
  final String icon;
  final num saved;
  final num target;

  /// First day of the target month.
  final DateTime due;

  /// Monthly auto-save amount, `null` = off.
  final num? autoSave;

  /// Newest first.
  final List<GoalEntry> history;

  const Goal({
    required this.id,
    required this.name,
    required this.icon,
    required this.saved,
    required this.target,
    required this.due,
    this.autoSave,
    this.history = const [],
  });

  double get progress => target <= 0 ? 0 : (saved / target).clamp(0, 1);

  bool get reached => saved >= target;

  num get remaining => saved >= target ? 0 : target - saved;

  Goal copyWith({
    num? saved,
    num? Function()? autoSave,
    List<GoalEntry>? history,
  }) => Goal(
    id: id,
    name: name,
    icon: icon,
    saved: saved ?? this.saved,
    target: target,
    due: due,
    autoSave: autoSave == null ? this.autoSave : autoSave(),
    history: history ?? this.history,
  );
}

enum ReminderRepeat { once, weekly, monthly, yearly }

enum ReminderNotify { sameDay, dayBefore, threeDaysBefore }

class Reminder {
  final String id;
  final String title;
  final String categoryId;
  final num amount;
  final DateTime dueDate;
  final ReminderRepeat repeat;
  final ReminderNotify notify;
  final bool enabled;

  const Reminder({
    required this.id,
    required this.title,
    required this.categoryId,
    required this.amount,
    required this.dueDate,
    this.repeat = ReminderRepeat.monthly,
    this.notify = ReminderNotify.dayBefore,
    this.enabled = true,
  });

  /// Whole days from [now] to the due date (0 = today).
  int dueIn(DateTime now) => DateTime.utc(
    dueDate.year,
    dueDate.month,
    dueDate.day,
  ).difference(DateTime.utc(now.year, now.month, now.day)).inDays;

  Reminder copyWith({bool? enabled}) => Reminder(
    id: id,
    title: title,
    categoryId: categoryId,
    amount: amount,
    dueDate: dueDate,
    repeat: repeat,
    notify: notify,
    enabled: enabled ?? this.enabled,
  );
}

class Account {
  final String id;

  /// "Kapitalbank" / "Cash".
  final String bank;

  /// UZCARD / HUMO / VISA; `null` for cash.
  final String? network;
  final String? last4;
  final String? expiry;
  final num balance;
  final int color;
  final num? monthlyLimit;
  final bool frozen;
  final bool isMain;

  const Account({
    required this.id,
    required this.bank,
    required this.balance,
    required this.color,
    this.network,
    this.last4,
    this.expiry,
    this.monthlyLimit,
    this.frozen = false,
    this.isMain = false,
  });

  bool get isCard => network != null;

  Account copyWith({bool? frozen}) => Account(
    id: id,
    bank: bank,
    balance: balance,
    color: color,
    network: network,
    last4: last4,
    expiry: expiry,
    monthlyLimit: monthlyLimit,
    frozen: frozen ?? this.frozen,
    isMain: isMain,
  );
}

/// Where the starting balance is kept (Starting balance screen).
enum BalanceLocation { cash, card, both }

/// Immutable view of everything in the finance store.
class FinanceSnapshot {
  final String userName;
  final String phone;
  final bool isNew;
  final bool balanceSet;
  final num startingBalance;
  final List<Category> categories;

  /// Newest first.
  final List<Transaction> transactions;
  final List<Goal> goals;

  /// Sorted by due date.
  final List<Reminder> reminders;
  final List<Account> accounts;

  /// Spending per category this month (budgets).
  final Map<String, num> monthSpent;

  /// All-time transactions per category (from the server).
  final Map<String, int> transactionCounts;

  /// Current balance of all accounts (computed by the server).
  final num balance;

  /// False until the first load finished.
  final bool loaded;

  /// More transactions can be loaded ([FinanceFacade.loadMoreTransactions]).
  final bool hasMoreTransactions;

  const FinanceSnapshot({
    required this.userName,
    required this.phone,
    required this.isNew,
    required this.balanceSet,
    required this.startingBalance,
    required this.categories,
    required this.transactions,
    required this.goals,
    required this.reminders,
    required this.accounts,
    required this.monthSpent,
    this.transactionCounts = const {},
    this.balance = 0,
    this.loaded = false,
    this.hasMoreTransactions = false,
  });

  static const empty = FinanceSnapshot(
    userName: '',
    phone: '',
    isNew: false,
    balanceSet: false,
    startingBalance: 0,
    categories: [],
    transactions: [],
    goals: [],
    reminders: [],
    accounts: [],
    monthSpent: {},
  );

  Category? category(String id) =>
      categories.where((e) => e.id == id).firstOrNull;

  Iterable<Category> get budgets => categories.where((e) => e.limit != null);

  int transactionCount(String categoryId) =>
      transactionCounts[categoryId] ??
      transactions.where((t) => t.categoryId == categoryId).length;
}
