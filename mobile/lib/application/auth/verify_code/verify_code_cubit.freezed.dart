// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'verify_code_cubit.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$VerifyCodeState {

/// E.164 phone the code was sent to.
 String get phone; String get code; int get secondsLeft; VerifyPhase get phase;/// Set after a wrong code; stays visible until the next verification.
 int? get attemptsLeft; int? get lockedMinutes; bool get isResending;/// Incremented to replay the shake animation.
 int get shakeTick;/// Incremented on unexpected errors (network, server).
 int get failureTick; String? get failureMessage;/// Incremented when the code expired (resend is enabled right away).
 int get expiredTick;/// Incremented when a new code was sent.
 int get resentTick; VerifyResult? get result;/// "Forgot PIN" flow: verify with `purpose: pin_reset`.
 bool get pinReset; String? get telegramBotUrl;
/// Create a copy of VerifyCodeState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$VerifyCodeStateCopyWith<VerifyCodeState> get copyWith => _$VerifyCodeStateCopyWithImpl<VerifyCodeState>(this as VerifyCodeState, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is VerifyCodeState&&(identical(other.phone, phone) || other.phone == phone)&&(identical(other.code, code) || other.code == code)&&(identical(other.secondsLeft, secondsLeft) || other.secondsLeft == secondsLeft)&&(identical(other.phase, phase) || other.phase == phase)&&(identical(other.attemptsLeft, attemptsLeft) || other.attemptsLeft == attemptsLeft)&&(identical(other.lockedMinutes, lockedMinutes) || other.lockedMinutes == lockedMinutes)&&(identical(other.isResending, isResending) || other.isResending == isResending)&&(identical(other.shakeTick, shakeTick) || other.shakeTick == shakeTick)&&(identical(other.failureTick, failureTick) || other.failureTick == failureTick)&&(identical(other.failureMessage, failureMessage) || other.failureMessage == failureMessage)&&(identical(other.expiredTick, expiredTick) || other.expiredTick == expiredTick)&&(identical(other.resentTick, resentTick) || other.resentTick == resentTick)&&(identical(other.result, result) || other.result == result)&&(identical(other.pinReset, pinReset) || other.pinReset == pinReset)&&(identical(other.telegramBotUrl, telegramBotUrl) || other.telegramBotUrl == telegramBotUrl));
}


@override
int get hashCode => Object.hash(runtimeType,phone,code,secondsLeft,phase,attemptsLeft,lockedMinutes,isResending,shakeTick,failureTick,failureMessage,expiredTick,resentTick,result,pinReset,telegramBotUrl);

@override
String toString() {
  return 'VerifyCodeState(phone: $phone, code: $code, secondsLeft: $secondsLeft, phase: $phase, attemptsLeft: $attemptsLeft, lockedMinutes: $lockedMinutes, isResending: $isResending, shakeTick: $shakeTick, failureTick: $failureTick, failureMessage: $failureMessage, expiredTick: $expiredTick, resentTick: $resentTick, result: $result, pinReset: $pinReset, telegramBotUrl: $telegramBotUrl)';
}


}

