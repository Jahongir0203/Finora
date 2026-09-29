import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:hive_ce/hive.dart';
import 'package:injectable/injectable.dart';
import 'package:uuid/uuid.dart';

import 'cache_service.dart';

/// Tokens and device identity, stored in Keychain / Keystore.
@Singleton()
class SecureCache {
  static const _accessKey = 'token';
  static const _refreshKey = 'refresh_token';
  static const _deviceIdKey = 'device_id';
  static const _userNameKey = 'user_name';

  final CacheService _cacheService;
  late final Box _box;
  final FlutterSecureStorage _secureStorage;
  var _token = '';
  String? _deviceId;

  SecureCache(this._cacheService, this._secureStorage) {
    _box = _cacheService.secureBox;
  }

  /// Access token.
  Future<String> get token async {
    if (_token.isNotEmpty) {
      return _token;
    }
    if (_box.get('has_token', defaultValue: false)) {
      _token = await _secureStorage.read(key: _accessKey) ?? '';
    }
    return _token;
  }

  Future<String?> get refreshToken => _secureStorage.read(key: _refreshKey);

  Future<void> setTokens({
    required String access,
    required String refresh,
  }) async {
    await _box.put('has_token', true);
    await _secureStorage.write(key: _accessKey, value: access);
    await _secureStorage.write(key: _refreshKey, value: refresh);
    _token = access;
  }

  /// Installation id sent as `device_id`. Survives sign-out so the backend
  /// sees the same device.
  Future<String> get deviceId async {
    if (_deviceId != null) return _deviceId!;
    var id = await _secureStorage.read(key: _deviceIdKey);
    if (id == null) {
      id = const Uuid().v4();
      await _secureStorage.write(key: _deviceIdKey, value: id);
    }
    return _deviceId = id;
  }

  /// First name for the lock screen (before any data is loaded).
  Future<String> get userName async =>
      await _secureStorage.read(key: _userNameKey) ?? '';

  Future<void> setUserName(String name) =>
      _secureStorage.write(key: _userNameKey, value: name);

  Future<void> clear() async {
    await _box.clear();
    await _secureStorage.delete(key: _accessKey);
    await _secureStorage.delete(key: _refreshKey);
    await _secureStorage.delete(key: _userNameKey);
    _token = '';
  }
}
