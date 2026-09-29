import 'package:finora/domain/models/stats/stats_data.dart';

abstract class StatsFacade {
  /// `GET /stats?period=` for the period containing today.
  Future<StatsData> getStats(StatsPeriod period);
}
