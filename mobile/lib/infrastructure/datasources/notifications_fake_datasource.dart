import 'package:finora/domain/facades/notifications_facade.dart';
import 'package:finora/domain/models/notifications/app_notification.dart';
import 'package:injectable/injectable.dart';

import 'finance_fake_store.dart';

/// Temporary in-memory notifications. Empty for a fresh user; filled with the
/// examples from docs/screens/HOME_SCREENS.md §4 when
/// [FinanceFakeStore.seedDemoData] is on.
///
/// TODO: replace with a Dio datasource once `/notifications` exists.
@LazySingleton(as: NotificationsFacade)
class NotificationsFakeDatasource implements NotificationsFacade {
  static const _latency = Duration(milliseconds: 300);

  final List<AppNotification> _items = FinanceFakeStore.seedDemoData
      ? _demo()
      : [];

  @override
  Future<List<AppNotification>> getNotifications() async {
    await Future.delayed(_latency);
    return List.unmodifiable(_items);
  }

  @override
  Future<void> markRead(String id) async {
    final i = _items.indexWhere((e) => e.id == id);
    if (i != -1) _items[i] = _items[i].copyWith(isRead: true);
  }

  @override
  Future<void> markAllRead() async {
    for (var i = 0; i < _items.length; i++) {
      _items[i] = _items[i].copyWith(isRead: true);
    }
  }

  @override
  Future<void> delete(String id) async => _items.removeWhere((e) => e.id == id);

  @override
  Future<void> clear() async => _items.clear();

  @override
  Future<void> restore(List<AppNotification> items) async {
    final ids = _items.map((e) => e.id).toSet();
    _items
      ..addAll(items.where((e) => !ids.contains(e.id)))
      ..sort((a, b) => b.createdAt.compareTo(a.createdAt));
  }

  static List<AppNotification> _demo() {
    final now = DateTime.now();
    DateTime at(int daysAgo, int h, int m) =>
        DateTime(now.year, now.month, now.day - daysAgo, h, m);

    return [
      AppNotification(
        id: 'n1',
        type: .paymentDue,
        title: 'Payment due tomorrow',
        body: 'Electricity · 142 000 UZS is due on 29 Sep.',
        createdAt: at(0, 10, 0),
      ),
      AppNotification(
        id: 'n2',
        type: .income,
        title: 'Salary received',
        body: '+12 500 000 UZS from Acme LLC arrived on Uzcard •• 4821.',
        createdAt: at(0, 9, 12),
      ),
      AppNotification(
        id: 'n3',
        type: .budgetExceeded,
        title: 'Food budget exceeded',
        body: "You've spent 920 000 of 800 000 UZS on Food & drinks.",
        createdAt: at(1, 20, 45),
        isRead: true,
      ),
      AppNotification(
        id: 'n4',
        type: .weeklyReport,
        title: 'Weekly report is ready',
        body: 'You spent 8% less than last week. Tap to see details.',
        createdAt: at(2, 9, 0),
        isRead: true,
      ),
      AppNotification(
        id: 'n5',
        type: .goalMilestone,
        title: 'Goal milestone',
        body: 'Samarkand trip is 62% funded. Keep going.',
        createdAt: at(4, 18, 30),
        isRead: true,
      ),
      AppNotification(
        id: 'n6',
        type: .security,
        title: 'New sign-in',
        body: 'Finora was opened on a new device in Tashkent.',
        createdAt: at(8, 11, 15),
        isRead: true,
      ),
    ];
  }
}
