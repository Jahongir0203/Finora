import 'package:bloc/bloc.dart';
import 'package:finora/application/var_status.dart';
import 'package:finora/domain/facades/auth_facade.dart';
import 'package:finora/domain/models/auth/verify_result.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:injectable/injectable.dart';

part 'sign_in_cubit.freezed.dart';
part 'sign_in_state.dart';

@Injectable()
class SignInCubit extends Cubit<SignInState> {
  static const phoneLength = 9;

  final AuthFacade _auth;

  SignInCubit(this._auth) : super(const .initial());

  void phoneChanged(String digits) {
    if (digits == state.digits) return;
    // Any edit clears the error immediately.
    emit(state.copyWith(digits: digits, showError: false));
  }

  Future<void> submit() async {
    if (state.status.isLoading) return;

    if (!state.isValid) {
      emit(state.copyWith(showError: true, shakeTick: state.shakeTick + 1));
      return;
    }

    emit(state.copyWith(status: .loading()));
    final result = await _auth.requestOtp(state.phone);
    if (isClosed) return;

    result.fold(
      (failure) => emit(state.copyWith(status: .fail(failure))),
      (sent) => emit(state.copyWith(status: .success(), sent: sent)),
    );
  }

  /// Call after navigation so returning to the screen starts clean.
  void resetStatus() => emit(state.copyWith(status: const VarStatus()));
}
