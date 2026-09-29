// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format width=80

// **************************************************************************
// InjectableConfigGenerator
// **************************************************************************

// ignore_for_file: type=lint
// coverage:ignore-file

// ignore_for_file: no_leading_underscores_for_library_prefixes

import 'package:alice/alice.dart' as _i917;
import 'package:alice_dio/alice_dio_adapter.dart' as _i433;
import 'package:dio_cache_interceptor/dio_cache_interceptor.dart' as _i695;
import 'package:finora/application/auth/sign_in/sign_in_cubit.dart' as _i496;
import 'package:finora/application/auth/splash/splash_cubit.dart' as _i275;
import 'package:finora/application/auth/verify_code/verify_code_cubit.dart'
    as _i623;
import 'package:finora/application/device_info/device_info_cubit.dart' as _i195;
import 'package:finora/application/finance/finance_cubit.dart' as _i994;
import 'package:finora/application/home/home_cubit.dart' as _i967;
import 'package:finora/application/network_info/network_info_cubit.dart'
    as _i416;
import 'package:finora/application/notifications/notifications_cubit.dart'
    as _i69;
import 'package:finora/application/stats/stats_cubit.dart' as _i589;
import 'package:finora/application/theme/theme_cubit.dart' as _i931;
import 'package:finora/domain/facades/auth_facade.dart' as _i880;
import 'package:finora/domain/facades/exports_facade.dart' as _i294;
import 'package:finora/domain/facades/finance_facade.dart' as _i606;
import 'package:finora/domain/facades/home_facade.dart' as _i482;
import 'package:finora/domain/facades/insights_facade.dart' as _i850;
import 'package:finora/domain/facades/notifications_facade.dart' as _i1037;
import 'package:finora/domain/facades/profile_facade.dart' as _i901;
import 'package:finora/domain/facades/receipts_facade.dart' as _i126;
import 'package:finora/domain/facades/stats_facade.dart' as _i566;
import 'package:finora/infrastructure/datasources/auth_datasource.dart'
    as _i729;
import 'package:finora/infrastructure/datasources/exports_datasource.dart'
    as _i482;
import 'package:finora/infrastructure/datasources/finance_datasource.dart'
    as _i748;
import 'package:finora/infrastructure/datasources/home_datasource.dart'
    as _i658;
import 'package:finora/infrastructure/datasources/insights_datasource.dart'
    as _i376;
import 'package:finora/infrastructure/datasources/notifications_datasource.dart'
    as _i643;
import 'package:finora/infrastructure/datasources/profile_datasource.dart'
    as _i241;
import 'package:finora/infrastructure/datasources/receipts_datasource.dart'
    as _i48;
import 'package:finora/infrastructure/datasources/stats_datasource.dart'
    as _i630;
import 'package:finora/infrastructure/services/cache/app_cache.dart' as _i459;
import 'package:finora/infrastructure/services/cache/cache_service.dart'
    as _i379;
import 'package:finora/infrastructure/services/cache/dio_cache_store.dart'
    as _i920;
import 'package:finora/infrastructure/services/cache/secure_cache.dart'
    as _i856;
import 'package:finora/infrastructure/services/db/db_crud.dart' as _i236;
import 'package:finora/infrastructure/services/db/db_service.dart' as _i383;
import 'package:finora/infrastructure/services/device/device_info_service.dart'
    as _i522;
import 'package:finora/infrastructure/services/di_module.dart' as _i26;
import 'package:finora/infrastructure/services/http/api_client.dart' as _i369;
import 'package:finora/infrastructure/services/http/http_service.dart' as _i189;
import 'package:finora/infrastructure/services/http/interceptors/api_headers_interceptor.dart'
    as _i962;
import 'package:finora/infrastructure/services/http/interceptors/connection_checker_interceptor.dart'
    as _i867;
import 'package:finora/infrastructure/services/http/interceptors/my_log_interceptor.dart'
    as _i922;