/// @nodoc
abstract mixin class $VerifyCodeStateCopyWith<$Res>  {
  factory $VerifyCodeStateCopyWith(VerifyCodeState value, $Res Function(VerifyCodeState) _then) = _$VerifyCodeStateCopyWithImpl;
@useResult
$Res call({
 String phone, String code, int secondsLeft, VerifyPhase phase, int? attemptsLeft, int? lockedMinutes, bool isResending, int shakeTick, int failureTick, String? failureMessage, int expiredTick, int resentTick, VerifyResult? result, bool pinReset, String? telegramBotUrl
});




}
/// @nodoc
class _$VerifyCodeStateCopyWithImpl<$Res>
    implements $VerifyCodeStateCopyWith<$Res> {
  _$VerifyCodeStateCopyWithImpl(this._self, this._then);

  final VerifyCodeState _self;
  final $Res Function(VerifyCodeState) _then;

/// Create a copy of VerifyCodeState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? phone = null,Object? code = null,Object? secondsLeft = null,Object? phase = null,Object? attemptsLeft = freezed,Object? lockedMinutes = freezed,Object? isResending = null,Object? shakeTick = null,Object? failureTick = null,Object? failureMessage = freezed,Object? expiredTick = null,Object? resentTick = null,Object? result = freezed,Object? pinReset = null,Object? telegramBotUrl = freezed,}) {
  return _then(_self.copyWith(
phone: null == phone ? _self.phone : phone // ignore: cast_nullable_to_non_nullable
as String,code: null == code ? _self.code : code // ignore: cast_nullable_to_non_nullable
as String,secondsLeft: null == secondsLeft ? _self.secondsLeft : secondsLeft // ignore: cast_nullable_to_non_nullable
as int,phase: null == phase ? _self.phase : phase // ignore: cast_nullable_to_non_nullable
as VerifyPhase,attemptsLeft: freezed == attemptsLeft ? _self.attemptsLeft : attemptsLeft // ignore: cast_nullable_to_non_nullable
as int?,lockedMinutes: freezed == lockedMinutes ? _self.lockedMinutes : lockedMinutes // ignore: cast_nullable_to_non_nullable
as int?,isResending: null == isResending ? _self.isResending : isResending // ignore: cast_nullable_to_non_nullable
as bool,shakeTick: null == shakeTick ? _self.shakeTick : shakeTick // ignore: cast_nullable_to_non_nullable
as int,failureTick: null == failureTick ? _self.failureTick : failureTick // ignore: cast_nullable_to_non_nullable
as int,failureMessage: freezed == failureMessage ? _self.failureMessage : failureMessage // ignore: cast_nullable_to_non_nullable
as String?,expiredTick: null == expiredTick ? _self.expiredTick : expiredTick // ignore: cast_nullable_to_non_nullable
as int,resentTick: null == resentTick ? _self.resentTick : resentTick // ignore: cast_nullable_to_non_nullable
as int,result: freezed == result ? _self.result : result // ignore: cast_nullable_to_non_nullable
as VerifyResult?,pinReset: null == pinReset ? _self.pinReset : pinReset // ignore: cast_nullable_to_non_nullable
as bool,telegramBotUrl: freezed == telegramBotUrl ? _self.telegramBotUrl : telegramBotUrl // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [VerifyCodeState].
extension VerifyCodeStatePatterns on VerifyCodeState {
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>({TResult Function( String phone,  String code,  int secondsLeft,  VerifyPhase phase,  int? attemptsLeft,  int? lockedMinutes,  bool isResending,  int shakeTick,  int failureTick,  String? failureMessage,  int expiredTick,  int resentTick,  VerifyResult? result,  bool pinReset,  String? telegramBotUrl)?  initial,required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Initial() when initial != null:
return initial(_that.phone,_that.code,_that.secondsLeft,_that.phase,_that.attemptsLeft,_that.lockedMinutes,_that.isResending,_that.shakeTick,_that.failureTick,_that.failureMessage,_that.expiredTick,_that.resentTick,_that.result,_that.pinReset,_that.telegramBotUrl);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>({required TResult Function( String phone,  String code,  int secondsLeft,  VerifyPhase phase,  int? attemptsLeft,  int? lockedMinutes,  bool isResending,  int shakeTick,  int failureTick,  String? failureMessage,  int expiredTick,  int resentTick,  VerifyResult? result,  bool pinReset,  String? telegramBotUrl)  initial,}) {final _that = this;
switch (_that) {
case _Initial():
return initial(_that.phone,_that.code,_that.secondsLeft,_that.phase,_that.attemptsLeft,_that.lockedMinutes,_that.isResending,_that.shakeTick,_that.failureTick,_that.failureMessage,_that.expiredTick,_that.resentTick,_that.result,_that.pinReset,_that.telegramBotUrl);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>({TResult? Function( String phone,  String code,  int secondsLeft,  VerifyPhase phase,  int? attemptsLeft,  int? lockedMinutes,  bool isResending,  int shakeTick,  int failureTick,  String? failureMessage,  int expiredTick,  int resentTick,  VerifyResult? result,  bool pinReset,  String? telegramBotUrl)?  initial,}) {final _that = this;
switch (_that) {
case _Initial() when initial != null:
return initial(_that.phone,_that.code,_that.secondsLeft,_that.phase,_that.attemptsLeft,_that.lockedMinutes,_that.isResending,_that.shakeTick,_that.failureTick,_that.failureMessage,_that.expiredTick,_that.resentTick,_that.result,_that.pinReset,_that.telegramBotUrl);case _:
  return null;

}
}

}

/// @nodoc


class _Initial extends VerifyCodeState {
  const _Initial({this.phone = '', this.code = '', this.secondsLeft = VerifyCodeCubit.resendSeconds, this.phase = VerifyPhase.input, this.attemptsLeft, this.lockedMinutes, this.isResending = false, this.shakeTick = 0, this.failureTick = 0, this.failureMessage, this.expiredTick = 0, this.resentTick = 0, this.result, this.pinReset = false, this.telegramBotUrl}): super._();
  

/// E.164 phone the code was sent to.
@override@JsonKey() final  String phone;
@override@JsonKey() final  String code;
@override@JsonKey() final  int secondsLeft;
@override@JsonKey() final  VerifyPhase phase;
/// Set after a wrong code; stays visible until the next verification.
@override final  int? attemptsLeft;
@override final  int? lockedMinutes;
@override@JsonKey() final  bool isResending;
/// Incremented to replay the shake animation.
@override@JsonKey() final  int shakeTick;
/// Incremented on unexpected errors (network, server).
@override@JsonKey() final  int failureTick;
@override final  String? failureMessage;
/// Incremented when the code expired (resend is enabled right away).
@override@JsonKey() final  int expiredTick;
/// Incremented when a new code was sent.
@override@JsonKey() final  int resentTick;
@override final  VerifyResult? result;
/// "Forgot PIN" flow: verify with `purpose: pin_reset`.
@override@JsonKey() final  bool pinReset;
@override final  String? telegramBotUrl;

/// Create a copy of VerifyCodeState
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$InitialCopyWith<_Initial> get copyWith => __$InitialCopyWithImpl<_Initial>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _Initial&&(identical(other.phone, phone) || other.phone == phone)&&(identical(other.code, code) || other.code == code)&&(identical(other.secondsLeft, secondsLeft) || other.secondsLeft == secondsLeft)&&(identical(other.phase, phase) || other.phase == phase)&&(identical(other.attemptsLeft, attemptsLeft) || other.attemptsLeft == attemptsLeft)&&(identical(other.lockedMinutes, lockedMinutes) || other.lockedMinutes == lockedMinutes)&&(identical(other.isResending, isResending) || other.isResending == isResending)&&(identical(other.shakeTick, shakeTick) || other.shakeTick == shakeTick)&&(identical(other.failureTick, failureTick) || other.failureTick == failureTick)&&(identical(other.failureMessage, failureMessage) || other.failureMessage == failureMessage)&&(identical(other.expiredTick, expiredTick) || other.expiredTick == expiredTick)&&(identical(other.resentTick, resentTick) || other.resentTick == resentTick)&&(identical(other.result, result) || other.result == result)&&(identical(other.pinReset, pinReset) || other.pinReset == pinReset)&&(identical(other.telegramBotUrl, telegramBotUrl) || other.telegramBotUrl == telegramBotUrl));
}


@override
int get hashCode => Object.hash(runtimeType,phone,code,secondsLeft,phase,attemptsLeft,lockedMinutes,isResending,shakeTick,failureTick,failureMessage,expiredTick,resentTick,result,pinReset,telegramBotUrl);

@override
String toString() {
  return 'VerifyCodeState.initial(phone: $phone, code: $code, secondsLeft: $secondsLeft, phase: $phase, attemptsLeft: $attemptsLeft, lockedMinutes: $lockedMinutes, isResending: $isResending, shakeTick: $shakeTick, failureTick: $failureTick, failureMessage: $failureMessage, expiredTick: $expiredTick, resentTick: $resentTick, result: $result, pinReset: $pinReset, telegramBotUrl: $telegramBotUrl)';
}


}

/// @nodoc
abstract mixin class _$InitialCopyWith<$Res> implements $VerifyCodeStateCopyWith<$Res> {
  factory _$InitialCopyWith(_Initial value, $Res Function(_Initial) _then) = __$InitialCopyWithImpl;
@override @useResult
$Res call({
 String phone, String code, int secondsLeft, VerifyPhase phase, int? attemptsLeft, int? lockedMinutes, bool isResending, int shakeTick, int failureTick, String? failureMessage, int expiredTick, int resentTick, VerifyResult? result, bool pinReset, String? telegramBotUrl
});




}
/// @nodoc
class __$InitialCopyWithImpl<$Res>
    implements _$InitialCopyWith<$Res> {
  __$InitialCopyWithImpl(this._self, this._then);

  final _Initial _self;
  final $Res Function(_Initial) _then;

/// Create a copy of VerifyCodeState
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? phone = null,Object? code = null,Object? secondsLeft = null,Object? phase = null,Object? attemptsLeft = freezed,Object? lockedMinutes = freezed,Object? isResending = null,Object? shakeTick = null,Object? failureTick = null,Object? failureMessage = freezed,Object? expiredTick = null,Object? resentTick = null,Object? result = freezed,Object? pinReset = null,Object? telegramBotUrl = freezed,}) {
  return _then(_Initial(
phone: null == phone ? _self.phone : phone // ignore: cast_nullable_to_non_nullable
as String,code: null == code ? _self.code : code // ignore: cast_nullable_to_non_nullable
as String,secondsLeft: null == secondsLeft ? _self.secondsLeft : secondsLeft // ignore: cast_nullable_to_non_nullable
as int,phase: null == phase ? _self.phase : phase // ignore: cast_nullable_to_non_nullable
as VerifyPhase,attemptsLeft: freezed == attemptsLeft ? _self.attemptsLeft : attemptsLeft // ignore: cast_nullable_to_non_nullable
as int?,lockedMinutes: freezed == lockedMinutes ? _self.lockedMinutes : lockedMinutes // ignore: cast_nullable_to_non_nullable
as int?,isResending: null == isResending ? _self.isResending : isResending // ignore: cast_nullable_to_non_nullable
as bool,shakeTick: null == shakeTick ? _self.shakeTick : shakeTick // ignore: cast_nullable_to_non_nullable
as int,failureTick: null == failureTick ? _self.failureTick : failureTick // ignore: cast_nullable_to_non_nullable
as int,failureMessage: freezed == failureMessage ? _self.failureMessage : failureMessage // ignore: cast_nullable_to_non_nullable
as String?,expiredTick: null == expiredTick ? _self.expiredTick : expiredTick // ignore: cast_nullable_to_non_nullable
as int,resentTick: null == resentTick ? _self.resentTick : resentTick // ignore: cast_nullable_to_non_nullable
as int,result: freezed == result ? _self.result : result // ignore: cast_nullable_to_non_nullable
as VerifyResult?,pinReset: null == pinReset ? _self.pinReset : pinReset // ignore: cast_nullable_to_non_nullable
as bool,telegramBotUrl: freezed == telegramBotUrl ? _self.telegramBotUrl : telegramBotUrl // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
