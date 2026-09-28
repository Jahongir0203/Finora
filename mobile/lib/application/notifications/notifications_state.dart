part of 'notifications_cubit.dart';

@freezed
abstract class NotificationsState with _$NotificationsState {
  const NotificationsState._();

  const factory NotificationsState.initial({
    @Default(<AppNotification>[]) List<AppNotification> items,
    @Default(false) bool isLoading,
  }) = _Initial;

  bool get hasUnread => items.any((e) => !e.isRead);
}
