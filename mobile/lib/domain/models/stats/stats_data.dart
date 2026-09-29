enum StatsPeriod { week, month, year }

/// `GET /stats` (docs/screens/STATS_INSIGHTS.md §1).
class StatsData {
  final StatsPeriod period;
  final num totalSpent;

  /// Biggest first; percentages add up to 100.
  final List<StatsSlice> breakdown;
  final List<StatsBar> bars;

  /// vs the previous period; `null` when there is nothing to compare.
  final int? changePct;

  /// False for new users: the page shows the empty state.
  final bool hasEnoughData;

  const StatsData({
    required this.period,
    required this.totalSpent,
    required this.breakdown,
    required this.bars,
    required this.changePct,
    required this.hasEnoughData,
  });

  /// Index of the current bar (highlighted), -1 when none.
  int get currentBar => bars.indexWhere((b) => b.current);
}

class StatsSlice {
  final String categoryId;
  final num amount;
  final int pct;

  const StatsSlice(this.categoryId, this.amount, this.pct);
}

class StatsBar {
  /// `M`, `W1`, `J`… (localized by the server).
  final String label;
  final num value;
  final bool current;

  const StatsBar(this.label, this.value, {this.current = false});
}
