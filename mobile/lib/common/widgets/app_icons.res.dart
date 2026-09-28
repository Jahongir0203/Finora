// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'app_icons.dart';

// **************************************************
// ResIconsGenerator
// **************************************************

abstract class AppIcons {
  const AppIcons._();

  static final google = SvgPicture.asset('assets/icons/google.svg');

  static const list = <String>['assets/icons/google.svg'];
}

extension ExtensionAppIcons on SvgPicture {
  SvgPicture copyWith({
    double? width,
    double? height,
    BoxFit? fit,
    ColorFilter? colorFilter,
    AlignmentGeometry? alignment,
  }) {
    return SvgPicture.asset(
      path,
      width: width ?? this.width,
      height: height ?? this.height,
      fit: fit ?? this.fit,
      colorFilter: colorFilter ?? this.colorFilter,
      alignment: alignment ?? this.alignment,
    );
  }

  String get path => (this.bytesLoader as SvgAssetLoader).assetName;
}
