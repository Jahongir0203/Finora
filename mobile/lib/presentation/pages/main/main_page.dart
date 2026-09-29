import 'package:auto_route/auto_route.dart';
import 'package:finora/application/finance/finance_cubit.dart';
import 'package:finora/application/home/home_cubit.dart';
import 'package:finora/application/notifications/notifications_cubit.dart';
import 'package:finora/di.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'widgets/auto_lock_guard.dart';

/// Signed-in area: tabs + screens pushed over them.
///
/// Holds the cubits shared across those screens (e.g. the Home bell and the
/// Notifications list use the same [NotificationsCubit]).
@RoutePage()
class MainPage extends StatelessWidget implements AutoRouteWrapper {
  const MainPage({super.key});

  @override
  Widget wrappedRoute(BuildContext context) => MultiBlocProvider(
    providers: [
      BlocProvider(create: (_) => di<FinanceCubit>()..load()),
      BlocProvider(create: (_) => di<HomeCubit>()..load()),
      BlocProvider(create: (_) => di<NotificationsCubit>()..load()),
    ],
    child: this,
  );

  @override
  Widget build(BuildContext context) =>
      const AutoLockGuard(child: AutoRouter());
}