import 'package:finora/infrastructure/services/http/interceptors/token_interceptor.dart'
    as _i317;
import 'package:finora/infrastructure/services/security/auto_lock_service.dart'
    as _i417;
import 'package:finora/infrastructure/services/security/biometric_service.dart'
    as _i162;
import 'package:finora/infrastructure/services/security/device_key_service.dart'
    as _i330;
import 'package:finora/infrastructure/services/security/pin_service.dart'
    as _i74;
import 'package:finora/infrastructure/services/security/session_service.dart'
    as _i967;
import 'package:flutter_secure_storage/flutter_secure_storage.dart' as _i558;
import 'package:get_it/get_it.dart' as _i174;
import 'package:injectable/injectable.dart' as _i526;
import 'package:internet_connection_checker_plus/internet_connection_checker_plus.dart'
    as _i161;

extension GetItInjectableX on _i174.GetIt {
  // initializes the registration of main-scope dependencies inside of GetIt
  Future<_i174.GetIt> init({
    String? environment,
    _i526.EnvironmentFilter? environmentFilter,
  }) async {
    final gh = _i526.GetItHelper(this, environment, environmentFilter);
    final dIModule = _$DIModule();
    gh.factory<_i416.NetworkInfoCubit>(() => _i416.NetworkInfoCubit());
    gh.factory<_i236.DBCrud<dynamic>>(() => _i236.DBCrud<dynamic>());
    await gh.singletonAsync<_i379.CacheService>(() {
      final i = _i379.CacheService();
      return i.init().then((_) => i);
    }, preResolve: true);
    gh.singleton<_i920.DioCacheStore>(() => _i920.DioCacheStore());
    gh.singleton<_i383.DBService>(() => _i383.DBService());
    gh.singleton<_i558.FlutterSecureStorage>(() => dIModule.secureStorage);
    gh.singleton<_i161.InternetConnection>(() => dIModule.connectionChecker);
    gh.singleton<_i433.AliceDioAdapter>(() => dIModule.aliceDioAdapter);
    gh.singleton<_i917.Alice>(() => dIModule.alice);
    gh.singleton<_i962.ApiHeadersInterceptor>(
      () => _i962.ApiHeadersInterceptor(),
    );
    gh.singleton<_i922.MyLogInterceptor>(() => const _i922.MyLogInterceptor());
    gh.lazySingleton<_i522.DeviceInfoService>(() => _i522.DeviceInfoService());
    gh.lazySingleton<_i162.BiometricService>(() => _i162.BiometricService());
    gh.lazySingleton<_i330.DeviceKeyService>(() => _i330.DeviceKeyService());
    gh.singleton<_i867.ConnectionCheckerInterceptor>(
      () => _i867.ConnectionCheckerInterceptor(gh<_i161.InternetConnection>()),
    );
    gh.lazySingleton<_i74.PinService>(
      () => _i74.PinService(gh<_i558.FlutterSecureStorage>()),
    );
    gh.factory<_i195.DeviceInfoCubit>(
      () => _i195.DeviceInfoCubit(gh<_i522.DeviceInfoService>()),
    );
    gh.singleton<_i856.SecureCache>(
      () => _i856.SecureCache(
        gh<_i379.CacheService>(),
        gh<_i558.FlutterSecureStorage>(),
      ),
    );
    gh.factory<_i459.AppCache>(() => _i459.AppCache(gh<_i379.CacheService>()));
    gh.singleton<_i695.CacheOptions>(
      () => dIModule.cacheOptions(gh<_i920.DioCacheStore>()),
    );
    gh.singleton<_i317.TokenInterceptor>(
      () => _i317.TokenInterceptor(
        gh<_i856.SecureCache>(),
        gh<_i330.DeviceKeyService>(),
        gh<_i74.PinService>(),
      ),
    );
    gh.lazySingleton<_i417.AutoLockService>(
      () => _i417.AutoLockService(gh<_i459.AppCache>()),
    );
    gh.factory<_i931.ThemeCubit>(() => _i931.ThemeCubit(gh<_i459.AppCache>()));
    gh.singleton<_i189.HttpService>(
      () => _i189.HttpService(
        gh<_i917.Alice>(),
        gh<_i433.AliceDioAdapter>(),
        gh<_i922.MyLogInterceptor>(),
        gh<_i867.ConnectionCheckerInterceptor>(),
        gh<_i317.TokenInterceptor>(),
        gh<_i962.ApiHeadersInterceptor>(),
        gh<_i695.CacheOptions>(),
      )..init(),
    );
    gh.lazySingleton<_i369.ApiClient>(
      () => _i369.ApiClient(
        gh<_i189.HttpService>(),
        gh<_i330.DeviceKeyService>(),
      ),
    );
    gh.lazySingleton<_i294.ExportsFacade>(
      () => _i482.ExportsDatasource(gh<_i369.ApiClient>()),
    );
    gh.lazySingleton<_i566.StatsFacade>(
      () => _i630.StatsDatasource(gh<_i369.ApiClient>()),
    );
    gh.lazySingleton<_i901.ProfileFacade>(
      () => _i241.ProfileDatasource(gh<_i369.ApiClient>()),
    );
    gh.lazySingleton<_i850.InsightsFacade>(
      () => _i376.InsightsDatasource(gh<_i369.ApiClient>()),
    );
    gh.lazySingleton<_i880.AuthFacade>(
      () => _i729.AuthDatasource(
        gh<_i369.ApiClient>(),
        gh<_i856.SecureCache>(),
        gh<_i330.DeviceKeyService>(),
        gh<_i522.DeviceInfoService>(),
      ),
    );
    gh.lazySingleton<_i1037.NotificationsFacade>(
      () => _i643.NotificationsDatasource(gh<_i369.ApiClient>()),
    );
    gh.lazySingleton<_i606.FinanceFacade>(
      () => _i748.FinanceDatasource(gh<_i369.ApiClient>()),
    );
    gh.factory<_i496.SignInCubit>(
      () => _i496.SignInCubit(gh<_i880.AuthFacade>()),
    );
    gh.factory<_i623.VerifyCodeCubit>(
      () => _i623.VerifyCodeCubit(gh<_i880.AuthFacade>()),
    );
    gh.lazySingleton<_i126.ReceiptsFacade>(
      () => _i48.ReceiptsDatasource(gh<_i369.ApiClient>()),
    );
    gh.factory<_i69.NotificationsCubit>(
      () => _i69.NotificationsCubit(gh<_i1037.NotificationsFacade>()),
    );
    gh.factory<_i275.SplashCubit>(
      () => _i275.SplashCubit(
        gh<_i459.AppCache>(),
        gh<_i880.AuthFacade>(),
        gh<_i74.PinService>(),
      ),
    );
    gh.lazySingleton<_i967.SessionService>(
      () => _i967.SessionService(
        gh<_i856.SecureCache>(),
        gh<_i74.PinService>(),
        gh<_i880.AuthFacade>(),
        gh<_i606.FinanceFacade>(),
      ),
    );
    gh.factory<_i994.FinanceCubit>(
      () => _i994.FinanceCubit(gh<_i606.FinanceFacade>()),
    );
    gh.factory<_i589.StatsCubit>(
      () =>
          _i589.StatsCubit(gh<_i566.StatsFacade>(), gh<_i606.FinanceFacade>()),
    );
    gh.lazySingleton<_i482.HomeFacade>(
      () => _i658.HomeDatasource(
        gh<_i369.ApiClient>(),
        gh<_i606.FinanceFacade>(),
      ),
    );
    gh.factory<_i967.HomeCubit>(
      () => _i967.HomeCubit(
        gh<_i482.HomeFacade>(),
        gh<_i459.AppCache>(),
        gh<_i606.FinanceFacade>(),
      ),
    );
    return this;
  }
}

class _$DIModule extends _i26.DIModule {}
