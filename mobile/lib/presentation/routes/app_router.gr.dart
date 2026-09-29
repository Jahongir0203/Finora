// dart format width=80
// GENERATED CODE - DO NOT MODIFY BY HAND

// **************************************************************************
// AutoRouterGenerator
// **************************************************************************

// ignore_for_file: type=lint
// coverage:ignore-file

// ignore_for_file: no_leading_underscores_for_library_prefixes

import 'package:auto_route/auto_route.dart' as _i27;
import 'package:finora/presentation/pages/activity/activity_page.dart' as _i2;
import 'package:finora/presentation/pages/auth/auth_page.dart' as _i3;
import 'package:finora/presentation/pages/auth/onboarding/onboarding_page.dart'
    as _i15;
import 'package:finora/presentation/pages/auth/sign_in/sign_in_page.dart'
    as _i21;
import 'package:finora/presentation/pages/auth/verify_code/verify_code_page.dart'
    as _i26;
import 'package:finora/presentation/pages/budgets/budgets_page.dart' as _i4;
import 'package:finora/presentation/pages/goals/goal_details_page.dart' as _i8;
import 'package:finora/presentation/pages/home/home_page.dart' as _i10;
import 'package:finora/presentation/pages/insights/insights_page.dart' as _i11;
import 'package:finora/presentation/pages/main/main_page.dart' as _i13;
import 'package:finora/presentation/pages/main/tabs_page.dart' as _i25;
import 'package:finora/presentation/pages/notifications/notifications_page.dart'
    as _i14;
import 'package:finora/presentation/pages/one_id/one_id_page.dart' as _i16;
import 'package:finora/presentation/pages/pin/create_pin_page.dart' as _i6;
import 'package:finora/presentation/pages/pin/pin_lock_page.dart' as _i17;
import 'package:finora/presentation/pages/pin/starting_balance_page.dart'
    as _i23;
import 'package:finora/presentation/pages/profile/accounts_page.dart' as _i1;
import 'package:finora/presentation/pages/profile/categories_page.dart' as _i5;
import 'package:finora/presentation/pages/profile/currency_page.dart' as _i7;
import 'package:finora/presentation/pages/profile/help_page.dart' as _i9;
import 'package:finora/presentation/pages/profile/language_page.dart' as _i12;
import 'package:finora/presentation/pages/profile/profile_page.dart' as _i18;
import 'package:finora/presentation/pages/reminders/reminders_page.dart'
    as _i19;
import 'package:finora/presentation/pages/scan/scan_page.dart' as _i20;
import 'package:finora/presentation/pages/splash/splash_page.dart' as _i22;
import 'package:finora/presentation/pages/stats/stats_page.dart' as _i24;
import 'package:flutter/cupertino.dart' as _i29;
import 'package:flutter/material.dart' as _i28;

/// generated route for
/// [_i1.AccountsPage]
class AccountsRoute extends _i27.PageRouteInfo<void> {
  const AccountsRoute({List<_i27.PageRouteInfo>? children})
    : super(AccountsRoute.name, initialChildren: children);

  static const String name = 'AccountsRoute';

  static _i27.PageInfo page = _i27.PageInfo(
    name,
    builder: (data) {
      return const _i1.AccountsPage();
    },
  );
}

/// generated route for
/// [_i2.ActivityPage]
class ActivityRoute extends _i27.PageRouteInfo<void> {
  const ActivityRoute({List<_i27.PageRouteInfo>? children})
    : super(ActivityRoute.name, initialChildren: children);

  static const String name = 'ActivityRoute';

  static _i27.PageInfo page = _i27.PageInfo(
    name,
    builder: (data) {
      return const _i2.ActivityPage();
    },
  );
}

/// generated route for
/// [_i3.AuthPage]
class AuthRoute extends _i27.PageRouteInfo<void> {
  const AuthRoute({List<_i27.PageRouteInfo>? children})
    : super(AuthRoute.name, initialChildren: children);

