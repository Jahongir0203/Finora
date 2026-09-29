import 'dart:math' as math;

import 'package:auto_route/auto_route.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:finora/application/finance/finance_cubit.dart';
import 'package:finora/common/extensions/format_extensions.dart';
import 'package:finora/common/helpers/api_call.dart';
import 'package:finora/common/theme/category_icons.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_empty_state.dart';
import 'package:finora/common/widgets/app_button.dart';
import 'package:finora/common/widgets/app_fade_in.dart';
import 'package:finora/common/widgets/app_float.dart';
import 'package:finora/common/widgets/app_header.dart';
import 'package:finora/common/widgets/app_pressable.dart';
import 'package:finora/common/widgets/app_text_field.dart';
import 'package:finora/common/widgets/app_toast.dart';
import 'package:finora/common/widgets/edge_scroll_row.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/di.dart';
import 'package:finora/domain/facades/insights_facade.dart';
import 'package:finora/domain/models/insights/insight.dart';
import 'package:finora/presentation/pages/auth/widgets/auth_back_button.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';


/// AI insights (docs/screens/STATS_INSIGHTS.md §2).
@RoutePage()
class InsightsPage extends StatefulWidget {
  const InsightsPage({super.key});

  @override
  State<InsightsPage> createState() => _InsightsPageState();
}

class _InsightsPageState extends State<InsightsPage> {
  final _facade = di<InsightsFacade>();
  final _input = TextEditingController();
  final _dismissed = <String>{};

  InsightList? _list;
  var _suggestions = const <String>[];
  String? _asked;
  String? _answer;
  var _loading = false;

  @override
  void initState() {
    super.initState();
    _load();
    _facade.suggestions().then((v) {
      if (mounted) setState(() => _suggestions = v);
    }, onError: (_) {});
  }

  Future<void> _load({bool includeDismissed = false}) async {
    final list = await apiCall(
      () => _facade.getInsights(includeDismissed: includeDismissed),
    );
    if (!mounted || list == null) return;
    setState(() {
      _list = list;
      _dismissed.clear();
    });
  }

  @override
  void dispose() {
    _input.dispose();
    super.dispose();
  }

  List<Insight> get _all => _list?.items ?? const [];

  List<Insight> get _visible => _all
      .where((r) => !r.dismissed && !_dismissed.contains(r.id))
      .toList();

  bool _hidden(Insight r) => r.dismissed || _dismissed.contains(r.id);

  Future<void> _ask(String q) async {
    if (q.trim().isEmpty || _loading) return;
    FocusScope.of(context).unfocus();
    _input.clear();
    setState(() {
      _asked = q.trim();
      _answer = null;
      _loading = true;
    });
    final answer = await apiCall(() => _facade.ask(_asked!));
    if (!mounted) return;
    setState(() {
      _loading = false;
      _answer = answer;
      if (answer == null) _asked = null;
    });
  }

  void _dismiss(Insight r) {
    setState(() => _dismissed.add(r.id));
    apiRun(() => _facade.dismiss(r.id));
  }

