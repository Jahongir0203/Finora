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
import 'package:finora/application/theme/theme_cubit.dart' as _i931;
import 'package:finora/domain/facades/auth_facade.dart' as _i880;
import 'package:finora/domain/facades/fake_facade.dart' as _i610;
import 'package:finora/domain/facades/finance_facade.dart' as _i606;
import 'package:finora/domain/facades/home_facade.dart' as _i482;
import 'package:finora/domain/facades/notifications_facade.dart' as _i1037;
import 'package:finora/infrastructure/datasources/auth_fake_datasource.dart'
    as _i226;
import 'package:finora/infrastructure/datasources/fake_datasource.dart'
    as _i480;
import 'package:finora/infrastructure/datasources/finance_fake_store.dart'
    as _i440;
import 'package:finora/infrastructure/datasources/home_fake_datasource.dart'
    as _i43;
import 'package:finora/infrastructure/datasources/notifications_fake_datasource.dart'
    as _i861;
import 'package:finora/infrastructure/services/cache/app_cache.dart' as _i459;
import 'package:finora/infrastructure/services/cache/cache_service.dart'
    as _i379;
import 'package:finora/infrastructure/services/cache/dio_cache_store.dart'
    as _i920;
import 'package:finora/infrastructure/services/cache/secure_cache.dart'
    as _i856;
import 'package:finora/infrastructure/services/db/db_crud.dart' as _i236;
import 'package:finora/infrastructure/services/db/db_service.dart' as _i383;
import 'package:finora/infrastructure/services/di_module.dart' as _i26;
import 'package:finora/infrastructure/services/http/http_service.dart' as _i189;
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
    gh.factory<_i195.DeviceInfoCubit>(() => _i195.DeviceInfoCubit());
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
    gh.singleton<_i922.MyLogInterceptor>(() => const _i922.MyLogInterceptor());
    gh.lazySingleton<_i162.BiometricService>(() => _i162.BiometricService());
    gh.singleton<_i867.ConnectionCheckerInterceptor>(
      () => _i867.ConnectionCheckerInterceptor(gh<_i161.InternetConnection>()),
    );
    gh.lazySingleton<_i74.PinService>(
      () => _i74.PinService(gh<_i558.FlutterSecureStorage>()),
    );
    gh.lazySingleton<_i1037.NotificationsFacade>(
      () => _i861.NotificationsFakeDatasource(),
    );
    gh.lazySingleton<_i606.FinanceFacade>(() => _i440.FinanceFakeStore());
    gh.lazySingleton<_i482.HomeFacade>(
      () => _i43.HomeFakeDatasource(gh<_i606.FinanceFacade>()),
    );
    gh.singleton<_i856.SecureCache>(
      () => _i856.SecureCache(
        gh<_i379.CacheService>(),
        gh<_i558.FlutterSecureStorage>(),
      ),
    );
    gh.factory<_i459.AppCache>(() => _i459.AppCache(gh<_i379.CacheService>()));
    gh.factory<_i994.FinanceCubit>(
      () => _i994.FinanceCubit(gh<_i606.FinanceFacade>()),
    );
    gh.singleton<_i695.CacheOptions>(
      () => dIModule.cacheOptions(gh<_i920.DioCacheStore>()),
    );
    gh.lazySingleton<_i967.SessionService>(
      () =>
          _i967.SessionService(gh<_i856.SecureCache>(), gh<_i74.PinService>()),
    );
    gh.factory<_i967.HomeCubit>(
      () => _i967.HomeCubit(
        gh<_i482.HomeFacade>(),
        gh<_i459.AppCache>(),
        gh<_i606.FinanceFacade>(),
      ),
    );
    gh.factory<_i69.NotificationsCubit>(
      () => _i69.NotificationsCubit(gh<_i1037.NotificationsFacade>()),
    );
    gh.lazySingleton<_i417.AutoLockService>(
      () => _i417.AutoLockService(gh<_i459.AppCache>()),
    );
    gh.factory<_i931.ThemeCubit>(() => _i931.ThemeCubit(gh<_i459.AppCache>()));
    gh.singleton<_i317.TokenInterceptor>(
      () => _i317.TokenInterceptor(gh<_i856.SecureCache>()),
    );
    gh.factory<_i880.AuthFacade>(
      () => _i226.AuthFakeDatasource(gh<_i856.SecureCache>()),
    );
    gh.singleton<_i189.HttpService>(
      () => _i189.HttpService(
        gh<_i917.Alice>(),
        gh<_i433.AliceDioAdapter>(),
        gh<_i922.MyLogInterceptor>(),
        gh<_i867.ConnectionCheckerInterceptor>(),
        gh<_i317.TokenInterceptor>(),
        gh<_i695.CacheOptions>(),
      )..init(),
    );
    gh.factory<_i496.SignInCubit>(
      () => _i496.SignInCubit(gh<_i880.AuthFacade>()),
    );
    gh.factory<_i623.VerifyCodeCubit>(
      () => _i623.VerifyCodeCubit(gh<_i880.AuthFacade>()),
    );
    gh.factory<_i275.SplashCubit>(
      () => _i275.SplashCubit(
        gh<_i459.AppCache>(),
        gh<_i880.AuthFacade>(),
        gh<_i74.PinService>(),
      ),
    );
    gh.factory<_i610.FakeFacade>(
      () => _i480.FakeDatasource(gh<_i189.HttpService>()),
    );
    return this;
  }
}

class _$DIModule extends _i26.DIModule {}