  static const String name = 'AuthRoute';

  static _i27.PageInfo page = _i27.PageInfo(
    name,
    builder: (data) {
      return const _i3.AuthPage();
    },
  );
}

/// generated route for
/// [_i4.BudgetsPage]
class BudgetsRoute extends _i27.PageRouteInfo<void> {
  const BudgetsRoute({List<_i27.PageRouteInfo>? children})
    : super(BudgetsRoute.name, initialChildren: children);

  static const String name = 'BudgetsRoute';

  static _i27.PageInfo page = _i27.PageInfo(
    name,
    builder: (data) {
      return const _i4.BudgetsPage();
    },
  );
}

/// generated route for
/// [_i5.CategoriesPage]
class CategoriesRoute extends _i27.PageRouteInfo<void> {
  const CategoriesRoute({List<_i27.PageRouteInfo>? children})
    : super(CategoriesRoute.name, initialChildren: children);

  static const String name = 'CategoriesRoute';

  static _i27.PageInfo page = _i27.PageInfo(
    name,
    builder: (data) {
      return const _i5.CategoriesPage();
    },
  );
}

/// generated route for
/// [_i6.CreatePinPage]
class CreatePinRoute extends _i27.PageRouteInfo<CreatePinRouteArgs> {
  CreatePinRoute({
    _i28.Key? key,
    bool change = false,
    List<_i27.PageRouteInfo>? children,
  }) : super(
         CreatePinRoute.name,
         args: CreatePinRouteArgs(key: key, change: change),
         initialChildren: children,
       );

  static const String name = 'CreatePinRoute';

  static _i27.PageInfo page = _i27.PageInfo(
    name,
    builder: (data) {
      final args = data.argsAs<CreatePinRouteArgs>(
        orElse: () => const CreatePinRouteArgs(),
      );
      return _i6.CreatePinPage(key: args.key, change: args.change);
    },
  );
}

class CreatePinRouteArgs {
  const CreatePinRouteArgs({this.key, this.change = false});

  final _i28.Key? key;

  final bool change;

  @override
  String toString() {
    return 'CreatePinRouteArgs{key: $key, change: $change}';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    if (other is! CreatePinRouteArgs) return false;
    return key == other.key && change == other.change;
  }

  @override
  int get hashCode => key.hashCode ^ change.hashCode;
}

/// generated route for
/// [_i7.CurrencyPage]
class CurrencyRoute extends _i27.PageRouteInfo<void> {
  const CurrencyRoute({List<_i27.PageRouteInfo>? children})
    : super(CurrencyRoute.name, initialChildren: children);

  static const String name = 'CurrencyRoute';

  static _i27.PageInfo page = _i27.PageInfo(
    name,
    builder: (data) {
      return const _i7.CurrencyPage();
    },
  );
}

/// generated route for
/// [_i8.GoalDetailsPage]
class GoalDetailsRoute extends _i27.PageRouteInfo<GoalDetailsRouteArgs> {
  GoalDetailsRoute({
    _i28.Key? key,
    required String goalId,
    List<_i27.PageRouteInfo>? children,
  }) : super(
         GoalDetailsRoute.name,
         args: GoalDetailsRouteArgs(key: key, goalId: goalId),
         rawPathParams: {'id': goalId},
         initialChildren: children,
       );

  static const String name = 'GoalDetailsRoute';

  static _i27.PageInfo page = _i27.PageInfo(
    name,
    builder: (data) {
      final pathParams = data.inheritedPathParams;
      final args = data.argsAs<GoalDetailsRouteArgs>(
        orElse: () => GoalDetailsRouteArgs(goalId: pathParams.getString('id')),
      );
      return _i8.GoalDetailsPage(key: args.key, goalId: args.goalId);
    },
  );
}

class GoalDetailsRouteArgs {
  const GoalDetailsRouteArgs({this.key, required this.goalId});

