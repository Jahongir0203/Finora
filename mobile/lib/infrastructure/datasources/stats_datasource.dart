import 'package:finora/domain/facades/stats_facade.dart';
import 'package:finora/domain/models/stats/stats_data.dart';
import 'package:injectable/injectable.dart';

import '../services/http/api_client.dart';

@LazySingleton(as: StatsFacade)
class StatsDatasource implements StatsFacade {
  final ApiClient _api;

  StatsDatasource(this._api);

  @override
  Future<StatsData> getStats(StatsPeriod period) async {
    final j = await _api.get('/stats', query: {'period': period.name});
    return StatsData(
      period: period,
      totalSpent: j['total_spent'],
      breakdown: [
        for (final b in j['breakdown'])
          StatsSlice(b['category_id'], b['amount'], b['pct']),
      ],
      bars: [
        for (final b in j['bars'])
          StatsBar(b['label'], b['value'], current: b['current'] ?? false),
      ],
      changePct: j['change_pct'],
      hasEnoughData: j['has_enough_data'] ?? false,
    );
  }
}
