import 'package:dio/dio.dart';
import 'package:flutter_timezone/flutter_timezone.dart';
import 'package:injectable/injectable.dart';
import 'package:uuid/uuid.dart';

/// `Accept-Language`, `X-Timezone` and `Idempotency-Key` for every API call.
@Singleton()
class ApiHeadersInterceptor extends Interceptor {
  /// Set `extra: {idempotent: true}` on creating POSTs: retries with the same
  /// key never create a second record.
  static const idempotent = 'idempotent';

  /// Current UI language; `MyApp` keeps it in sync.
  static var language = 'en';

  static var _timezone = 'Asia/Tashkent';

  static Future<void> loadTimezone() async {
    try {
      _timezone = (await FlutterTimezone.getLocalTimezone()).identifier;
    } catch (_) {
      // Keep the default: the backend falls back to Tashkent too.
    }
  }

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    options.headers.addAll({
      'Accept-Language': language,
      'X-Timezone': _timezone,
    });
    if (options.extra[idempotent] == true &&
        !options.headers.containsKey('Idempotency-Key')) {
      options.headers['Idempotency-Key'] = const Uuid().v4();
    }
    handler.next(options);
  }
}
