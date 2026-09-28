import 'package:auto_route/auto_route.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_fade_in.dart';
import 'package:finora/common/widgets/app_header.dart';
import 'package:finora/common/widgets/app_list_tiles.dart';
import 'package:finora/common/widgets/app_pressable.dart';
import 'package:finora/common/widgets/app_toast.dart';
import 'package:finora/common/widgets/radio_dot.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/presentation/pages/auth/widgets/auth_back_button.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Languages listed on the Language screen (PROFILE_SETTINGS.md §6).
enum AppLanguage {
  en('EN', 'English', 'English', Locale('en', 'US')),
  uz('UZ', "O'zbekcha", 'Uzbek · Latin', Locale('uz', 'UZ')),
  uzCyrl('ЎЗ', 'Ўзбекча', 'Uzbek · Cyrillic', null),
  ru('RU', 'Русский', 'Russian', Locale('ru', 'RU')),
  kk('KZ', 'Қазақша', 'Kazakh', null),
  tr('TR', 'Türkçe', 'Turkish', null);

  final String code;
  final String name;
  final String sub;

  /// `null` = no translation yet.
  final Locale? locale;

  const AppLanguage(this.code, this.name, this.sub, this.locale);

  static AppLanguage of(Locale locale) => values.firstWhere(
    (e) => e.locale?.languageCode == locale.languageCode,
    orElse: () => en,
  );
}

/// Language (docs/screens/PROFILE_SETTINGS.md §6).
@RoutePage()
class LanguagePage extends StatelessWidget {
  const LanguagePage({super.key});

  Future<void> _select(BuildContext context, AppLanguage lang) async {
    final locale = lang.locale;
    // TODO: add translations for Uzbek Cyrillic, Kazakh and Turkish.
    if (locale == null) return AppToast.info(Words.soon.str);
    await context.setLocale(locale);
    AppToast.success(Words.languageSet.tr(args: [lang.name]));
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final current = AppLanguage.of(context.locale);

    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: authOverlayStyle(
        context,
      ).copyWith(systemNavigationBarColor: c.background),
      child: Scaffold(
        backgroundColor: c.background,
        body: SafeArea(
          bottom: false,
          child: AppFadeIn(
            horizontal: true,
            child: ListView(
              padding: .fromLTRB(
                20,
                8,
                20,
                28 + MediaQuery.paddingOf(context).bottom,
              ),
              children: [
                PushHeader(title: Words.language.str),
                const SizedBox(height: AppSpacing.lg),
                Padding(
                  padding: const .symmetric(horizontal: 4),
                  child: Text(
                    Words.languageDesc.str,
                    style: AppTypography.body.copyWith(
                      fontSize: 14,
                      height: 20 / 14,
                      color: c.textSecondary,
                    ),
                  ),
                ),
                const SizedBox(height: AppSpacing.lg),
                AppListCard(
                  padding: const .symmetric(horizontal: 16),
                  children: [
                    for (final (i, lang) in AppLanguage.values.indexed)
                      AppFadeIn(
                        index: i,
                        step: const Duration(milliseconds: 40),
                        child: OptionRow(
                          badge: Text(
                            lang.code,
                            style: AppTypography.caption.copyWith(
                              fontWeight: .w700,
                              color: c.primaryText,
                            ),
                          ),
                          badgeRadius: 12,
                          title: lang.name,
                          subtitle: lang.sub,
                          selected: lang == current,
                          onTap: () => _select(context, lang),
                        ),
                      ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Shared by Language and Currency.
class OptionRow extends StatelessWidget {
  final Widget badge;
  final double badgeRadius;
  final double badgeSize;
  final String title;
  final String subtitle;
  final String? trailingText;
  final bool selected;
  final VoidCallback onTap;

  const OptionRow({
    super.key,
    required this.badge,
    required this.title,
    required this.subtitle,
    required this.selected,
    required this.onTap,
    this.badgeRadius = 12,
    this.badgeSize = 40,
    this.trailingText,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Semantics(
      selected: selected,
      child: AppPressable(
        onTap: onTap,
        scale: AppMotion.pressScaleCard,
        child: SizedBox(
          height: 64,
          child: Row(
            spacing: AppSpacing.md,
            children: [
              Container(
                width: badgeSize,
                height: badgeSize,
                alignment: .center,
                decoration: BoxDecoration(
                  color: c.tint,
                  borderRadius: .circular(badgeRadius),
                ),
                child: badge,
              ),
              Expanded(
                child: Column(
                  mainAxisAlignment: .center,
                  crossAxisAlignment: .start,
                  children: [
                    Text(
                      title,
                      style: AppTypography.body.copyWith(
                        fontWeight: .w600,
                        color: c.textPrimary,
                      ),
                    ),
                    Text(
                      subtitle,
                      style: AppTypography.caption.copyWith(
                        color: c.textTertiary,
                      ),
                    ),
                  ],
                ),
              ),
              if (trailingText != null)
                Text(
                  trailingText!,
                  style: AppTypography.caption.copyWith(
                    color: c.textTertiary,
                    fontFeatures: const [FontFeature.tabularFigures()],
                  ),
                ),
              RadioDot(selected: selected),
            ],
          ),
        ),
      ),
    );
  }
}
