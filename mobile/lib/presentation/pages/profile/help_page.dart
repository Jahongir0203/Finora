import 'package:finora/di.dart';
import 'package:finora/common/extensions/format_extensions.dart';
import 'package:finora/domain/models/profile/profile_models.dart';
import 'package:finora/domain/facades/profile_facade.dart';
import 'package:auto_route/auto_route.dart';
import 'package:finora/application/device_info/device_info_cubit.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_button.dart';
import 'package:finora/common/widgets/app_empty_state.dart';
import 'package:finora/common/widgets/app_fade_in.dart';
import 'package:finora/common/widgets/app_header.dart';
import 'package:finora/common/widgets/app_pressable.dart';
import 'package:finora/common/widgets/app_text_field.dart';
import 'package:finora/common/widgets/app_toast.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/presentation/pages/auth/widgets/auth_back_button.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:url_launcher/url_launcher.dart';

/// Help & support (docs/screens/PROFILE_SETTINGS.md §8).
@RoutePage()
class HelpPage extends StatefulWidget {
  const HelpPage({super.key});

  @override
  State<HelpPage> createState() => _HelpPageState();
}

class _HelpPageState extends State<HelpPage> {
  // Shown until `GET /help/faq` answers (or when it fails).
  static const _fallbackFaqs = [
    (
      'How do I add a card?',
      'Open Profile → Accounts & cards and tap +. Enter the card number and confirm with the SMS code from your bank.',
    ),
    (
      'Is my data safe?',
      'Your data is encrypted on the device and on our servers. The app is protected by your PIN or Face ID, and Finora never shares your transactions with anyone.',
    ),
    (
      'How do payment reminders work?',
      'Add a bill in Payment reminders with its amount, due date and how often it repeats. We notify you on the day you choose: the same day, 1 day or 3 days before.',
    ),
    (
      'How do I export my transactions?',
      'Tap the download button on Activity or Statistics, or open Profile → Export data. Pick a period and a format: PDF, Excel or CSV.',
    ),
    (
      'Can I change my primary currency?',
      'Yes. Open Profile → Primary currency and pick a new one. Past transactions keep the rate from the day they were made.',
    ),
  ];

  final _search = TextEditingController();
  int? _open = 0;
  var _faqs = _fallbackFaqs;
  var _contacts = const SupportContacts(
    email: 'help@finora.uz',
    phone: '+998712000000',
    telegram: 'finora_support',
    liveChat: false,
  );

  @override
  void initState() {
    super.initState();
    final profile = di<ProfileFacade>();
    profile.faq().then((list) {
      if (!mounted || list.isEmpty) return;
      setState(
        () => _faqs = [for (final f in list) (f.question, f.answer)],
      );
    }, onError: (_) {});
    profile.contacts().then((v) {
      if (mounted) setState(() => _contacts = v);
    }, onError: (_) {});
  }

  @override
  void dispose() {
    _search.dispose();
    super.dispose();
  }

  Future<void> _launch(String url) async {
    final ok = await launchUrl(
      Uri.parse(url),
      mode: LaunchMode.externalApplication,
    );
    if (!ok) AppToast.error(Words.happenError.str);
  }

  void _liveChat() => AppToast.info(Words.soon.str);

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final q = _search.text.trim().toLowerCase();
    final faqs = [
      for (final (i, f) in _faqs.indexed)
        if (q.isEmpty || '${f.$1} ${f.$2}'.toLowerCase().contains(q)) (i, f),
    ];
    final info = context.watch<DeviceInfoCubit>().state.projectInfo;

