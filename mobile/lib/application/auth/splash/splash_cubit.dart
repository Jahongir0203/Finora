import 'package:bloc/bloc.dart';
import 'package:finora/domain/facades/auth_facade.dart';
import 'package:finora/infrastructure/services/cache/app_cache.dart';
import 'package:finora/infrastructure/services/security/pin_service.dart';
import 'package:injectable/injectable.dart';

enum SplashDestination { onboarding, signIn, lock }

/// Decides where the app goes after the splash (docs/AUTH_SCREENS.md §2, §7).
@Injectable()
class SplashCubit extends Cubit<SplashDestination?> {
  final AppCache _cache;
  final AuthFacade _auth;
  final PinService _pins;

  SplashCubit(this._cache, this._auth, this._pins) : super(null);

  Future<SplashDestination> resolve() async {
    final destination = await _decide();
    if (!isClosed) emit(destination);
    return destination;
  }

  Future<SplashDestination> _decide() async {
    try {
      // A session without a PIN (setup was interrupted) signs in again.
      if (await _auth.hasSession() && await _pins.hasPin()) return .lock;
    } catch (_) {
      // Unreadable secure storage → treat as signed out.
    }
    return _cache.onboardingSeen ? .signIn : .onboarding;
  }
}
