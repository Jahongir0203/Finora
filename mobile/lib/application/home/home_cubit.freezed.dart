// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'home_cubit.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$HomeState {

 HomeData? get data; bool get isLoading; bool get isSavingBalance; bool get balanceHidden;/// Incremented when loading fails.
 int get failureTick;
/// Create a copy of HomeState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$HomeStateCopyWith<HomeState> get copyWith => _$HomeStateCopyWithImpl<HomeState>(this as HomeState, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is HomeState&&(identical(other.data, data) || other.data == data)&&(identical(other.isLoading, isLoading) || other.isLoading == isLoading)&&(identical(other.isSavingBalance, isSavingBalance) || other.isSavingBalance == isSavingBalance)&&(identical(other.balanceHidden, balanceHidden) || other.balanceHidden == balanceHidden)&&(identical(other.failureTick, failureTick) || other.failureTick == failureTick));
}


@override
int get hashCode => Object.hash(runtimeType,data,isLoading,isSavingBalance,balanceHidden,failureTick);

@override
String toString() {
  return 'HomeState(data: $data, isLoading: $isLoading, isSavingBalance: $isSavingBalance, balanceHidden: $balanceHidden, failureTick: $failureTick)';
}


}

/// @nodoc
abstract mixin class $HomeStateCopyWith<$Res>  {
  factory $HomeStateCopyWith(HomeState value, $Res Function(HomeState) _then) = _$HomeStateCopyWithImpl;
@useResult
$Res call({
 HomeData? data, bool isLoading, bool isSavingBalance, bool balanceHidden, int failureTick
});




}
/// @nodoc
class _$HomeStateCopyWithImpl<$Res>
    implements $HomeStateCopyWith<$Res> {
  _$HomeStateCopyWithImpl(this._self, this._then);

  final HomeState _self;
  final $Res Function(HomeState) _then;

/// Create a copy of HomeState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? data = freezed,Object? isLoading = null,Object? isSavingBalance = null,Object? balanceHidden = null,Object? failureTick = null,}) {
  return _then(_self.copyWith(
data: freezed == data ? _self.data : data // ignore: cast_nullable_to_non_nullable
as HomeData?,isLoading: null == isLoading ? _self.isLoading : isLoading // ignore: cast_nullable_to_non_nullable
as bool,isSavingBalance: null == isSavingBalance ? _self.isSavingBalance : isSavingBalance // ignore: cast_nullable_to_non_nullable
as bool,balanceHidden: null == balanceHidden ? _self.balanceHidden : balanceHidden // ignore: cast_nullable_to_non_nullable
as bool,failureTick: null == failureTick ? _self.failureTick : failureTick // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [HomeState].
extension HomeStatePatterns on HomeState {
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>({TResult Function( HomeData? data,  bool isLoading,  bool isSavingBalance,  bool balanceHidden,  int failureTick)?  initial,required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Initial() when initial != null:
return initial(_that.data,_that.isLoading,_that.isSavingBalance,_that.balanceHidden,_that.failureTick);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>({required TResult Function( HomeData? data,  bool isLoading,  bool isSavingBalance,  bool balanceHidden,  int failureTick)  initial,}) {final _that = this;
switch (_that) {
case _Initial():
return initial(_that.data,_that.isLoading,_that.isSavingBalance,_that.balanceHidden,_that.failureTick);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>({TResult? Function( HomeData? data,  bool isLoading,  bool isSavingBalance,  bool balanceHidden,  int failureTick)?  initial,}) {final _that = this;
switch (_that) {
case _Initial() when initial != null:
return initial(_that.data,_that.isLoading,_that.isSavingBalance,_that.balanceHidden,_that.failureTick);case _:
  return null;

}
}

}

/// @nodoc


class _Initial implements HomeState {
  const _Initial({this.data, this.isLoading = false, this.isSavingBalance = false, this.balanceHidden = false, this.failureTick = 0});
  

@override final  HomeData? data;
@override@JsonKey() final  bool isLoading;
@override@JsonKey() final  bool isSavingBalance;
@override@JsonKey() final  bool balanceHidden;
/// Incremented when loading fails.
@override@JsonKey() final  int failureTick;

/// Create a copy of HomeState
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$InitialCopyWith<_Initial> get copyWith => __$InitialCopyWithImpl<_Initial>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _Initial&&(identical(other.data, data) || other.data == data)&&(identical(other.isLoading, isLoading) || other.isLoading == isLoading)&&(identical(other.isSavingBalance, isSavingBalance) || other.isSavingBalance == isSavingBalance)&&(identical(other.balanceHidden, balanceHidden) || other.balanceHidden == balanceHidden)&&(identical(other.failureTick, failureTick) || other.failureTick == failureTick));
}


@override
int get hashCode => Object.hash(runtimeType,data,isLoading,isSavingBalance,balanceHidden,failureTick);

@override
String toString() {
  return 'HomeState.initial(data: $data, isLoading: $isLoading, isSavingBalance: $isSavingBalance, balanceHidden: $balanceHidden, failureTick: $failureTick)';
}


}

/// @nodoc
abstract mixin class _$InitialCopyWith<$Res> implements $HomeStateCopyWith<$Res> {
  factory _$InitialCopyWith(_Initial value, $Res Function(_Initial) _then) = __$InitialCopyWithImpl;
@override @useResult
$Res call({
 HomeData? data, bool isLoading, bool isSavingBalance, bool balanceHidden, int failureTick
});




}
/// @nodoc
class __$InitialCopyWithImpl<$Res>
    implements _$InitialCopyWith<$Res> {
  __$InitialCopyWithImpl(this._self, this._then);

  final _Initial _self;
  final $Res Function(_Initial) _then;

/// Create a copy of HomeState
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? data = freezed,Object? isLoading = null,Object? isSavingBalance = null,Object? balanceHidden = null,Object? failureTick = null,}) {
  return _then(_Initial(
data: freezed == data ? _self.data : data // ignore: cast_nullable_to_non_nullable
as HomeData?,isLoading: null == isLoading ? _self.isLoading : isLoading // ignore: cast_nullable_to_non_nullable
as bool,isSavingBalance: null == isSavingBalance ? _self.isSavingBalance : isSavingBalance // ignore: cast_nullable_to_non_nullable
as bool,balanceHidden: null == balanceHidden ? _self.balanceHidden : balanceHidden // ignore: cast_nullable_to_non_nullable
as bool,failureTick: null == failureTick ? _self.failureTick : failureTick // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}

// dart format on
