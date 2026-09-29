import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:finora/common/constants/app_env.dart';
import 'package:finora/di.dart';
import 'package:finora/domain/facades/finance_facade.dart';
import 'package:finora/infrastructure/services/cache/secure_cache.dart';
import 'package:finora/infrastructure/services/security/device_key_service.dart';
import 'package:finora/infrastructure/services/security/pin_service.dart';
import 'package:finora/presentation/routes/app_router.dart';
import 'package:injectable/injectable.dart';

/// Adds the access token and renews it with the refresh token when the
/// server answers `401 token_expired`.
///
/// Queued: while one refresh runs, other failed requests wait and then retry
/// with the new token. When the session can't be renewed the user is signed
/// out and sent to Sign in.
@Singleton()
class TokenInterceptor extends QueuedInterceptor {
  static const _retried = 'token_retried';

  final SecureCache _cache;
  final DeviceKeyService _deviceKey;
  final PinService _pins;

  TokenInterceptor(this._cache, this._deviceKey, this._pins);

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final token = await _cache.token;
    if (token.isNotEmpty) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    final response = err.response;
    if (response?.statusCode != 401 ||
        err.requestOptions.extra[_retried] == true) {
      return handler.next(err);
    }

    final code = response?.data is Map ? response!.data['code'] : null;
    if (code != 'token_expired') {
      await _endSession();
      return handler.next(err);
    }

    try {
      final sent = err.requestOptions.headers['Authorization'];
      final current = 'Bearer ${await _cache.token}';
      // Another queued request may have refreshed already.
      if (sent == current && !await _refresh()) {
        await _endSession();
        return handler.next(err);
      }
      final options = err.requestOptions
        ..extra[_retried] = true
        ..headers['Authorization'] = 'Bearer ${await _cache.token}';
      handler.resolve(await Dio(BaseOptions(baseUrl: AppEnv.baseUrl)).fetch(options));
    } on DioException catch (e) {
      handler.next(e);
    }
  }

  /// `POST /auth/refresh`, signed with the device key.
  Future<bool> _refresh() async {
    final refreshToken = await _cache.refreshToken;
    if (refreshToken == null) return false;

    const url = '${AppEnv.baseUrl}/auth/refresh';
    final body = utf8.encode(jsonEncode({'refresh_token': refreshToken}));
    try {
      final headers = await _deviceKey.sign(
        method: 'POST',
        path: Uri.parse(url).path,
        body: body,
      );
      final response = await Dio().post(
        url,
        data: Stream.fromIterable([body]),
        options: Options(
          headers: {
            ...headers,
            Headers.contentTypeHeader: Headers.jsonContentType,
            Headers.contentLengthHeader: body.length,
          },
        ),
      );
      await _cache.setTokens(
        access: response.data['access_token'],
        refresh: response.data['refresh_token'],
      );
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<void> _endSession() async {
    if ((await _cache.token).isEmpty) return;
    await _pins.clear();
    await _cache.clear();
    // Resolved lazily: FinanceFacade itself depends on this interceptor.
    di<FinanceFacade>().reset();
    router.replaceAll([SignInRoute()]);
  }
}
