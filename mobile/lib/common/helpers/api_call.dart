import 'package:finora/common/widgets/app_toast.dart';
import 'package:finora/infrastructure/services/http/api_client.dart';

/// Runs an API action from the UI; on failure shows the server's (already
/// localized) message and returns `null`.
Future<T?> apiCall<T>(Future<T> Function() action) async {
  try {
    return await action();
  } catch (e) {
    AppToast.error(apiErrorMessage(e));
    return null;
  }
}

/// [apiCall] for actions without a result: `true` when it succeeded.
Future<bool> apiRun(Future<void> Function() action) async =>
    await apiCall(() async {
      await action();
      return true;
    }) ??
    false;
