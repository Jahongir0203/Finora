import 'package:finora/common/extensions/format_extensions.dart';
import 'package:finora/domain/facades/profile_facade.dart';
import 'package:finora/common/helpers/api_call.dart';
import 'package:auto_route/auto_route.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_empty_state.dart';
import 'package:finora/common/widgets/app_fade_in.dart';
import 'package:finora/common/widgets/app_header.dart';
import 'package:finora/common/widgets/app_list_tiles.dart';
import 'package:finora/common/widgets/app_text_field.dart';
import 'package:finora/common/widgets/app_toast.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/di.dart';
import 'package:finora/infrastructure/services/cache/app_cache.dart';
import 'package:finora/presentation/pages/auth/widgets/auth_back_button.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'language_page.dart';

/// Primary currency (docs/screens/PROFILE_SETTINGS.md §7).
///
/// TODO: rates from `GET /rates`.
@RoutePage()
class CurrencyPage extends StatefulWidget {
  const CurrencyPage({super.key});

  @override
  State<CurrencyPage> createState() => _CurrencyPageState();
}

class _CurrencyPageState extends State<CurrencyPage> {
  // (code, symbol, name, rate in UZS; null = base). Shown until the list
  // from `GET /currencies` arrives.
  static const _fallback = [
    ('UZS', "so'm", "Uzbek so'm", null),
    ('USD', r'$', 'US dollar', '12 650'),
    ('EUR', '€', 'Euro', '14 120'),
    ('RUB', '₽', 'Russian ruble', '152'),
    ('KZT', '₸', 'Kazakhstani tenge', '25'),
    ('GBP', '£', 'British pound', '16 900'),
    ('CNY', '¥', 'Chinese yuan', '1 760'),
    ('TRY', '₺', 'Turkish lira', '330'),
  ];

  final _cache = di<AppCache>();
  final _profile = di<ProfileFacade>();
  final _search = TextEditingController();
  var _currencies = _fallback;

  @override
  void initState() {
    super.initState();
    _profile.currencies().then((list) {
      if (!mounted || list.isEmpty) return;
      setState(
        () => _currencies = [
          for (final c in list)
            (c.code, c.symbol, c.name, _rate(c.rateToUzs)),
        ],
      );
    }, onError: (_) {});
  }

  static String? _rate(num? r) => r == null
      ? null
      : r >= 100
      ? r.round().toMoney()
      : r.toStringAsFixed(2);

  @override
  void dispose() {
    _search.dispose();
    super.dispose();
  }

  Future<void> _select(String code) async {
    if (!await apiRun(() => _profile.saveSettings(currency: code))) return;
    await _cache.setCurrency(code);
    if (!mounted) return;
    setState(() {});
    AppToast.success(Words.primaryCurrencySet.tr(args: [code]));
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final q = _search.text.trim().toLowerCase();
    final list = _currencies
        .where((e) => '${e.$1} ${e.$3}'.toLowerCase().contains(q))
        .toList();

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
                PushHeader(title: Words.primaryCurrency.str),
                const SizedBox(height: AppSpacing.lg),
                AppTextField.search(
                  hint: Words.searchCurrency.str,
                  controller: _search,
                  onChanged: (_) => setState(() {}),
                ),
                const SizedBox(height: AppSpacing.lg),
                if (list.isEmpty)
                  AppEmptyState(
                    icon: FinoraIcons.noResults,
                    title: Words.noCurrencyFound.str,
                    message: Words.noCurrencyFoundDesc.str,
                  )
                else
                  AppListCard(
                    padding: const .symmetric(horizontal: 16),
                    children: [
                      for (final (code, symbol, name, rate) in list)
                        OptionRow(
                          badge: Text(
                            symbol,
                            style: AppTypography.body.copyWith(
                              fontSize: 14,
                              fontWeight: .w700,
                              color: c.primaryText,
                            ),
                          ),
                          badgeSize: 44,
                          badgeRadius: AppRadius.full,
                          title: code,
                          subtitle: name,
                          trailingText: rate == null
                              ? Words.base.str
                              : '$rate UZS',
                          selected: code == _cache.currency,
                          onTap: () => _select(code),
                        ),
                    ],
                  ),
                const SizedBox(height: AppSpacing.lg),
                Padding(
                  padding: const .symmetric(horizontal: 4),
                  child: Text(
                    Words.ratesNote.str,
                    style: AppTypography.caption.copyWith(
                      height: 19 / 13,
                      color: c.textTertiary,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
