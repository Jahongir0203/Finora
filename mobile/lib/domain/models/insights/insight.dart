enum InsightAction { setBudget, remindMe, review, turnOn }

/// AI tip (`GET /insights`, docs/screens/STATS_INSIGHTS.md §2).
class Insight {
  final String id;

  /// Lucide icon name from the server.
  final String icon;

  /// Tints the icon; `null` for tips not tied to a category.
  final String? categoryId;
  final String title;
  final String body;
  final num? saving;
  final InsightAction action;
  final bool dismissed;

  const Insight({
    required this.id,
    required this.icon,
    required this.title,
    required this.body,
    required this.action,
    this.categoryId,
    this.saving,
    this.dismissed = false,
  });
}

class InsightList {
  final List<Insight> items;

  /// Hero amount: the server's estimate for all active tips.
  final num potentialSaving;

  const InsightList(this.items, this.potentialSaving);
}
