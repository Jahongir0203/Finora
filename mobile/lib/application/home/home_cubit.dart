import 'dart:async';

import 'package:bloc/bloc.dart';
import 'package:finora/domain/facades/finance_facade.dart';
import 'package:finora/domain/facades/home_facade.dart';
import 'package:finora/domain/models/home/home_data.dart';
import 'package:finora/infrastructure/services/cache/app_cache.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:injectable/injectable.dart';

part 'home_cubit.freezed.dart';
part 'home_state.dart';

/// Home screen data (docs/screens/HOME_SCREENS.md §3).
@Injectable()
class HomeCubit extends Cubit<HomeState> {
  final HomeFacade _home;
  final AppCache _cache;
  late final StreamSubscription<void> _financeSub;

  HomeCubit(this._home, this._cache, FinanceFacade finance)
    : super(HomeState.initial(balanceHidden: _cache.balanceHidden)) {
    // Transactions, goals and reminders added elsewhere update Home.
    _financeSub = finance.changes.listen((_) => load());
  }

  Future<void> load() async {
    emit(state.copyWith(isLoading: true));
    try {
      final data = await _home.getHome();
      if (!isClosed) emit(state.copyWith(data: data, isLoading: false));
    } catch (_) {
      if (isClosed) return;
      emit(
        state.copyWith(isLoading: false, failureTick: state.failureTick + 1),
      );
    }
  }

  void toggleBalance() {
    final hidden = !state.balanceHidden;
    emit(state.copyWith(balanceHidden: hidden));
    _cache.setBalanceHidden(hidden);
  }

  /// Returns `true` when saved.
  Future<bool> saveBalance(num amount) async {
    if (amount <= 0 || state.isSavingBalance) return false;
    emit(state.copyWith(isSavingBalance: true));
    try {
      final data = await _home.setBalance(amount);
      if (!isClosed) emit(state.copyWith(data: data, isSavingBalance: false));
      return true;
    } catch (_) {
      if (!isClosed) emit(state.copyWith(isSavingBalance: false));
      return false;
    }
  }

  @override
  Future<void> close() {
    _financeSub.cancel();
    return super.close();
  }
}
