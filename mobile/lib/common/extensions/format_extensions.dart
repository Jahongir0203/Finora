/// Number & text formatting rules (docs/DESIGN_SYSTEM.md §11).
abstract final class AppFormat {
  static const currency = 'UZS';
  static const minus = '−';
  static const hiddenBalance = '•••••••';

  static final _thousands = RegExp(r'\B(?=(\d{3})+(?!\d))');

  /// `24850000` → `24 850 000`. Tiyin is dropped.
  static String spaced(num value) =>
      value.abs().round().toString().replaceAllMapped(_thousands, (_) => ' ');
}

extension MoneyFormatExtension on num {
  /// `24 850 000`; with [sign]: `+12 500 000` / `−186 400`.
  /// Without [sign] negative values still get `−`.
  String toMoney({bool sign = false}) {
    final digits = AppFormat.spaced(this);
    if (this < 0 && round() != 0) return '${AppFormat.minus}$digits';
    if (sign && round() != 0) return '+$digits';
    return digits;
  }

  /// `24 850 000 UZS`.
  String toUzs({bool sign = false}) =>
      '${toMoney(sign: sign)} ${AppFormat.currency}';

  /// Compact form for charts and goal cards: `1.2M`, `5.46M`, `850K`.
  /// Up to 2 decimals, trailing zeros dropped (§11).
  String toShort() {
    final v = abs();
    final prefix = this < 0 ? AppFormat.minus : '';
    String trim(num n) => n
        .toStringAsFixed(2)
        .replaceFirst(RegExp(r'0+$'), '')
        .replaceFirst(RegExp(r'\.$'), '');

    if (v >= 1e9) return '$prefix${trim(v / 1e9)}B';
    if (v >= 1e6) return '$prefix${trim(v / 1e6)}M';
    if (v >= 1e3) return '$prefix${(v / 1e3).round()}K';
    return '$prefix${v.round()}';
  }
}

extension PhoneCardFormatExtension on String {
  String get _digits => replaceAll(RegExp(r'\D'), '');

  /// `998901234567` / `+998901234567` → `+998 90 123 45 67`.
  String toPhone() {
    final d = _digits;
    if (d.length != 12 || !d.startsWith('998')) return this;
    return '+998 ${d.substring(3, 5)} ${d.substring(5, 8)} '
        '${d.substring(8, 10)} ${d.substring(10)}';
  }

  /// `+998 90 *** ** 67`.
  String toMaskedPhone() {
    final d = _digits;
    if (d.length != 12 || !d.startsWith('998')) return this;
    return '+998 ${d.substring(3, 5)} *** ** ${d.substring(10)}';
  }

  /// Card number → `•••• 4821`.
  String toMaskedCard() {
    final d = _digits;
    if (d.length < 4) return this;
    return '•••• ${d.substring(d.length - 4)}';
  }
}
