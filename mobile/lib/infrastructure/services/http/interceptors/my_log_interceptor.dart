import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:injectable/injectable.dart';

/// Logs every request, response and error: base URL, path, query and body.
@Singleton()
class MyLogInterceptor extends Interceptor {
  const MyLogInterceptor();

  static const _startKey = '@logStart@';
  static const _maxBodyLength = 4000;
  static const _encoder = JsonEncoder.withIndent('  ');

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    if (kDebugMode) {
      options.extra[_startKey] = DateTime.now();
      _print('➡️ REQUEST', [
        '${options.method} ${options.uri}',
        'Base URL: ${options.baseUrl}',
        'Path: ${options.path}',
        if (options.queryParameters.isNotEmpty)
          'Query: ${_format(options.queryParameters)}',
        if (options.data != null) 'Data: ${_format(options.data)}',
      ]);
    }
    super.onRequest(options, handler);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    if (kDebugMode) {
      final options = response.requestOptions;
      final fromCache = response.extra['@fromNetwork@'] == false;
      _print('✅ RESPONSE', [
        '${response.statusCode}${fromCache ? ' (cache)' : ''}'
            ' | ${options.method} ${options.uri}${_duration(options)}',
        'Data: ${_format(response.data)}',
      ]);
    }
    super.onResponse(response, handler);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    if (kDebugMode) {
      final options = err.requestOptions;
      final response = err.response;
      _print('❌ ERROR', [
        '${response?.statusCode ?? err.type.name}'
            ' | ${options.method} ${options.uri}${_duration(options)}',
        if (options.queryParameters.isNotEmpty)
          'Query: ${_format(options.queryParameters)}',
        if (options.data != null) 'Request data: ${_format(options.data)}',
        if (response?.data != null) 'Data: ${_format(response!.data)}',
        if (response == null && err.message != null) 'Message: ${err.message}',
      ]);
    }
    super.onError(err, handler);
  }

  static String _duration(RequestOptions options) {
    final start = options.extra[_startKey];
    if (start is! DateTime) return '';
    return ' | ${DateTime.now().difference(start).inMilliseconds} ms';
  }

  static String _format(Object? data) {
    final String text;
    if (data is Stream) {
      text = '<stream>';
    } else if (data is FormData) {
      text = _encoder.convert({
        for (final MapEntry(:key, :value) in data.fields) key: value,
        for (final MapEntry(:key, :value) in data.files)
          key: '<file ${value.filename}>',
      });
    } else if (data is Map || data is List) {
      text = _tryEncode(data);
    } else if (data is String) {
      text = _tryEncode(_tryDecode(data));
    } else {
      text = '$data';
    }
    return text.length > _maxBodyLength
        ? '${text.substring(0, _maxBodyLength)}… (${text.length} chars)'
        : text;
  }

  static Object? _tryDecode(String text) {
    try {
      return jsonDecode(text);
    } catch (_) {
      return text;
    }
  }

  static String _tryEncode(Object? data) {
    try {
      return data is String ? data : _encoder.convert(data);
    } catch (_) {
      return '$data';
    }
  }

  static void _print(String title, List<String> lines) {
    debugPrint(
      [
        '┌── $title ─────────────',
        for (final line in lines)
          for (final part in line.split('\n')) '│ $part',
        '└──────────────────────────',
      ].join('\n'),
    );
  }
}
