// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'sign_in_cubit.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$SignInState {

/// National number without `+998`, digits only (max 9).
 String get digits; bool get showError;/// Incremented on each failed submit to replay the shake animation.
 int get shakeTick; VarStatus get status;/// Set on success; the code screen reads its resend timer.
 OtpSent? get sent;
/// Create a copy of SignInState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SignInStateCopyWith<SignInState> get copyWith => _$SignInStateCopyWithImpl<SignInState>(this as SignInState, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SignInState&&(identical(other.digits, digits) || other.digits == digits)&&(identical(other.showError, showError) || other.showError == showError)&&(identical(other.shakeTick, shakeTick) || other.shakeTick == shakeTick)&&(identical(other.status, status) || other.status == status)&&(identical(other.sent, sent) || other.sent == sent));
}


@override
int get hashCode => Object.hash(runtimeType,digits,showError,shakeTick,status,sent);

@override
String toString() {
  return 'SignInState(digits: $digits, showError: $showError, shakeTick: $shakeTick, status: $status, sent: $sent)';
}


}

/// @nodoc
abstract mixin class $SignInStateCopyWith<$Res>  {
  factory $SignInStateCopyWith(SignInState value, $Res Function(SignInState) _then) = _$SignInStateCopyWithImpl;
@useResult
$Res call({
 String digits, bool showError, int shakeTick, VarStatus status, OtpSent? sent
});




}
/// @nodoc
class _$SignInStateCopyWithImpl<$Res>
    implements $SignInStateCopyWith<$Res> {
  _$SignInStateCopyWithImpl(this._self, this._then);

  final SignInState _self;
  final $Res Function(SignInState) _then;

/// Create a copy of SignInState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? digits = null,Object? showError = null,Object? shakeTick = null,Object? status = null,Object? sent = freezed,}) {
  return _then(_self.copyWith(
digits: null == digits ? _self.digits : digits // ignore: cast_nullable_to_non_nullable
as String,showError: null == showError ? _self.showError : showError // ignore: cast_nullable_to_non_nullable
as bool,shakeTick: null == shakeTick ? _self.shakeTick : shakeTick // ignore: cast_nullable_to_non_nullable
as int,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as VarStatus,sent: freezed == sent ? _self.sent : sent // ignore: cast_nullable_to_non_nullable
as OtpSent?,
  ));
}

}


/// Adds pattern-matching-related methods to [SignInState].
extension SignInStatePatterns on SignInState {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>({TResult Function( _Initial value)?  initial,required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Initial() when initial != null:
return initial(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>({required TResult Function( _Initial value)  initial,}){
final _that = this;
switch (_that) {
case _Initial():
return initial(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>({TResult? Function( _Initial value)?  initial,}){
final _that = this;
switch (_that) {
case _Initial() when initial != null:
return initial(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>({TResult Function( String digits,  bool showError,  int shakeTick,  VarStatus status,  OtpSent? sent)?  initial,required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Initial() when initial != null:
return initial(_that.digits,_that.showError,_that.shakeTick,_that.status,_that.sent);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>({required TResult Function( String digits,  bool showError,  int shakeTick,  VarStatus status,  OtpSent? sent)  initial,}) {final _that = this;
switch (_that) {
case _Initial():
return initial(_that.digits,_that.showError,_that.shakeTick,_that.status,_that.sent);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>({TResult? Function( String digits,  bool showError,  int shakeTick,  VarStatus status,  OtpSent? sent)?  initial,}) {final _that = this;
switch (_that) {
case _Initial() when initial != null:
return initial(_that.digits,_that.showError,_that.shakeTick,_that.status,_that.sent);case _:
  return null;

}
}

}

/// @nodoc


class _Initial extends SignInState {
  const _Initial({this.digits = '', this.showError = false, this.shakeTick = 0, this.status = const VarStatus(), this.sent}): super._();
  

/// National number without `+998`, digits only (max 9).
@override@JsonKey() final  String digits;
@override@JsonKey() final  bool showError;
/// Incremented on each failed submit to replay the shake animation.
@override@JsonKey() final  int shakeTick;
@override@JsonKey() final  VarStatus status;
/// Set on success; the code screen reads its resend timer.
@override final  OtpSent? sent;

/// Create a copy of SignInState
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$InitialCopyWith<_Initial> get copyWith => __$InitialCopyWithImpl<_Initial>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _Initial&&(identical(other.digits, digits) || other.digits == digits)&&(identical(other.showError, showError) || other.showError == showError)&&(identical(other.shakeTick, shakeTick) || other.shakeTick == shakeTick)&&(identical(other.status, status) || other.status == status)&&(identical(other.sent, sent) || other.sent == sent));
}


@override
int get hashCode => Object.hash(runtimeType,digits,showError,shakeTick,status,sent);

@override
String toString() {
  return 'SignInState.initial(digits: $digits, showError: $showError, shakeTick: $shakeTick, status: $status, sent: $sent)';
}


}

/// @nodoc
abstract mixin class _$InitialCopyWith<$Res> implements $SignInStateCopyWith<$Res> {
  factory _$InitialCopyWith(_Initial value, $Res Function(_Initial) _then) = __$InitialCopyWithImpl;
@override @useResult
$Res call({
 String digits, bool showError, int shakeTick, VarStatus status, OtpSent? sent
});




}
/// @nodoc
class __$InitialCopyWithImpl<$Res>
    implements _$InitialCopyWith<$Res> {
  __$InitialCopyWithImpl(this._self, this._then);

  final _Initial _self;
  final $Res Function(_Initial) _then;

/// Create a copy of SignInState
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? digits = null,Object? showError = null,Object? shakeTick = null,Object? status = null,Object? sent = freezed,}) {
  return _then(_Initial(
digits: null == digits ? _self.digits : digits // ignore: cast_nullable_to_non_nullable
as String,showError: null == showError ? _self.showError : showError // ignore: cast_nullable_to_non_nullable
as bool,shakeTick: null == shakeTick ? _self.shakeTick : shakeTick // ignore: cast_nullable_to_non_nullable
as int,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as VarStatus,sent: freezed == sent ? _self.sent : sent // ignore: cast_nullable_to_non_nullable
as OtpSent?,
  ));
}


}

// dart format on
