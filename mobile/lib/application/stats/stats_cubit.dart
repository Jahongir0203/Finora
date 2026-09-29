import 'dart:async';

import 'package:bloc/bloc.dart';
import 'package:finora/domain/facades/finance_facade.dart';
import 'package:finora/domain/facades/stats_facade.dart';
import 'package:finora/domain/models/stats/stats_data.dart';
import 'package:injectable/injectable.dart';

class StatsState {
  final StatsPeriod period;

  /// Loaded periods; switching back shows the cached one at once.
  final Map<StatsPeriod, StatsData> data;
  final bool isLoading;
  final bool failed;

  const StatsState({
    this.period = StatsPeriod.month,
    this.data = const {},
    this.isLoading = false,
    this.failed = false,
  });

  StatsData? get current => data[period];

  StatsState copyWith({
    StatsPeriod? period,
    Map<StatsPeriod, StatsData>? data,
    bool? isLoading,
    bool? failed,
  }) => StatsState(
    period: period ?? this.period,
    data: data ?? this.data,
    isLoading: isLoading ?? this.isLoading,
    failed: failed ?? this.failed,
  );
}

/// Statistics tab (docs/screens/STATS_INSIGHTS.md §1).
@Injectable()
class StatsCubit extends Cubit<StatsState> {
  final StatsFacade _stats;
  late final StreamSubscription<void> _financeSub;

  StatsCubit(this._stats, FinanceFacade finance) : super(const StatsState()) {
    // New transactions change every period: drop the cache and reload.
    _financeSub = finance.changes.listen((_) {
      emit(state.copyWith(data: const {}));
      load();
    });
  }

  void setPeriod(StatsPeriod period) {
    if (period == state.period) return;
    emit(state.copyWith(period: period));
    if (state.current == null) load();
  }

  Future<void> load() async {
    final period = state.period;
    emit(state.copyWith(isLoading: true, failed: false));
    try {
      final data = await _stats.getStats(period);
      if (isClosed) return;
      emit(
        state.copyWith(data: {...state.data, period: data}, isLoading: false),
      );
    } catch (_) {
      if (!isClosed) emit(state.copyWith(isLoading: false, failed: true));
    }
  }

  @override
  Future<void> close() {
    _financeSub.cancel();
    return super.close();
  }
}