  final _i28.Key? key;

  final String goalId;

  @override
  String toString() {
    return 'GoalDetailsRouteArgs{key: $key, goalId: $goalId}';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    if (other is! GoalDetailsRouteArgs) return false;
    return key == other.key && goalId == other.goalId;
  }

  @override
  int get hashCode => key.hashCode ^ goalId.hashCode;
}

/// generated route for
/// [_i9.HelpPage]
class HelpRoute extends _i27.PageRouteInfo<void> {
  const HelpRoute({List<_i27.PageRouteInfo>? children})
    : super(HelpRoute.name, initialChildren: children);

  static const String name = 'HelpRoute';

  static _i27.PageInfo page = _i27.PageInfo(
    name,
    builder: (data) {
      return const _i9.HelpPage();
    },
  );
}

/// generated route for
/// [_i10.HomePage]
class HomeRoute extends _i27.PageRouteInfo<void> {
  const HomeRoute({List<_i27.PageRouteInfo>? children})
    : super(HomeRoute.name, initialChildren: children);

  static const String name = 'HomeRoute';

  static _i27.PageInfo page = _i27.PageInfo(
    name,
    builder: (data) {
      return const _i10.HomePage();
    },
  );
}

/// generated route for
/// [_i11.InsightsPage]
class InsightsRoute extends _i27.PageRouteInfo<void> {
  const InsightsRoute({List<_i27.PageRouteInfo>? children})
    : super(InsightsRoute.name, initialChildren: children);

  static const String name = 'InsightsRoute';

  static _i27.PageInfo page = _i27.PageInfo(
    name,
    builder: (data) {
      return const _i11.InsightsPage();
    },
  );
}

/// generated route for
/// [_i12.LanguagePage]
class LanguageRoute extends _i27.PageRouteInfo<void> {
  const LanguageRoute({List<_i27.PageRouteInfo>? children})
    : super(LanguageRoute.name, initialChildren: children);

  static const String name = 'LanguageRoute';

  static _i27.PageInfo page = _i27.PageInfo(
    name,
    builder: (data) {
      return const _i12.LanguagePage();
    },
  );
}

/// generated route for
/// [_i13.MainPage]
class MainRoute extends _i27.PageRouteInfo<void> {
  const MainRoute({List<_i27.PageRouteInfo>? children})
    : super(MainRoute.name, initialChildren: children);

  static const String name = 'MainRoute';

  static _i27.PageInfo page = _i27.PageInfo(
    name,
    builder: (data) {
      return _i27.WrappedRoute(child: const _i13.MainPage());
    },
  );
}

/// generated route for
/// [_i14.NotificationsPage]
class NotificationsRoute extends _i27.PageRouteInfo<void> {
  const NotificationsRoute({List<_i27.PageRouteInfo>? children})
    : super(NotificationsRoute.name, initialChildren: children);

  static const String name = 'NotificationsRoute';

  static _i27.PageInfo page = _i27.PageInfo(
    name,
    builder: (data) {
      return const _i14.NotificationsPage();
    },
  );
}

/// generated route for
/// [_i15.OnboardingPage]
class OnboardingRoute extends _i27.PageRouteInfo<void> {
  const OnboardingRoute({List<_i27.PageRouteInfo>? children})
    : super(OnboardingRoute.name, initialChildren: children);

  static const String name = 'OnboardingRoute';

  static _i27.PageInfo page = _i27.PageInfo(
    name,
    builder: (data) {
      return const _i15.OnboardingPage();
    },
  );
}

/// generated route for
/// [_i16.OneIdPage]
class OneIdRoute extends _i27.PageRouteInfo<OneIdRouteArgs> {
  OneIdRoute({
    _i28.Key? key,
    required String oneIdUrl,
    List<_i27.PageRouteInfo>? children,
  }) : super(
         OneIdRoute.name,
         args: OneIdRouteArgs(key: key, oneIdUrl: oneIdUrl),
         initialChildren: children,
       );

