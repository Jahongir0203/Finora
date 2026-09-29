import 'dart:async';

import 'package:finora/domain/facades/notifications_facade.dart';
import 'package:finora/domain/models/notifications/app_notification.dart';
import 'package:injectable/injectable.dart';

import '../dto/finance_dto.dart';
import '../services/http/api_client.dart';

/// `/notifications`. Deleting waits for the Undo snackbar (4 s) before it
/// reaches the server, so Undo needs no restore endpoint.
@LazySingleton(as: NotificationsFacade)
class NotificationsDatasource implements NotificationsFacade {
  static const _undoWindow = Duration(seconds: 5);

  final ApiClient _api;

  NotificationsDatasource(this._api);

  /// id → pending delete. `_all` → pending Clear.
  final _pending = <String, Timer>{};
  static const _all = '*';

  @override
  Future<List<AppNotification>> getNotifications() async {
    if (_pending.containsKey(_all)) return const [];
    final items = <AppNotification>[];
    String? cursor;
    // Two pages (up to 200) are plenty for the list; older ones age out.
    for (var i = 0; i < 2; i++) {
      final page = await _api.get(
        '/notifications',
        query: {'limit': 100, 'cursor': cursor},
      );
      items.addAll([for (final n in page['items']) _map(n)]);
      cursor = page['next_cursor'];
      if (cursor == null) break;
    }
    return items.where((n) => !_pending.containsKey(n.id)).toList();
  }

  @override
  Future<void> markRead(String id) =>
      _api.post('/notifications/$id/read').catchError((_) {});

  @override
  Future<void> markAllRead() =>
      _api.post('/notifications/read-all').catchError((_) {});

  @override
  Future<void> delete(String id) async =>
      _schedule(id, () => _api.delete('/notifications/$id'));

  @override
  Future<void> clear() async =>
      _schedule(_all, () => _api.delete('/notifications'));

  @override
  Future<void> restore(List<AppNotification> items) async {
    _pending.remove(_all)?.cancel();
    for (final n in items) {
      _pending.remove(n.id)?.cancel();
    }
  }

  void _schedule(String key, Future<dynamic> Function() commit) {
    _pending.remove(key)?.cancel();
    _pending[key] = Timer(_undoWindow, () {
      _pending.remove(key);
      commit().catchError((_) {});
    });
  }

  static AppNotification _map(Json j) => AppNotification(
    id: j['id'],
    type: NotificationType.byKey(j['type']) ?? NotificationType.security,
    title: j['title'],
    body: j['body'],
    createdAt: DateTime.parse(j['created_at']).toLocal(),
    isRead: j['read'] ?? false,
    deepLink: j['deep_link'],
  );
}
