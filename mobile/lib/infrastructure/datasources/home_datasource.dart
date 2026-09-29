import 'package:finora/domain/facades/finance_facade.dart';
import 'package:finora/domain/facades/home_facade.dart';
import 'package:finora/domain/models/finance/finance_models.dart';
import 'package:finora/domain/models/home/home_data.dart';
import 'package:injectable/injectable.dart';

import '../dto/finance_dto.dart';
import '../services/http/api_client.dart';

/// `GET /home`: everything the Home screen shows in one call.
@LazySingleton(as: HomeFacade)
class HomeDatasource implements HomeFacade {
  final ApiClient _api;
  final FinanceFacade _finance;

  HomeDatasource(this._api, this._finance);

  @override
  Future<HomeData> getHome() async => _map(await _api.get('/home'));

  @override
  Future<HomeData> setBalance(num amount, {BalanceLocation? location}) async {
    // Also reloads accounts and the onboarding state for other screens.
    await _finance.setStartingBalance(amount, location: location);
    return getHome();
  }

  HomeData _map(Json j) {
    final started = j['get_started'] as Json;
    final balance = j['balance'] as Json;
    final month = j['month'] as Json;
    final budget = j['budget_summary'] as Json?;
    final teaser = j['ai_teaser'] as Json?;
    final categories = _finance.snapshot.categories;
    String label(String id) =>
        categories.where((c) => c.id == id).firstOrNull?.name ?? '';

    return HomeData(
      userName: j['user']['first_name'] ?? '',
      isNew: !started.values.every((v) => v == true),
      balanceSet: !(balance['need_balance'] as bool),
      balance: balance['total'],
      monthIncome: month['income'],
      monthExpenses: month['expenses'],
      hasTransactions: started['transaction'],
      hasGoals: started['goal'],
      hasReminders: started['reminder'],
      unreadNotifications: j['unread_notifications'] ?? 0,
      recentTransactions: [
        for (final t in j['recent_transactions'])
          TransactionItem(
            id: t['id'],
            title: (t['title'] as String?)?.isNotEmpty == true
                ? t['title']
                : label(t['category_id']),
            category: t['category_id'],
            categoryLabel: label(t['category_id']),
            amount: signedAmount(t),
            date: DateTime.parse(t['occurred_at']).toLocal(),
          ),
      ],
      upcomingPayments: [
        for (final p in j['upcoming_payments'])
          UpcomingPayment(
            id: p['id'],
            title: p['title'],
            category: p['category_id'],
            amount: p['amount'],
            dueDate: dateFromJson(p['due_date']),
          ),
      ],
      budget: budget == null
          ? null
          : BudgetSummary(
              month: DateTime.parse('${budget['month']}-01'.substring(0, 10)),
              spent: budget['spent'],
              limit: budget['limit'],
            ),
      aiSavingAmount: teaser?['saving'],
      fetchedAt: DateTime.now(),
    );
  }
}
