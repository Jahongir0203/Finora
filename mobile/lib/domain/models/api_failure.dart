/// Backend error (`ErrorOut`, docs/backend/ERROR_CODES.md).
///
/// UI decides by [code]; [message] is already localized by the server.
class ApiFailure implements Exception {
  /// HTTP status, 0 for network errors.
  final int status;
  final String code;
  final String message;
  final int? attemptsLeft;
  final Duration? retryAfter;
  final List<String> fields;

  const ApiFailure({
    required this.status,
    required this.code,
    required this.message,
    this.attemptsLeft,
    this.retryAfter,
    this.fields = const [],
  });

  static const network = 'network_error';

  bool get isNetwork => code == network;

  @override
  String toString() => 'ApiFailure($status, $code, $message)';
}
