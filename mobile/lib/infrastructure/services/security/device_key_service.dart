import 'dart:convert';

import 'package:crypto/crypto.dart';
import 'package:flutter/services.dart';
import 'package:injectable/injectable.dart';

/// ECDSA P-256 device key kept in Android Keystore / iOS Secure Enclave
/// (MainActivity.kt, AppDelegate.swift). The private key never leaves the
/// device; the backend binds the session to the public key and checks
/// signed requests (backend `app/application/common/device_proof.py`).
@LazySingleton()
class DeviceKeyService {
  static const _channel = MethodChannel('uz.finora/device_key');

  /// X.509 SubjectPublicKeyInfo DER, base64url. Creates the key if needed.
  Future<String> publicKey() async {
    final der = await _channel.invokeMethod<Uint8List>('publicKey');
    return base64Url.encode(der!);
  }

  Future<void> delete() => _channel.invokeMethod('delete');

  /// Headers for a signed request.
  ///
  /// Canonical message: `METHOD\nPATH\nTIMESTAMP\nsha256hex(body)`, where
  /// [path] is the full URL path (e.g. `/v1/auth/refresh`) and [body] the
  /// exact bytes sent.
  Future<Map<String, String>> sign({
    required String method,
    required String path,
    required List<int> body,
  }) async {
    final ts = '${DateTime.now().millisecondsSinceEpoch ~/ 1000}';
    final message =
        '${method.toUpperCase()}\n$path\n$ts\n${sha256.convert(body)}';
    final signature = await _channel.invokeMethod<Uint8List>(
      'sign',
      Uint8List.fromList(utf8.encode(message)),
    );
    return {
      'X-Device-Timestamp': ts,
      'X-Device-Signature': base64Url.encode(signature!).replaceAll('=', ''),
    };
  }
}
