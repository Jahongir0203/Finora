import 'package:finora/domain/facades/profile_facade.dart';
import 'package:finora/domain/models/profile/profile_models.dart';
import 'package:injectable/injectable.dart';

import '../services/http/api_client.dart';
import '../services/http/interceptors/api_headers_interceptor.dart';

@LazySingleton(as: ProfileFacade)
class ProfileDatasource implements ProfileFacade {
  final ApiClient _api;

  ProfileDatasource(this._api);

  @override
  Future<void> saveSettings({
    String? language,
    String? currency,
    String? theme,
    int? autoLockMinutes,
    bool? biometricEnabled,
    bool? notificationsEnabled,
  }) => _api.patch(
    '/me/settings',
    data: {
      'language': ?language,
      'currency': ?currency,
      'theme': ?theme,
      'auto_lock_minutes': ?autoLockMinutes,
      'biometric_enabled': ?biometricEnabled,
      'notifications_enabled': ?notificationsEnabled,
    },
  );

  @override
  Future<List<Currency>> currencies() async {
    final list = await _api.get('/currencies') as List;
    return [
      for (final c in list)
        Currency(
          code: c['code'],
          symbol: c['symbol'],
          name: c['name'],
          rateToUzs: num.tryParse('${c['rate_to_uzs']}'),
        ),
    ];
  }

  @override
  Future<List<FaqItem>> faq() async {
    final list =
        await _api.get(
              '/help/faq',
              query: {'lang': ApiHeadersInterceptor.language},
            )
            as List;
    return [for (final f in list) FaqItem(f['question'], f['answer'])];
  }

  @override
  Future<SupportContacts> contacts() async {
    final j = await _api.get('/help/contacts');
    return SupportContacts(
      email: j['email'],
      phone: j['phone'],
      telegram: (j['telegram'] as String).replaceFirst('@', ''),
      liveChat: j['live_chat'] ?? false,
    );
  }
}
