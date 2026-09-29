import 'package:finora/domain/models/finance/finance_models.dart';
import 'package:finora/domain/models/home/home_data.dart';

abstract class HomeFacade {
  /// `GET /home`.
  Future<HomeData> getHome();

  /// Sets the current balance (`POST /onboarding/balance`).
  Future<HomeData> setBalance(num amount, {BalanceLocation? location});
}
