import 'package:auto_route/auto_route.dart';
import 'package:finora/application/notifications/notifications_cubit.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_button.dart';
import 'package:finora/common/widgets/app_fade_in.dart';
import 'package:finora/common/widgets/app_float.dart';
import 'package:finora/common/widgets/app_pressable.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/domain/models/notifications/app_notification.dart';
import 'package:finora/presentation/pages/auth/widgets/auth_back_button.dart';
import 'package:finora/presentation/pages/main/main_actions.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'widgets/notification_tile.dart';

/// Notifications list (docs/screens/HOME_SCREENS.md §4).
@RoutePage()
class NotificationsPage extends StatelessWidget {
  const NotificationsPage({super.key});

  void _open(BuildContext context, AppNotification n) {
    context.read<NotificationsCubit>().markRead(n.id);
    MainActions.forNotification(context, n.type);
  }

  void _showUndo(
    BuildContext context,
    String message,
    List<AppNotification> removed,
  ) {
    if (removed.isEmpty) return;
    final c = context.appColors;
    final cubit = context.read<NotificationsCubit>();

    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: Text(
            message,
            style: AppTypography.bodyMedium.copyWith(
              fontSize: 14,
              color: c.surface,
            ),
          ),
          duration: const Duration(seconds: 4),
          behavior: SnackBarBehavior.floating,
          backgroundColor: c.textPrimary,
          shape: const StadiumBorder(),
          action: SnackBarAction(
            label: Words.undo.str,
            textColor: AppPalette.primary400,
            onPressed: () => cubit.restore(removed),
          ),
        ),
      );
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final cubit = context.read<NotificationsCubit>();

    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: authOverlayStyle(
        context,
      ).copyWith(systemNavigationBarColor: c.background),
      child: Scaffold(
        backgroundColor: c.background,
        body: SafeArea(
          bottom: false,
          child: BlocBuilder<NotificationsCubit, NotificationsState>(
            builder: (context, state) {
              final now = DateTime.now();
              bool isToday(DateTime d) =>
                  d.year == now.year &&
                  d.month == now.month &&
                  d.day == now.day;
              final today = state.items.where((e) => isToday(e.createdAt));
              final earlier = state.items.where((e) => !isToday(e.createdAt));

              var index = 0;
              Widget group(String title, Iterable<AppNotification> items) =>
                  _Group(
                    title: title,
                    children: [
                      for (final (i, n) in items.indexed)
                        AppFadeIn(
                          key: ValueKey(n.id),
                          index: index++,
                          step: const Duration(milliseconds: 60),
                          child: _Dismissible(
                            id: n.id,
                            onDismissed: () {
                              final removed = cubit.delete(n.id);
                              _showUndo(
                                context,
                                Words.notificationDeleted.str,
                                [?removed],
                              );
                            },
                            child: NotificationTile(
                              notification: n,
                              divided: i > 0,
                              onTap: () => _open(context, n),
                            ),
                          ),
                        ),
                    ],
                  );

              return RefreshIndicator(
                onRefresh: cubit.load,
                color: c.primary,
                backgroundColor: c.surface,
                child: ListView(
                  physics: const AlwaysScrollableScrollPhysics(),
                  padding: .fromLTRB(
                    AppSpacing.xl,
                    8,
                    AppSpacing.xl,
                    28 + MediaQuery.paddingOf(context).bottom,
                  ),
                  children: [
                    _TopBar(
                      hasUnread: state.hasUnread,
                      canClear: state.items.isNotEmpty,
                      onMarkAllRead: cubit.markAllRead,
                      onClear: () => _showUndo(
                        context,
                        Words.notificationsCleared.str,
                        cubit.clear(),
                      ),
                    ),
                    if (today.isNotEmpty) ...[
                      const SizedBox(height: AppSpacing.lg),
                      group(Words.today.str, today),
                    ],
                    if (earlier.isNotEmpty) ...[
                      const SizedBox(height: AppSpacing.lg),
                      group(Words.earlier.str, earlier),
                    ],
                    if (state.items.isEmpty && !state.isLoading) ...[
                      const SizedBox(height: AppSpacing.lg),
                      const _EmptyState(),
                    ],
                  ],
                ),
              );
            },
          ),
        ),
      ),
    );
  }
}

class _TopBar extends StatelessWidget {
  final bool hasUnread;
  final bool canClear;
  final VoidCallback onMarkAllRead;
  final VoidCallback onClear;

