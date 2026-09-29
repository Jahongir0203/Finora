import 'package:finora/domain/models/notifications/app_notification.dart';

abstract class NotificationsFacade {
  /// Newest first.
  Future<List<AppNotification>> getNotifications();

  Future<void> markRead(String id);

  Future<void> markAllRead();

  /// Committed after the Undo window unless [restore] is called.
  Future<void> delete(String id);

  /// Committed after the Undo window unless [restore] is called.
  Future<void> clear();

  /// Puts back notifications removed by [clear] or [delete] (Undo).
  Future<void> restore(List<AppNotification> items);
}
