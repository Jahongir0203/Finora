import 'package:flutter/material.dart';

/// Raw Finora palette (docs/DESIGN_SYSTEM.md §2).
///
/// These colors are identical in light and dark mode. For theme-dependent
/// tokens (text, surfaces, borders...) use `context.appColors`.
abstract final class AppPalette {
  // Primary
  static const primary50 = Color(0xFFECFDF5);
  static const primary100 = Color(0xFFD1FAE5);
  static const primary200 = Color(0xFFA7F3D0);
  static const primary300 = Color(0xFF6EE7B7);
  static const primary400 = Color(0xFF34D399);
  static const primary500 = Color(0xFF10B981);
  static const primary600 = Color(0xFF059669);
  static const primary700 = Color(0xFF047857);
  static const primary800 = Color(0xFF065F46);
  static const primary900 = Color(0xFF064E3B);
  static const primary950 = Color(0xFF052E1F);

  // Blocks inside dark (primary900) cards
  static const heroBlock = Color(0xFF0B5E48);
  static const heroBlockAlt = Color(0x12FFFFFF); // rgba(255,255,255,0.07)
  static const heroTrack = Color(0xFF0B5E48);
  static const heroAvatarBg = Color(0x29A7F3D0); // rgba(167,243,208,0.16)
  static const pinDotBorder = Color(0x80A7F3D0); // rgba(167,243,208,0.5)
  static const pinKeyPressed = Color(0x29FFFFFF); // rgba(255,255,255,0.16)
  static const pinError = Color(0xFFFCA5A5); // error text on primary900
  static const pinChipText = Color(0xFFD1FAE5);
  static const pinChipBg = Color(0x14FFFFFF); // rgba(255,255,255,0.08)

  static const scanner = Color(0xFF0B0F0D);
  static const scannerControl = Color(0xFF1F2925);
  static const scannerViewport = Color(0xFF18201C);
  static const scannerMuted = Color(0xFFA7B3AC);
  static const scannerInk = Color(0xFF0E1A14);
  static const white = Color(0xFFFFFFFF);

  // Categories
  static const catGroceries = Color(0xFF10B981);
  static const catFood = Color(0xFFF59E0B);
  static const catTransport = Color(0xFF3B82F6);
  static const catBills = Color(0xFF8B5CF6);
  static const catHealth = Color(0xFFEF4444);
  static const catShopping = Color(0xFFEC4899);
  static const catHousing = Color(0xFF14B8A6);
  static const catSubs = Color(0xFF6366F1);
  static const catTransfer = Color(0xFF0EA5E9);

  // Bank cards
  static const cardKapitalbank = Color(0xFF064E3B);
  static const cardHamkorbank = Color(0xFF1E293B);
  static const cardTbc = Color(0xFF4C1D95);

  /// Category icon background: the color at 12% opacity.
  static Color tintOf(Color color) => color.withValues(alpha: 0.12);
}
