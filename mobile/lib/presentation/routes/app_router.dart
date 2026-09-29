import 'package:auto_route/auto_route.dart';
import 'app_router.gr.dart';
export 'app_router.gr.dart';

@AutoRouterConfig()
class AppRouter extends RootStackRouter {
  @override
  List<AutoRoute> get routes => [
    AutoRoute(page: SplashRoute.page, initial: true),
    AutoRoute(page: OnboardingRoute.page),
    AutoRoute(page: SignInRoute.page),
    AutoRoute(page: VerifyCodeRoute.page),
    AutoRoute(page: OneIdRoute.page),
    AutoRoute(page: AuthRoute.page),
    AutoRoute(page: CreatePinRoute.page),
    AutoRoute(page: PinLockRoute.page),
    AutoRoute(page: StartingBalanceRoute.page),
    AutoRoute(
      page: MainRoute.page,
      children: [
        AutoRoute(
          page: TabsRoute.page,
          initial: true,
          children: [
            AutoRoute(page: HomeRoute.page, initial: true),
            AutoRoute(page: ActivityRoute.page),
            AutoRoute(page: StatsRoute.page),
            AutoRoute(page: BudgetsRoute.page),
          ],
        ),
        AutoRoute(page: NotificationsRoute.page),
        AutoRoute(page: ScanRoute.page),
        AutoRoute(page: InsightsRoute.page),
        AutoRoute(page: GoalDetailsRoute.page),
        AutoRoute(page: RemindersRoute.page),
        AutoRoute(page: ProfileRoute.page),
        AutoRoute(page: AccountsRoute.page),
        AutoRoute(page: CategoriesRoute.page),
        AutoRoute(page: LanguageRoute.page),
        AutoRoute(page: CurrencyRoute.page),
        AutoRoute(page: HelpRoute.page),
      ],
    ),
  ];
}

final router = AppRouter();
