import 'package:finora/domain/models/home/home_data.dart';

abstract class HomeFacade {
  /// `GET /home`.
  Future<HomeData> getHome();

  /// Sets the current balance (cash and cards combined).
  Future<HomeData> setBalance(num amount);
}
