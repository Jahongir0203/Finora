import 'package:bloc/bloc.dart';
import 'package:finora/domain/facades/notifications_facade.dart';
import 'package:finora/domain/models/notifications/app_notification.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:injectable/injectable.dart';

part 'notifications_cubit.freezed.dart';
part 'notifications_state.dart';

/// Shared by the Home bell and the Notifications screen
/// (docs/screens/HOME_SCREENS.md §4).
@Injectable()
class NotificationsCubit extends Cubit<NotificationsState> {
  final NotificationsFacade _facade;

  NotificationsCubit(this._facade) : super(const .initial());

  Future<void> load() async {
    emit(state.copyWith(isLoading: true));
    try {
      final items = await _facade.getNotifications();
      if (!isClosed) emit(state.copyWith(items: items, isLoading: false));
    } catch (_) {
      if (!isClosed) emit(state.copyWith(isLoading: false));
    }
  }

  void markRead(String id) {
    emit(
      state.copyWith(
        items: [
          for (final e in state.items)
            e.id == id ? e.copyWith(isRead: true) : e,
        ],
      ),
    );
    _facade.markRead(id);
  }

  void markAllRead() {
    if (!state.hasUnread) return;
    emit(
      state.copyWith(
        items: [for (final e in state.items) e.copyWith(isRead: true)],
      ),
    );
    _facade.markAllRead();
  }

  /// Returns the removed item for Undo.
  AppNotification? delete(String id) {
    final removed = state.items.where((e) => e.id == id).firstOrNull;
    if (removed == null) return null;
    emit(state.copyWith(items: state.items.where((e) => e.id != id).toList()));
    _facade.delete(id);
    return removed;
  }

  /// Returns the removed items for Undo.
  List<AppNotification> clear() {
    final removed = state.items;
    emit(state.copyWith(items: const []));
    _facade.clear();
    return removed;
  }

  Future<void> restore(List<AppNotification> items) async {
    await _facade.restore(items);
    await load();
  }
}
