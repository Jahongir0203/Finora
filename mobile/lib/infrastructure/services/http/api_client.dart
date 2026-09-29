import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/domain/models/api_failure.dart';
import 'package:finora/infrastructure/services/security/device_key_service.dart';
import 'package:injectable/injectable.dart';

import 'http_service.dart';
import 'interceptors/api_headers_interceptor.dart';

/// Finora REST API (`/v1`, docs/backend/openapi.json).
///
/// Returns decoded JSON (`Map` / `List` / `null` for 204) and throws
/// [ApiFailure] on any error.
@LazySingleton()
class ApiClient {
  final HttpService _http;
  final DeviceKeyService _deviceKey;

  ApiClient(this._http, this._deviceKey);

  late final _auth = _http.client(requiredToken: true);
  late final _public = _http.client(requiredToken: false);

  Future<dynamic> get(String path, {Map<String, dynamic>? query}) =>
      _send(() => _auth.get(path, queryParameters: _clean(query)));

  /// [idempotent] adds an `Idempotency-Key` (creating endpoints).
  Future<dynamic> post(String path, {Object? data, bool idempotent = false}) =>
      _send(
        () => _auth.post(
          path,
          data: data,
          options: Options(
            extra: {ApiHeadersInterceptor.idempotent: idempotent},
          ),
        ),
      );

  /// Raw upload (`/receipts/scan`): the body is the file itself.
  Future<dynamic> postBytes(
    String path,
    List<int> bytes, {
    required String contentType,
  }) => _send(
    () => _auth.post(
      path,
      data: Stream.fromIterable([bytes]),
      options: Options(
        contentType: contentType,
        headers: {Headers.contentLengthHeader: bytes.length},
        extra: {ApiHeadersInterceptor.idempotent: true},
      ),
    ),
  );

  Future<dynamic> patch(String path, {Object? data}) =>
      _send(() => _auth.patch(path, data: data));

  Future<dynamic> delete(String path, {Object? data}) =>
      _send(() => _auth.delete(path, data: data));

  /// Endpoints called before sign-in (`/auth/otp`, `/auth/verify`).
  Future<dynamic> postPublic(String path, {Object? data}) =>
      _send(() => _public.post(path, data: data));

  /// POST signed with the device key (`X-Device-Signature`).
  Future<dynamic> postSigned(String path, Map<String, dynamic> data) async {
    final body = utf8.encode(jsonEncode(data));
    final url = '${_public.options.baseUrl}$path';
    final headers = await _deviceKey.sign(
      method: 'POST',
      path: Uri.parse(url).path,
      body: body,
    );
    return _send(
      () => _public.post(
        path,
        data: Stream.fromIterable([body]),
        options: Options(
          headers: {
            ...headers,
            Headers.contentTypeHeader: Headers.jsonContentType,
            Headers.contentLengthHeader: body.length,
          },
        ),
      ),
    );
  }

  Future<dynamic> _send(Future<Response> Function() request) async {
    try {
      return (await request()).data;
    } catch (e) {
      throw toApiFailure(e);
    }
  }

  static Map<String, dynamic>? _clean(Map<String, dynamic>? query) =>
      query == null
      ? null
      : {
          for (final MapEntry(:key, :value) in query.entries)
            if (value != null) key: '$value',
        };
}

ApiFailure toApiFailure(Object e) {
  if (e is ApiFailure) return e;
  if (e is DioException) {
    final response = e.response;
    final data = response?.data;
    if (response != null && (response.statusCode ?? 0) > 0) {
      if (data is Map) {
        final retry = data['retry_after'];
        return ApiFailure(
          status: response.statusCode!,
          code: data['code'] ?? 'unknown',
          message: data['message'] ?? Words.happenError.str,
          attemptsLeft: data['attempts_left'],
          retryAfter: retry is int ? Duration(seconds: retry) : null,
          fields: [...?(data['fields'] as List?)?.cast<String>()],
        );
      }
      return ApiFailure(
        status: response.statusCode!,
        code: 'unknown',
        message: response.statusCode! >= 500
            ? Words.serverError.str
            : Words.happenError.str,
      );
    }
    return ApiFailure(
      status: 0,
      code: ApiFailure.network,
      message: Words.noInternet.str,
    );
  }
  return ApiFailure(status: 0, code: 'unknown', message: Words.happenError.str);
}

/// Message to show for any error thrown by a facade.
String apiErrorMessage(Object e) => toApiFailure(e).message;