    final contacts = [
      (
        FinoraIcons.message,
        AppPalette.primary500,
        Words.liveChat.str,
        Words.repliesIn.str,
        _liveChat,
      ),
      (
        FinoraIcons.send,
        AppPalette.catTransfer,
        'Telegram',
        '@${_contacts.telegram}',
        () => _launch('https://t.me/${_contacts.telegram}'),
      ),
      (
        FinoraIcons.phone,
        AppPalette.catBills,
        Words.callUs.str,
        _contacts.phone.toPhone(),
        () => _launch('tel:${_contacts.phone}'),
      ),
      (
        FinoraIcons.mail,
        AppPalette.catFood,
        Words.email.str,
        _contacts.email,
        () => _launch('mailto:${_contacts.email}'),
      ),
    ];

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
                PushHeader(title: Words.helpAndSupport.str),
                const SizedBox(height: AppSpacing.lg),
                Container(
                  padding: const .all(20),
                  decoration: BoxDecoration(
                    color: AppPalette.primary900,
                    borderRadius: .circular(AppRadius.x2l),
                  ),
                  child: Column(
                    crossAxisAlignment: .stretch,
                    spacing: 14,
                    children: [
                      Text(
                        Words.howCanWeHelp.str,
                        style: AppTypography.title.copyWith(
                          color: AppPalette.white,
                        ),
                      ),
                      Container(
                        height: 48,
                        padding: const .symmetric(horizontal: 14),
                        decoration: BoxDecoration(
                          color: AppPalette.heroBlock,
                          borderRadius: .circular(AppRadius.md),
                        ),
                        child: Row(
                          spacing: 10,
                          children: [
                            const Icon(
                              FinoraIcons.search,
                              size: AppSizes.iconTrailing,
                              color: AppPalette.primary200,
                            ),
                            Expanded(
                              child: TextField(
                                controller: _search,
                                onChanged: (_) => setState(() => _open = null),
                                cursorColor: AppPalette.primary200,
                                style: AppTypography.body.copyWith(
                                  color: AppPalette.white,
                                ),
                                decoration: bareInputDecoration(hint: Words.searchQuestions.str,
                                  hintStyle: AppTypography.body.copyWith(
                                    color: AppPalette.primary200.withValues(
                                      alpha: 0.6,
                                    ),
                                  ),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: AppSpacing.lg),
                GridView.count(
                  crossAxisCount: 2,
                  mainAxisSpacing: 10,
                  crossAxisSpacing: 10,
                  childAspectRatio: 1.45,
                  shrinkWrap: true,
                  padding: EdgeInsets.zero,
                  physics: const NeverScrollableScrollPhysics(),
                  children: [
                    for (final (icon, color, title, sub, onTap) in contacts)
                      AppPressable(
                        onTap: onTap,
                        scale: 0.97,
                        child: Container(
                          padding: const .all(14),
                          decoration: BoxDecoration(
                            color: c.surface,
                            borderRadius: .circular(AppRadius.xl),
                            border: Border.all(color: c.border),
                          ),
                          child: Column(
                            crossAxisAlignment: .start,
                            children: [
                              Container(
                                width: 40,
                                height: 40,
                                alignment: .center,
                                decoration: BoxDecoration(
                                  color: AppPalette.tintOf(color),
                                  borderRadius: .circular(12),
                                ),
                                child: Icon(
                                  icon,
                                  size: AppSizes.iconMd,
                                  color: color,
                                ),
                              ),
                              const Spacer(),
                              Text(
                                title,
                                style: AppTypography.body.copyWith(
                                  fontWeight: .w600,
                                  color: c.textPrimary,
                                ),
                              ),
                              Text(
                                sub,
                                maxLines: 1,
                                overflow: .ellipsis,
                                style: AppTypography.caption.copyWith(
                                  fontSize: 12,
                                  color: c.textTertiary,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: AppSpacing.lg),
                SectionLabel(
                  Words.frequentlyAsked.str,
                  padding: const .symmetric(horizontal: 4),
                ),
                const SizedBox(height: AppSpacing.sm),
                if (faqs.isEmpty)
                  AppEmptyState(
                    icon: FinoraIcons.noResults,
                    title: Words.noMatchingQuestions.str,
                    message: Words.noMatchingQuestionsDesc.str,
                    action: AppButton(
                      text: Words.startLiveChat.str,
                      size: AppButtonSize.small,
                      expanded: false,
                      onPressed: _liveChat,
                    ),
                  )
                else
                  Container(
                    padding: const .symmetric(horizontal: 16),
                    decoration: BoxDecoration(
                      color: c.surface,
                      borderRadius: .circular(AppRadius.xl),
                      border: Border.all(color: c.border),
                    ),
                    child: Column(
                      children: [
                        for (final (j, (i, (question, answer))) in faqs.indexed)
                          _FaqTile(
                            question: question,
                            answer: answer,
                            divided: j > 0,
                            open: _open == i,
                            onTap: () =>
                                setState(() => _open = _open == i ? null : i),
                          ),
                      ],
                    ),
                  ),
                const SizedBox(height: AppSpacing.lg),
                Text(
                  'Finora ${info.version} (${info.buildNumber})',
                  textAlign: .center,
                  style: AppTypography.caption.copyWith(color: c.textTertiary),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _FaqTile extends StatelessWidget {
  final String question;
  final String answer;
  final bool divided;
  final bool open;
  final VoidCallback onTap;

  const _FaqTile({
    required this.question,
    required this.answer,
    required this.divided,
    required this.open,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Container(
      decoration: divided
          ? BoxDecoration(
              border: Border(top: BorderSide(color: c.divider)),
            )
          : null,
      child: Column(
        crossAxisAlignment: .stretch,
        children: [
          Semantics(
            button: true,
            expanded: open,
            child: GestureDetector(
              behavior: HitTestBehavior.opaque,
              onTap: onTap,
              child: ConstrainedBox(
                constraints: const BoxConstraints(minHeight: 56),
                child: Row(
                  spacing: AppSpacing.md,
                  children: [
                    Expanded(
                      child: Text(
                        question,
                        style: context.textStyles.bodyMedium,
                      ),
                    ),
                    AnimatedRotation(
                      turns: open ? 0.5 : 0,
                      duration: AppMotion.fade,
                      child: Icon(
                        FinoraIcons.chevronDown,
                        size: AppSizes.iconTrailing,
                        color: c.textTertiary,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          AnimatedSize(
            duration: const Duration(milliseconds: 350),
            curve: AppMotion.ease,
            alignment: Alignment.topCenter,
            child: open
                ? Padding(
                    padding: const .only(bottom: 14),
                    child: Text(
                      answer,
                      style: AppTypography.body.copyWith(
                        fontSize: 14,
                        height: 21 / 14,
                        color: c.textSecondary,
                      ),
                    ),
                  )
                : const SizedBox(width: double.infinity),
          ),
        ],
      ),
    );
  }
}
