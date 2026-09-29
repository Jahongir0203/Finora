import 'package:dartz/dartz.dart';
import 'package:finora/domain/facades/auth_facade.dart';
import 'package:finora/domain/models/auth/auth_failure.dart';
import 'package:finora/domain/models/auth/verify_result.dart';
import 'package:injectable/injectable.dart';

import '../services/cache/secure_cache.dart';
import '../services/device/device_info_service.dart';
import '../services/http/api_client.dart';
import '../services/security/device_key_service.dart';

/// `/auth/*`, `/me/pin-setup`, `/devices/current/pin-lockout`.
@LazySingleton(as: AuthFacade)
class AuthDatasource implements AuthFacade {
  final ApiClient _api;
  final SecureCache _cache;
  final DeviceKeyService _deviceKey;
  final DeviceInfoService _device;

  AuthDatasource(this._api, this._cache, this._deviceKey, this._device);

  @override
  Future<Either<AuthFailure, OtpSent>> requestOtp(
    String phone, {
    bool sms = false,
  }) async {
    try {
      final data = await _api.postPublic(
        '/auth/otp',
        data: {
          'phone': phone,
          'device_id': await _cache.deviceId,
          'channel': sms ? 'sms' : 'auto',
        },
      );
      return right(
        OtpSent(
          resendAfter: data['resend_after'],
          telegramBotUrl: data['telegram_bot_url'],
        ),
      );
    } catch (e) {
      return left(_failure(e));
    }
  }

  @override
  Future<Either<AuthFailure, VerifyResult>> verifyOtp({
    required String phone,
    required String code,
    bool pinReset = false,
  }) async {
    try {
      final data = await _api.postPublic(
        '/auth/verify',
        data: {
          'phone': phone,
          'code': code,
          'device_id': await _cache.deviceId,
          'device_name': await _device.deviceName(),
          'platform': _device.platform,
          'device_public_key': await _deviceKey.publicKey(),
          'purpose': pinReset ? 'pin_reset' : 'login',
        },
      );
      await _cache.setTokens(
        access: data['access_token'],
        refresh: data['refresh_token'],
      );
      final user = data['user'] as Map;
      await _cache.setUserName(user['first_name'] ?? '');
      return right(
        VerifyResult(
          isNewUser: user['is_new'],
          hasPin: user['has_pin_setup'],
          balanceSet: user['onboarding']?['balance_set'] ?? false,
        ),
      );
    } catch (e) {
      return left(_failure(e));
    }
  }

  @override
  Future<bool> hasSession() async => (await _cache.token).isNotEmpty;

  @override
  Future<void> pinCreated() async {
    await _api.post(
      '/me/pin-setup',
      data: {'device_id': await _cache.deviceId},
    );
  }

  @override
  Future<void> reportPinLockout() async {
    final refresh = await _cache.refreshToken;
    if (refresh == null) return;
    await _api.postSigned('/devices/current/pin-lockout', {
      'refresh_token': refresh,
    });
  }

  @override
  Future<void> logout() async {
    if (!await hasSession()) return;
    await _api.post('/auth/logout');
  }

  static AuthFailure _failure(Object e) {
    final f = toApiFailure(e);
    return switch (f.code) {
      'otp_invalid' => InvalidCodeFailure(f.attemptsLeft ?? 0),
      'otp_expired' => const ExpiredCodeFailure(),
      'rate_limited' || 'otp_blocked' => RateLimitedFailure(
        f.retryAfter ?? const Duration(minutes: 15),
      ),
      _ => UnknownAuthFailure(f.message),
    };
  }
}