  const _TopBar({
    required this.hasUnread,
    required this.canClear,
    required this.onMarkAllRead,
    required this.onClear,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Row(
      spacing: AppSpacing.md,
      children: [
        AppIconButton(
          icon: FinoraIcons.back,
          semanticLabel: Words.back.str,
          onPressed: () => context.router.maybePop(),
        ),
        Expanded(
          child: Semantics(
            header: true,
            child: Text(
              Words.notifications.str,
              maxLines: 1,
              overflow: .ellipsis,
              style: context.textStyles.titleSmall,
            ),
          ),
        ),
        AppPressable(
          onTap: hasUnread ? onMarkAllRead : null,
          child: SizedBox(
            height: AppSizes.buttonPill,
            child: Center(
              child: Text(
                Words.markAllRead.str,
                style: AppTypography.button.copyWith(
                  fontSize: 14,
                  height: 20 / 14,
                  color: hasUnread ? c.primaryText : c.textTertiary,
                ),
              ),
            ),
          ),
        ),
        if (canClear)
          AppIconButton(
            icon: FinoraIcons.trash,
            semanticLabel: Words.clearNotifications.str,
            size: 40,
            iconSize: AppSizes.iconTrailing,
            bordered: false,
            background: Colors.transparent,
            foreground: c.textSecondary,
            onPressed: onClear,
          ),
      ],
    );
  }
}

class _Group extends StatelessWidget {
  final String title;
  final List<Widget> children;

  const _Group({required this.title, required this.children});

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Column(
      crossAxisAlignment: .stretch,
      spacing: AppSpacing.sm,
      children: [
        Padding(
          padding: const .symmetric(horizontal: AppSpacing.xs),
          child: Semantics(
            header: true,
            child: Text(
              title,
              style: AppTypography.caption.copyWith(
                fontWeight: .w600,
                color: c.textSecondary,
              ),
            ),
          ),
        ),
        Container(
          clipBehavior: Clip.antiAlias,
          decoration: BoxDecoration(
            color: c.surface,
            borderRadius: .circular(AppRadius.xl),
            border: Border.all(color: c.border),
          ),
          child: Column(children: children),
        ),
      ],
    );
  }
}

/// Swipe left to delete.
class _Dismissible extends StatelessWidget {
  final String id;
  final VoidCallback onDismissed;
  final Widget child;

  const _Dismissible({
    required this.id,
    required this.onDismissed,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Dismissible(
      key: ValueKey('dismiss-$id'),
      direction: DismissDirection.endToStart,
      onDismissed: (_) => onDismissed(),
      background: Container(
        color: c.dangerSoft,
        alignment: AlignmentDirectional.centerEnd,
        padding: const .symmetric(horizontal: AppSpacing.xl),
        child: Icon(FinoraIcons.trash, size: AppSizes.iconMd, color: c.danger),
      ),
      // Card padding lives here so the red background spans the full width.
      child: Padding(
        padding: const .symmetric(horizontal: AppSpacing.lg),
        child: child,
      ),
    );
  }
}

/// "You're all caught up" (§4).
class _EmptyState extends StatelessWidget {
  const _EmptyState();

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Padding(
      padding: const .symmetric(horizontal: 12, vertical: 56),
      child: Column(
        spacing: AppSpacing.lg,
        children: [
          _Pop(
            child: Container(
              width: 120,
              height: 120,
              alignment: .center,
              decoration: BoxDecoration(color: c.tint, shape: BoxShape.circle),
              child: AppFloat(
                period: const Duration(milliseconds: 3500),
                child: Container(
                  width: 68,
                  height: 68,
                  alignment: .center,
                  decoration: BoxDecoration(
                    color: c.primary,
                    borderRadius: .circular(22),
                  ),
                  child: Icon(FinoraIcons.empty, size: 30, color: c.onPrimary),
                ),
              ),
            ),
          ),
          Text(
            Words.allCaughtUp.str,
            textAlign: .center,
            style: context.textStyles.title.copyWith(fontWeight: .w700),
          ),
          ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 280),
            child: Text(
              Words.allCaughtUpDesc.str,
              textAlign: .center,
              style: context.textStyles.bodySecondary,
            ),
          ),
        ],
      ),
    );
  }
}

/// `fnPop`: scale .6 → 1.06 → 1, 600ms.
class _Pop extends StatelessWidget {
  final Widget child;

  const _Pop({required this.child});

  @override
  Widget build(BuildContext context) {
    if (MediaQuery.disableAnimationsOf(context)) return child;

    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0, end: 1),
      duration: const Duration(milliseconds: 600),
      builder: (_, t, child) {
        final scale = t < 0.7
            ? 0.6 + 0.46 * Curves.easeOut.transform(t / 0.7)
            : 1.06 -
                  0.06 *
                      Curves.easeInOut.transform(
                        ((t - 0.7) / 0.3).clamp(0.0, 1.0),
                      );
        return Opacity(
          opacity: (t * 2).clamp(0.0, 1.0),
          child: Transform.scale(scale: scale, child: child),
        );
      },
      child: child,
    );
  }
}
