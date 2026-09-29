import 'package:finora/domain/models/notifications/app_notification.dart';

abstract class NotificationsFacade {
  /// Newest first.
  Future<List<AppNotification>> getNotifications();

  Future<void> markRead(String id);

  Future<void> markAllRead();

  Future<void> delete(String id);

  Future<void> clear();

  /// Puts back notifications removed by [clear] or [delete] (Undo).
  Future<void> restore(List<AppNotification> items);
}
