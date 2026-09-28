import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'core/schemas.dart';

/// Base Onest type scale without color (docs/DESIGN_SYSTEM.md §3).
///
/// Built through [GoogleFonts.onest] so each weight resolves to its own font
/// file instead of a synthesized bold.
abstract final class AppTypography {
  static const _tabular = [FontFeature.tabularFigures()];

  static TextStyle _onest(
    double size,
    double lineHeight,
    FontWeight weight, {
    double letterSpacing = 0,
    List<FontFeature>? features,
  }) => GoogleFonts.onest(
    fontSize: size,
    height: lineHeight / size,
    fontWeight: weight,
    letterSpacing: letterSpacing,
    fontFeatures: features,
  );

  static final displayLarge = _onest(
    40,
    48,
    FontWeight.w700,
    letterSpacing: -1.2,
    features: _tabular,
  );
  static final display = _onest(
    32,
    40,
    FontWeight.w700,
    letterSpacing: -0.64,
    features: _tabular,
  );
  static final headline = _onest(24, 32, FontWeight.w700, letterSpacing: -0.24);
  static final title = _onest(20, 28, FontWeight.w600);
  static final titleSmall = _onest(17, 24, FontWeight.w600);
  static final body = _onest(15, 22, FontWeight.w400);
  static final bodyMedium = _onest(15, 22, FontWeight.w500);
  static final caption = _onest(13, 18, FontWeight.w400);
  static final label = _onest(12, 16, FontWeight.w600, letterSpacing: 0.72);
  static final tabLabel = _onest(11, 14, FontWeight.w500);
  static final button = _onest(16, 22, FontWeight.w600);
  static final amount = _onest(15, 22, FontWeight.w600, features: _tabular);
}

/// Type scale colored for the current theme. Use via `context.textStyles`.
class AppTextStyles {
  final AppColorSchema _c;

  const AppTextStyles(this._c);

  /// 40/48 Bold — hero balance.
  TextStyle get displayLarge =>
      AppTypography.displayLarge.copyWith(color: _c.textPrimary);

  /// 32/40 Bold — amounts.
  TextStyle get display =>
      AppTypography.display.copyWith(color: _c.textPrimary);

  /// 24/32 Bold — tab screen titles.
  TextStyle get headline =>
      AppTypography.headline.copyWith(color: _c.textPrimary);

  /// 20/28 SemiBold — section titles, sheet titles.
  TextStyle get title => AppTypography.title.copyWith(color: _c.textPrimary);

  /// 17/24 SemiBold — push screen titles, card titles.
  TextStyle get titleSmall =>
      AppTypography.titleSmall.copyWith(color: _c.textPrimary);

  TextStyle get body => AppTypography.body.copyWith(color: _c.textPrimary);

  TextStyle get bodySecondary =>
      AppTypography.body.copyWith(color: _c.textSecondary);

  TextStyle get bodyMedium =>
      AppTypography.bodyMedium.copyWith(color: _c.textPrimary);

  TextStyle get caption =>
      AppTypography.caption.copyWith(color: _c.textTertiary);

  /// 12/16 SemiBold, tracked. Pass the text UPPERCASED.
  TextStyle get label => AppTypography.label.copyWith(color: _c.textSecondary);

  TextStyle get tabLabel =>
      AppTypography.tabLabel.copyWith(color: _c.textTertiary);

  TextStyle get button => AppTypography.button.copyWith(color: _c.textPrimary);

  /// 15 SemiBold tabular — list amounts.
  TextStyle get amount => AppTypography.amount.copyWith(color: _c.textPrimary);

  /// Kept for existing pages; same as [title].
  TextStyle get pageTitle => title;
}
