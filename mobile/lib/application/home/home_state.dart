part of 'home_cubit.dart';

@freezed
abstract class HomeState with _$HomeState {
  const factory HomeState.initial({
    HomeData? data,
    @Default(false) bool isLoading,
    @Default(false) bool isSavingBalance,
    @Default(false) bool balanceHidden,

    /// Incremented when loading fails.
    @Default(0) int failureTick,
  }) = _Initial;
}
