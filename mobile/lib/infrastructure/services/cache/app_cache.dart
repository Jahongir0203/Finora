import 'package:hive_ce/hive.dart';
import 'package:injectable/injectable.dart';

import 'cache_service.dart';

@Injectable()
class AppCache {
  final CacheService _cacheService;
  late final Box _box;

  AppCache(this._cacheService) {
    _box = _cacheService.appBox;
  }

  String get theme => _box.get('theme') ?? '';

  Future<void> setTheme(String theme) => _box.put('theme', theme);

  bool get onboardingSeen => _box.get('onboarding_seen') ?? false;

  Future<void> setOnboardingSeen() => _box.put('onboarding_seen', true);

  bool get balanceHidden => _box.get('balance_hidden') ?? false;

  Future<void> setBalanceHidden(bool value) =>
      _box.put('balance_hidden', value);

  /// Auto-lock after this many minutes of inactivity: 1, 3 or 5.
  int get autoLockMinutes => _box.get('auto_lock_minutes') ?? 1;

  Future<void> setAutoLockMinutes(int value) =>
      _box.put('auto_lock_minutes', value);

  bool get faceIdEnabled => _box.get('face_id') ?? false;

  Future<void> setFaceIdEnabled(bool value) => _box.put('face_id', value);

  String get currency => _box.get('currency') ?? 'UZS';

  Future<void> setCurrency(String value) => _box.put('currency', value);

  bool get notificationsEnabled => _box.get('notifications') ?? true;

  Future<void> setNotificationsEnabled(bool value) =>
      _box.put('notifications', value);
}
