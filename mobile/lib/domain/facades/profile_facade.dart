import 'package:finora/domain/models/profile/profile_models.dart';

/// Profile, settings and help (`/me`, `/me/settings`, `/currencies`, `/help`).
abstract class ProfileFacade {
  /// `PATCH /me/settings`: only the given values change.
  Future<void> saveSettings({
    String? language,
    String? currency,

    /// `light` / `dark` / `system`.
    String? theme,
    int? autoLockMinutes,
    bool? biometricEnabled,
    bool? notificationsEnabled,
  });

  Future<List<Currency>> currencies();

  /// In the current UI language.
  Future<List<FaqItem>> faq();

  Future<SupportContacts> contacts();
}
