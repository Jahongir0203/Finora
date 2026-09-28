import 'package:auto_route/auto_route.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:finora/application/finance/finance_cubit.dart';
import 'package:finora/application/theme/theme_cubit.dart';
import 'package:finora/common/extensions/format_extensions.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_avatar.dart';
import 'package:finora/common/widgets/app_button.dart';
import 'package:finora/common/widgets/app_fade_in.dart';
import 'package:finora/common/widgets/app_header.dart';
import 'package:finora/common/widgets/app_list_tiles.dart';
import 'package:finora/common/widgets/app_switch.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/di.dart';
import 'package:finora/infrastructure/services/cache/app_cache.dart';
import 'package:finora/infrastructure/services/security/session_service.dart';
import 'package:finora/presentation/pages/auth/widgets/auth_back_button.dart';
import 'package:finora/presentation/pages/main/main_actions.dart';
import 'package:finora/presentation/routes/app_router.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'language_page.dart';
import 'widgets/security_sheet.dart';

/// Profile (docs/screens/PROFILE_SETTINGS.md §2).
@RoutePage()
class ProfilePage extends StatefulWidget {
  const ProfilePage({super.key});

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  final _cache = di<AppCache>();

  Future<void> _logout() async {
    await di<SessionService>().signOut();
    if (!mounted) return;
    context.router.replaceAll([const SignInRoute()]);
  }

  Future<void> _open(PageRouteInfo route) async {
    await context.router.navigate(route);
    if (mounted) setState(() {}); // currency / language may have changed
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final s = context.watch<FinanceCubit>().state;
    final isDark =
        context.watch<ThemeCubit>().state.themeMode == ThemeMode.dark ||
        (context.watch<ThemeCubit>().state.themeMode == ThemeMode.system &&
            context.isDark);
    final language = AppLanguage.of(context.locale).name;
    final activeReminders = s.reminders.where((r) => r.enabled).length;

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
                PushHeader(title: Words.profile.str),
                const SizedBox(height: AppSpacing.xl),
                Padding(
                  padding: const .symmetric(vertical: 8),
                  child: Column(
                    spacing: 10,
                    children: [
                      AppAvatar(name: s.userName, size: 88, fontSize: 30),
                      Column(
                        children: [
                          Text(s.userName, style: context.textStyles.title),
                          Text(
                            s.phone.toPhone(),
                            style: AppTypography.body.copyWith(
                              fontSize: 14,
                              color: c.textSecondary,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: AppSpacing.xl),
                AppListCard(
                  children: [
                    SettingsTile(
                      icon: FinoraIcons.wallet,
                      label: Words.accountsAndCards.str,
                      value: '${s.accounts.length}',
                      onTap: () => _open(const AccountsRoute()),
                    ),
                    SettingsTile(
                      icon: FinoraIcons.shapes,
                      label: Words.categories.str,
                      value: '${s.categories.length}',
                      onTap: () => _open(const CategoriesRoute()),
                    ),
                    SettingsTile(
                      icon: FinoraIcons.reminder,
                      label: Words.paymentReminders.str,
                      value: '$activeReminders',
                      onTap: () => MainActions.reminders(context),
                    ),
                    SettingsTile(
                      icon: FinoraIcons.export,
                      label: Words.exportData.str,
                      onTap: () => MainActions.export(context),
                    ),
                    SettingsTile(
                      icon: FinoraIcons.coins,
                      label: Words.primaryCurrency.str,
                      value: _cache.currency,
                      onTap: () => _open(const CurrencyRoute()),
                    ),
                    SettingsTile(
                      icon: FinoraIcons.language,
                      label: Words.language.str,
                      value: language,
                      onTap: () => _open(const LanguageRoute()),
                    ),
                    SettingsTile(
                      icon: FinoraIcons.notifications,
                      label: Words.notifications.str,
                      value: _cache.notificationsEnabled
                          ? Words.on.str
                          : Words.off.str,
                      onTap: () => MainActions.notifications(context),
                    ),
                    SettingsTile(
                      icon: FinoraIcons.security,
                      label: Words.security.str,
                      value: Words.autoLockValue.tr(
                        args: ['${_cache.autoLockMinutes}'],
                      ),
                      onTap: () async {
                        await SecuritySheet.show(context);
                        if (mounted) setState(() {});
                      },
                    ),
                    SettingsTile(
                      icon: FinoraIcons.help,
                      label: Words.helpAndSupport.str,
                      onTap: () => _open(const HelpRoute()),
                    ),
                    SettingsTile(
                      icon: FinoraIcons.darkMode,
                      label: Words.darkMode.str,
                      trailing: AppSwitch(
                        large: true,
                        value: isDark,
                        semanticLabel: Words.darkMode.str,
                        onChanged: (v) => context.read<ThemeCubit>().change(
                          v ? ThemeMode.dark : ThemeMode.light,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: AppSpacing.xl),
                AppButton.destructive(
                  text: Words.logOut.str,
                  icon: FinoraIcons.logout,
                  onPressed: _logout,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