  static const String name = 'OneIdRoute';

  static _i27.PageInfo page = _i27.PageInfo(
    name,
    builder: (data) {
      final args = data.argsAs<OneIdRouteArgs>();
      return _i16.OneIdPage(key: args.key, oneIdUrl: args.oneIdUrl);
    },
  );
}

class OneIdRouteArgs {
  const OneIdRouteArgs({this.key, required this.oneIdUrl});

  final _i28.Key? key;

  final String oneIdUrl;

  @override
  String toString() {
    return 'OneIdRouteArgs{key: $key, oneIdUrl: $oneIdUrl}';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    if (other is! OneIdRouteArgs) return false;
    return key == other.key && oneIdUrl == other.oneIdUrl;
  }

  @override
  int get hashCode => key.hashCode ^ oneIdUrl.hashCode;
}

/// generated route for
/// [_i17.PinLockPage]
class PinLockRoute extends _i27.PageRouteInfo<PinLockRouteArgs> {
  PinLockRoute({
    _i28.Key? key,
    _i17.LockReason reason = _i17.LockReason.launch,
    List<_i27.PageRouteInfo>? children,
  }) : super(
         PinLockRoute.name,
         args: PinLockRouteArgs(key: key, reason: reason),
         initialChildren: children,
       );

  static const String name = 'PinLockRoute';

  static _i27.PageInfo page = _i27.PageInfo(
    name,
    builder: (data) {
      final args = data.argsAs<PinLockRouteArgs>(
        orElse: () => const PinLockRouteArgs(),
      );
      return _i17.PinLockPage(key: args.key, reason: args.reason);
    },
  );
}

class PinLockRouteArgs {
  const PinLockRouteArgs({this.key, this.reason = _i17.LockReason.launch});

  final _i28.Key? key;

  final _i17.LockReason reason;

  @override
  String toString() {
    return 'PinLockRouteArgs{key: $key, reason: $reason}';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    if (other is! PinLockRouteArgs) return false;
    return key == other.key && reason == other.reason;
  }

  @override
  int get hashCode => key.hashCode ^ reason.hashCode;
}

/// generated route for
/// [_i18.ProfilePage]
class ProfileRoute extends _i27.PageRouteInfo<void> {
  const ProfileRoute({List<_i27.PageRouteInfo>? children})
    : super(ProfileRoute.name, initialChildren: children);

  static const String name = 'ProfileRoute';

  static _i27.PageInfo page = _i27.PageInfo(
    name,
    builder: (data) {
      return const _i18.ProfilePage();
    },
  );
}

/// generated route for
/// [_i19.RemindersPage]
class RemindersRoute extends _i27.PageRouteInfo<RemindersRouteArgs> {
  RemindersRoute({
    _i28.Key? key,
    bool create = false,
    List<_i27.PageRouteInfo>? children,
  }) : super(
         RemindersRoute.name,
         args: RemindersRouteArgs(key: key, create: create),
         initialChildren: children,
       );

  static const String name = 'RemindersRoute';

  static _i27.PageInfo page = _i27.PageInfo(
    name,
    builder: (data) {
      final args = data.argsAs<RemindersRouteArgs>(
        orElse: () => const RemindersRouteArgs(),
      );
      return _i19.RemindersPage(key: args.key, create: args.create);
    },
  );
}

class RemindersRouteArgs {
  const RemindersRouteArgs({this.key, this.create = false});

  final _i28.Key? key;

  final bool create;

  @override
  String toString() {
    return 'RemindersRouteArgs{key: $key, create: $create}';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    if (other is! RemindersRouteArgs) return false;
    return key == other.key && create == other.create;
  }

  @override
  int get hashCode => key.hashCode ^ create.hashCode;
}

