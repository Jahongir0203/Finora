enum NotificationType {
  paymentDue('payment_due'),
  income('income'),
  budgetExceeded('budget_exceeded'),
  weeklyReport('weekly_report'),
  goalMilestone('goal_milestone'),
  security('security');

  /// Server value.
  final String key;

  const NotificationType(this.key);

  static NotificationType? byKey(String? key) =>
      values.where((e) => e.key == key).firstOrNull;
}

class AppNotification {
  final String id;
  final NotificationType type;
  final String title;
  final String body;
  final DateTime createdAt;
  final bool isRead;

  const AppNotification({
    required this.id,
    required this.type,
    required this.title,
    required this.body,
    required this.createdAt,
    this.isRead = false,
  });

  AppNotification copyWith({bool? isRead}) => AppNotification(
    id: id,
    type: type,
    title: title,
    body: body,
    createdAt: createdAt,
    isRead: isRead ?? this.isRead,
  );
}
