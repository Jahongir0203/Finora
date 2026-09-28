import 'dart:convert';
import 'dart:math';

import 'package:crypto/crypto.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:injectable/injectable.dart';

/// Stores the 4-digit PIN as a salted SHA-256 hash in secure storage and
/// counts failed attempts (docs/screens/PIN_SETUP_SCREENS.md).
///
/// The PIN itself is never stored or logged.
@LazySingleton()
class PinService {
  static const maxAttempts = 5;

  /// Rejected at creation: too easy to guess.
  static const weakPins = {'1234', '0000', '1111', '4321', '1212', '2580'};

  static const _hashKey = 'pin_hash';
  static const _saltKey = 'pin_salt';
  static const _attemptsKey = 'pin_attempts';

  final FlutterSecureStorage _storage;

  PinService(this._storage);

  Future<bool> hasPin() async => (await _storage.read(key: _hashKey)) != null;

  Future<void> setPin(String pin) async {
    final salt = base64Encode(
      List.generate(16, (_) => Random.secure().nextInt(256)),
    );
    await _storage.write(key: _saltKey, value: salt);
    await _storage.write(key: _hashKey, value: _hash(pin, salt));
    await _storage.delete(key: _attemptsKey);
  }

  /// Returns attempts left after a wrong PIN, or `null` when correct.
  Future<int?> verify(String pin) async {
    final salt = await _storage.read(key: _saltKey) ?? '';
    final hash = await _storage.read(key: _hashKey);
    if (hash != null && hash == _hash(pin, salt)) {
      await _storage.delete(key: _attemptsKey);
      return null;
    }
    final failed = int.parse(await _storage.read(key: _attemptsKey) ?? '0') + 1;
    await _storage.write(key: _attemptsKey, value: '$failed');
    return maxAttempts - failed;
  }

  Future<void> clear() async {
    await _storage.delete(key: _hashKey);
    await _storage.delete(key: _saltKey);
    await _storage.delete(key: _attemptsKey);
  }

  static String _hash(String pin, String salt) =>
      sha256.convert(utf8.encode('$salt:$pin')).toString();
}