  Future<void> _act(Insight r) async {
    setState(() => _dismissed.add(r.id));
    if (!await apiRun(() => _facade.act(r.id))) {
      if (mounted) setState(() => _dismissed.remove(r.id));
      return;
    }
    AppToast.success(switch (r.action) {
      .remindMe => Words.reminderSetTuesdays.str,
      .turnOn => Words.autoSaveTurnedOn.str,
      _ => Words.doneWeWillTrack.str,
    });
    // A budget, reminder or auto-save was created on the server.
    if (mounted) context.read<FinanceCubit>().load();
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final visible = _visible;
    // Tips handled here no longer count towards the server's estimate.
    final potential =
        (_list?.potentialSaving ?? 0) -
        _all
            .where((r) => !r.dismissed && _dismissed.contains(r.id))
            .fold<num>(0, (s, r) => s + (r.saving ?? 0));

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
                PushHeader(
                  title: Words.aiInsights.str,
                  trailing: const _BetaBadge(),
                ),
                const SizedBox(height: AppSpacing.lg),
                _Hero(amount: potential, tips: visible.length),
                const SizedBox(height: AppSpacing.lg),
                _ChatCard(
                  controller: _input,
                  asked: _asked,
                  answer: _answer,
                  loading: _loading,
                  suggestions: _suggestions,
                  onAsk: _ask,
                ),
                const SizedBox(height: AppSpacing.lg),
                SectionLabel(
                  Words.recommendations.str,
                  padding: const .symmetric(horizontal: 4),
                ),
                const SizedBox(height: AppSpacing.sm),
                for (final (i, r) in _all.indexed)
                  AnimatedSize(
                    key: ValueKey(r.id),
                    duration: AppMotion.fast,
                    curve: AppMotion.ease,
                    child: _hidden(r)
                        ? const SizedBox(width: double.infinity)
                        : Padding(
                            padding: const .only(bottom: AppSpacing.md),
                            child: AppFadeIn(
                              index: i,
                              step: const Duration(milliseconds: 70),
                              child: _RecommendationCard(
                                rec: r,
                                onDismiss: () => _dismiss(r),
                                onAction: () => _act(r),
                              ),
                            ),
                          ),
                  ),
                if (_list != null && visible.isEmpty)
                  AppEmptyState(
                    icon: FinoraIcons.empty,
                    title: Words.youreAllSet.str,
                    message: Words.youreAllSetDesc.str,
                    action: AppButton.secondary(
                      text: Words.showDismissed.str,
                      size: AppButtonSize.small,
                      expanded: false,
                      onPressed: () => _load(includeDismissed: true),
                    ),
                  ),
                const SizedBox(height: AppSpacing.sm),
                Text(
                  Words.aiDisclaimer.str,
                  textAlign: .center,
                  style: AppTypography.caption.copyWith(
                    fontSize: 12,
                    color: c.textTertiary,
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

class _BetaBadge extends StatelessWidget {
  const _BetaBadge();

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Container(
      height: 28,
      padding: const .symmetric(horizontal: 10),
      decoration: BoxDecoration(
        color: c.tint,
        borderRadius: .circular(AppRadius.full),
      ),
      child: Row(
        mainAxisSize: .min,
        spacing: 4,
        children: [
          Icon(FinoraIcons.ai, size: 14, color: c.primaryText),
          Text(
            Words.beta.str,
            style: AppTypography.label.copyWith(
              letterSpacing: 0,
              color: c.primaryText,
            ),
          ),
        ],
      ),
    );
  }
}

class _Hero extends StatelessWidget {
  final num amount;
  final int tips;

  const _Hero({required this.amount, required this.tips});

  @override
  Widget build(BuildContext context) {
    const sub = TextStyle(color: AppPalette.primary200);

    return ClipRRect(
      borderRadius: .circular(AppRadius.x2l),
      child: Container(
        color: AppPalette.primary900,
        child: Stack(
          children: [
            Positioned(
              right: -40,
              top: -50,
              child: AppFloat(
                period: const Duration(seconds: 5),
                child: Container(
                  width: 170,
                  height: 170,
                  decoration: BoxDecoration(
                    color: AppPalette.primary500.withValues(alpha: 0.18),
                    shape: BoxShape.circle,
                  ),
                ),
              ),
            ),
            Padding(
              padding: const .all(20),
              child: Column(
                crossAxisAlignment: .start,
                spacing: AppSpacing.sm,
                children: [
                  Text(
                    Words.potentialSavings.str.toUpperCase(),
                    style: AppTypography.label.copyWith(
                      color: AppPalette.primary200,
                    ),
                  ),
                  Text.rich(
                    TextSpan(
                      text: amount.toMoney(),
                      style: AppTypography.display.copyWith(
                        color: AppPalette.white,
                      ),
                      children: [
                        TextSpan(
                          text: ' ${AppFormat.currency}',
                          style: AppTypography.body.copyWith(
                            fontWeight: .w500,
                            color: AppPalette.primary200,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Text(
                    Words.basedOnLast90.tr(args: ['$tips']),
                    style: AppTypography.body
                        .copyWith(fontSize: 14, height: 20 / 14)
                        .merge(sub),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ChatCard extends StatelessWidget {
  final TextEditingController controller;
  final String? asked;
  final String? answer;
  final bool loading;
  final List<String> suggestions;
  final ValueChanged<String> onAsk;

  const _ChatCard({
    required this.controller,
    required this.asked,
    required this.answer,
    required this.loading,
    required this.suggestions,
    required this.onAsk,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final bubble = AppTypography.body.copyWith(fontSize: 14, height: 20 / 14);

    return Container(
      padding: const .all(14),
      decoration: BoxDecoration(
        color: c.surface,
        borderRadius: .circular(AppRadius.xl),
        border: Border.all(color: c.border),
      ),
      child: Column(
        crossAxisAlignment: .stretch,
        spacing: AppSpacing.md,
        children: [
          Row(
            spacing: AppSpacing.sm,
            children: [
              Icon(
                FinoraIcons.message,
                size: AppSizes.iconTrailing,
                color: c.primaryText,
              ),
              Text(
                Words.askFinoraAi.str,
                style: AppTypography.body.copyWith(
                  fontWeight: .w600,
                  color: c.textPrimary,
                ),
              ),
            ],
          ),
          EdgeScrollRow(
            height: 34,
            inset: 14,
            children: [
              for (final q in suggestions)
                AppPressable(
                  onTap: () => onAsk(q),
                  child: Container(
                    height: 34,
                    padding: const .symmetric(horizontal: 12),
                    alignment: .center,
                    decoration: BoxDecoration(
                      color: c.tint,
                      borderRadius: .circular(AppRadius.full),
                    ),
                    child: Text(
                      q,
                      style: AppTypography.bodyMedium.copyWith(
                        fontSize: 13,
                        color: c.primaryText,
                      ),
                    ),
                  ),
                ),
            ],
          ),
          if (asked != null) ...[
            Align(
              alignment: AlignmentDirectional.centerEnd,
              child: FractionallySizedBox(
                widthFactor: 0.8,
                alignment: AlignmentDirectional.centerEnd,
                child: Align(
                  alignment: AlignmentDirectional.centerEnd,
                  child: Container(
                    padding: const .symmetric(horizontal: 12, vertical: 10),
                    decoration: const BoxDecoration(
                      color: AppPalette.primary500,
                      borderRadius: .only(
                        topLeft: .circular(16),
                        topRight: .circular(16),
                        bottomLeft: .circular(16),
                        bottomRight: .circular(4),
                      ),
                    ),
                    child: Text(
                      asked!,
                      style: bubble.copyWith(color: AppPalette.primary950),
                    ),
                  ),
                ),
              ),
            ),
            Row(
              crossAxisAlignment: .start,
              spacing: AppSpacing.sm,
              children: [
                Container(
                  width: 28,
                  height: 28,
                  alignment: .center,
                  decoration: BoxDecoration(
                    color: AppPalette.primary900,
                    borderRadius: .circular(9),
                  ),
                  child: const Icon(
                    FinoraIcons.ai,
                    size: 14,
                    color: AppPalette.primary200,
                  ),
                ),
                Flexible(
                  child: Container(
                    padding: const .symmetric(horizontal: 12, vertical: 10),
                    decoration: BoxDecoration(
                      color: c.background,
                      borderRadius: const .only(
                        topLeft: .circular(16),
                        topRight: .circular(16),
                        bottomLeft: .circular(4),
                        bottomRight: .circular(16),
                      ),
                    ),
                    child: loading
                        ? const _TypingDots()
                        : AppFadeIn(
                            duration: const Duration(milliseconds: 400),
                            child: Text(
                              answer ?? '',
                              style: bubble.copyWith(
                                height: 21 / 14,
                                color: c.textPrimary,
                              ),
                            ),
                          ),
                  ),
                ),
              ],
            ),
          ],
          Container(
            height: 46,
            padding: const .only(left: 14, right: 5),
            decoration: BoxDecoration(
              color: c.background,
              borderRadius: .circular(AppRadius.md),
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: controller,
                    textInputAction: TextInputAction.send,
                    onSubmitted: onAsk,
                    style: context.textStyles.body,
                    decoration: bareInputDecoration(hint: Words.askAboutSpending.str,
                      hintStyle: AppTypography.body.copyWith(
                        color: c.textTertiary,
                      ),
                    ),
                  ),
                ),
                AppPressable(
                  onTap: () => onAsk(controller.text),
                  semanticLabel: Words.send.str,
                  child: Container(
                    width: 36,
                    height: 36,
                    alignment: .center,
                    decoration: BoxDecoration(
                      color: AppPalette.primary500,
                      borderRadius: .circular(AppRadius.sm),
                    ),
                    child: const Icon(
                      FinoraIcons.arrowUp,
                      size: 18,
                      color: AppPalette.primary950,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/// `fnDot`: three 7px dots bouncing with 0 / .15 / .3s delays.
class _TypingDots extends StatefulWidget {
  const _TypingDots();

  @override
  State<_TypingDots> createState() => _TypingDotsState();
}

class _TypingDotsState extends State<_TypingDots>
    with SingleTickerProviderStateMixin {
  late final _c = AnimationController(
    vsync: this,
    duration: const Duration(seconds: 1),
  )..repeat();

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final color = context.appColors.textTertiary;

    return SizedBox(
      height: 20,
      child: AnimatedBuilder(
        animation: _c,
        builder: (_, _) => Row(
          mainAxisSize: .min,
          spacing: 4,
          children: [
            for (var i = 0; i < 3; i++)
              Transform.translate(
                offset: Offset(
                  0,
                  -3 *
                      math.max(
                        0,
                        math.sin((_c.value - i * 0.15) * math.pi * 2),
                      ),
                ),
                child: Container(
                  width: 7,
                  height: 7,
                  decoration: BoxDecoration(
                    color: color,
                    shape: BoxShape.circle,
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _RecommendationCard extends StatelessWidget {
  final Insight rec;
  final VoidCallback onDismiss;
  final VoidCallback onAction;

  const _RecommendationCard({
    required this.rec,
    required this.onDismiss,
    required this.onAction,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final category = context.select(
      (FinanceCubit b) =>
          rec.categoryId == null ? null : b.state.category(rec.categoryId!),
    );
    final color = category?.colorValue ?? AppPalette.primary500;
    final icon = CategoryIcons.of(rec.icon);
    final label = switch (rec.action) {
      .setBudget => Words.setBudget.str,
      .remindMe => Words.remindMe.str,
      .review => Words.review.str,
      .turnOn => Words.turnOn.str,
    };

    return Container(
      padding: const .all(16),
      decoration: BoxDecoration(
        color: c.surface,
        borderRadius: .circular(AppRadius.xl),
        border: Border.all(color: c.border),
      ),
      child: Column(
        spacing: AppSpacing.md,
        children: [
          Row(
            crossAxisAlignment: .start,
            spacing: AppSpacing.md,
            children: [
              Container(
                width: 40,
                height: 40,
                alignment: .center,
                decoration: BoxDecoration(
                  color: AppPalette.tintOf(color),
                  borderRadius: .circular(12),
                ),
                child: Icon(icon, size: AppSizes.iconMd, color: color),
              ),
              Expanded(
                child: Column(
                  crossAxisAlignment: .start,
                  spacing: 2,
                  children: [
                    Text(
                      rec.title,
                      style: AppTypography.body.copyWith(
                        fontWeight: .w600,
                        color: c.textPrimary,
                      ),
                    ),
                    Text(
                      rec.body,
                      style: AppTypography.body.copyWith(
                        fontSize: 14,
                        height: 20 / 14,
                        color: c.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          Row(
            children: [
              if (rec.saving != null)
                Container(
                  height: 28,
                  padding: const .symmetric(horizontal: 10),
                  alignment: .center,
                  decoration: BoxDecoration(
                    color: c.tint,
                    borderRadius: .circular(AppRadius.full),
                  ),
                  child: Text(
                    '${AppFormat.minus}${rec.saving!.toMoney()}',
                    style: AppTypography.label.copyWith(
                      fontWeight: .w700,
                      letterSpacing: 0,
                      color: c.primaryText,
                      fontFeatures: const [FontFeature.tabularFigures()],
                    ),
                  ),
                ),
              const Spacer(),
              AppPressable(
                onTap: onDismiss,
                child: SizedBox(
                  height: 36,
                  child: Padding(
                    padding: const .symmetric(horizontal: 12),
                    child: Center(
                      child: Text(
                        Words.dismiss.str,
                        style: AppTypography.bodyMedium.copyWith(
                          fontSize: 14,
                          color: c.textSecondary,
                        ),
                      ),
                    ),
                  ),
                ),
              ),
              AppPressable(
                onTap: onAction,
                child: Container(
                  height: 36,
                  padding: const .symmetric(horizontal: 14),
                  alignment: .center,
                  decoration: BoxDecoration(
                    color: c.textPrimary,
                    borderRadius: .circular(12),
                  ),
                  child: Text(
                    label,
                    style: AppTypography.button.copyWith(
                      fontSize: 14,
                      color: c.surface,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
