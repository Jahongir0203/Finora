/// Statistics mock data from docs/screens/STATS_INSIGHTS.md §1.2.
///
/// TODO: load from `/stats?period=`.
library;

enum StatsPeriod { week, month, year }

/// Monthly base spend per category, in display order.
const statsMonthBase = [
  ('groceries', 1840000),
  ('shopping', 1150000),
  ('food', 920000),
  ('bills', 610000),
  ('transport', 460000),
  ('health', 320000),
];

const _factor = {
  StatsPeriod.week: 0.22,
  StatsPeriod.month: 1.0,
  StatsPeriod.year: 11.4,
};

/// (categoryId, amount) for [period], rounded to 1000.
List<(String, num)> statsBreakdown(StatsPeriod period) => [
  for (final (id, v) in statsMonthBase)
    (id, (v * _factor[period]! / 1000).round() * 1000),
];

/// Trend bars: (label, value). The current bar is [statsCurrentBar].
List<(String, double)> statsTrend(StatsPeriod period) => switch (period) {
  .week => const [
    ('M', 180),
    ('T', 95),
    ('W', 240),
    ('T', 60),
    ('F', 310),
    ('S', 420),
    ('S', 150),
  ],
  .month => const [('W1', 1200), ('W2', 1600), ('W3', 1100), ('W4', 1560)],
  .year => const [
    ('J', 4.8),
    ('F', 5.1),
    ('M', 4.6),
    ('A', 5.3),
    ('M', 4.9),
    ('J', 5.8),
    ('J', 6.1),
    ('A', 5.2),
    ('S', 5.46),
    ('O', 0),
    ('N', 0),
    ('D', 0),
  ],
};

int statsCurrentBar(StatsPeriod period) => switch (period) {
  .week => 6,
  .month => 3,
  .year => 8,
};