/// generated route for
/// [_i20.ScanPage]
class ScanRoute extends _i27.PageRouteInfo<void> {
  const ScanRoute({List<_i27.PageRouteInfo>? children})
    : super(ScanRoute.name, initialChildren: children);

  static const String name = 'ScanRoute';

  static _i27.PageInfo page = _i27.PageInfo(
    name,
    builder: (data) {
      return const _i20.ScanPage();
    },
  );
}

/// generated route for
/// [_i21.SignInPage]
class SignInRoute extends _i27.PageRouteInfo<void> {
  const SignInRoute({List<_i27.PageRouteInfo>? children})
    : super(SignInRoute.name, initialChildren: children);

  static const String name = 'SignInRoute';

  static _i27.PageInfo page = _i27.PageInfo(
    name,
    builder: (data) {
      return _i27.WrappedRoute(child: const _i21.SignInPage());
    },
  );
}

/// generated route for
/// [_i22.SplashPage]
class SplashRoute extends _i27.PageRouteInfo<void> {
  const SplashRoute({List<_i27.PageRouteInfo>? children})
    : super(SplashRoute.name, initialChildren: children);

  static const String name = 'SplashRoute';

  static _i27.PageInfo page = _i27.PageInfo(
    name,
    builder: (data) {
      return const _i22.SplashPage();
    },
  );
}

/// generated route for
/// [_i23.StartingBalancePage]
class StartingBalanceRoute extends _i27.PageRouteInfo<void> {
  const StartingBalanceRoute({List<_i27.PageRouteInfo>? children})
    : super(StartingBalanceRoute.name, initialChildren: children);

  static const String name = 'StartingBalanceRoute';

  static _i27.PageInfo page = _i27.PageInfo(
    name,
    builder: (data) {
      return const _i23.StartingBalancePage();
    },
  );
}

/// generated route for
/// [_i24.StatsPage]
class StatsRoute extends _i27.PageRouteInfo<void> {
  const StatsRoute({List<_i27.PageRouteInfo>? children})
    : super(StatsRoute.name, initialChildren: children);

  static const String name = 'StatsRoute';

  static _i27.PageInfo page = _i27.PageInfo(
    name,
    builder: (data) {
      return const _i24.StatsPage();
    },
  );
}

/// generated route for
/// [_i25.TabsPage]
class TabsRoute extends _i27.PageRouteInfo<void> {
  const TabsRoute({List<_i27.PageRouteInfo>? children})
    : super(TabsRoute.name, initialChildren: children);

  static const String name = 'TabsRoute';

  static _i27.PageInfo page = _i27.PageInfo(
    name,
    builder: (data) {
      return const _i25.TabsPage();
    },
  );
}

/// generated route for
/// [_i26.VerifyCodePage]
class VerifyCodeRoute extends _i27.PageRouteInfo<VerifyCodeRouteArgs> {
  VerifyCodeRoute({
    _i29.Key? key,
    required String phone,
    List<_i27.PageRouteInfo>? children,
  }) : super(
         VerifyCodeRoute.name,
         args: VerifyCodeRouteArgs(key: key, phone: phone),
         initialChildren: children,
       );

  static const String name = 'VerifyCodeRoute';

  static _i27.PageInfo page = _i27.PageInfo(
    name,
    builder: (data) {
      final args = data.argsAs<VerifyCodeRouteArgs>();
      return _i27.WrappedRoute(
        child: _i26.VerifyCodePage(key: args.key, phone: args.phone),
      );
    },
  );
}

class VerifyCodeRouteArgs {
  const VerifyCodeRouteArgs({this.key, required this.phone});

  final _i29.Key? key;

  final String phone;

  @override
  String toString() {
    return 'VerifyCodeRouteArgs{key: $key, phone: $phone}';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    if (other is! VerifyCodeRouteArgs) return false;
    return key == other.key && phone == other.phone;
  }

  @override
  int get hashCode => key.hashCode ^ phone.hashCode;
}
