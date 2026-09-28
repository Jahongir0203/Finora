import 'package:finora/infrastructure/services/cache/app_cache.dart';
import 'package:injectable/injectable.dart';

/// Tracks user activity for auto-lock (PIN_SETUP_SCREENS.md §4, Auto-lock).
///
/// `AutoLockGuard` feeds it taps and lifecycle changes; the Security sheet
/// reads [remaining] for its countdown.
@LazySingleton()
class AutoLockService {
  final AppCache _cache;

  AutoLockService(this._cache);

  var _lastActivity = DateTime.now();

  /// True while the lock screen is showing.
  var locked = false;

  int get minutes => _cache.autoLockMinutes;

  Future<void> setMinutes(int value) async {
    await _cache.setAutoLockMinutes(value);
    touch();
  }

  void touch() => _lastActivity = DateTime.now();

  Duration remaining([DateTime? now]) {
    final left =
        Duration(minutes: minutes) -
        (now ?? DateTime.now()).difference(_lastActivity);
    return left.isNegative ? Duration.zero : left;
  }

  bool get expired => !locked && remaining() == Duration.zero;
}
