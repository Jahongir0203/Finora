import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_shake.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// `+998` prefix + national number masked as `90 123 45 67`
/// (docs/AUTH_SCREENS.md §4).
class PhoneField extends StatefulWidget {
  final TextEditingController controller;
  final ValueChanged<String> onChanged;
  final VoidCallback? onSubmitted;
  final bool hasError;
  final AppShakeController shake;
  final bool autofocus;

  const PhoneField({
    super.key,
    required this.controller,
    required this.onChanged,
    required this.shake,
    this.onSubmitted,
    this.hasError = false,
    this.autofocus = false,
  });

  /// Digits only, without `+998`.
  static String digitsOf(String text) => text.replaceAll(RegExp(r'\D'), '');

  @override
  State<PhoneField> createState() => _PhoneFieldState();
}

class _PhoneFieldState extends State<PhoneField> {
  final _focus = FocusNode();

  @override
  void initState() {
    super.initState();
    _focus.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    _focus.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final borderColor = widget.hasError
        ? c.danger
        : _focus.hasFocus
        ? c.primary
        : c.border;

    return AppShake(
      controller: widget.shake,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        height: 56,
        clipBehavior: Clip.antiAlias,
        decoration: BoxDecoration(
          color: c.surface,
          borderRadius: .circular(AppRadius.lg),
          border: Border.all(color: borderColor, width: AppSizes.borderThick),
        ),
        child: Row(
          crossAxisAlignment: .stretch,
          children: [
            Container(
              padding: const .symmetric(horizontal: 14),
              alignment: .center,
              decoration: BoxDecoration(
                color: c.background,
                border: BorderDirectional(end: BorderSide(color: c.border)),
              ),
              child: Text(
                '+998',
                style: AppTypography.bodyMedium.copyWith(
                  fontSize: 16,
                  fontWeight: .w600,
                  color: c.textPrimary,
                ),
              ),
            ),
            Expanded(
              child: Center(
                child: TextField(
                  controller: widget.controller,
                  focusNode: _focus,
                  autofocus: widget.autofocus,
                  keyboardType: TextInputType.phone,
                  textInputAction: TextInputAction.done,
                  autofillHints: const [AutofillHints.telephoneNumberNational],
                  inputFormatters: [UzPhoneFormatter()],
                  onChanged: (v) => widget.onChanged(PhoneField.digitsOf(v)),
                  onSubmitted: (_) => widget.onSubmitted?.call(),
                  cursorColor: c.primary,
                  style: AppTypography.bodyMedium.copyWith(
                    fontSize: 17,
                    letterSpacing: 0.34,
                    color: c.textPrimary,
                    fontFeatures: const [FontFeature.tabularFigures()],
                  ),
                  decoration: InputDecoration(
                    hintText: '90 123 45 67',
                    hintStyle: AppTypography.bodyMedium.copyWith(
                      fontSize: 17,
                      letterSpacing: 0.34,
                      color: c.textTertiary,
                    ),
                    filled: false,
                    isDense: true,
                    contentPadding: const .symmetric(horizontal: 14),
                    border: InputBorder.none,
                    enabledBorder: InputBorder.none,
                    focusedBorder: InputBorder.none,
                    errorBorder: InputBorder.none,
                    focusedErrorBorder: InputBorder.none,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Keeps max 9 digits formatted as `XX XXX XX XX`.
/// Pasted `+998 90 123-45-67` / `998901234567` lose the country code.
class UzPhoneFormatter extends TextInputFormatter {
  static const maxDigits = 9;

  @override
  TextEditingValue formatEditUpdate(
    TextEditingValue oldValue,
    TextEditingValue newValue,
  ) {
    var digits = PhoneField.digitsOf(newValue.text);
    if (digits.length > maxDigits && digits.startsWith('998')) {
      digits = digits.substring(3);
    }
    if (digits.length > maxDigits) digits = digits.substring(0, maxDigits);

    final text = format(digits);

    // Keep the cursor after the same number of digits as before formatting.
    final digitsBeforeCursor = PhoneField.digitsOf(
      newValue.text.substring(
        0,
        newValue.selection.end.clamp(0, newValue.text.length),
      ),
    ).length.clamp(0, digits.length);
    var offset = 0;
    for (
      var seen = 0;
      offset < text.length && seen < digitsBeforeCursor;
      offset++
    ) {
      if (text[offset] != ' ') seen++;
    }

    return TextEditingValue(
      text: text,
      selection: .collapsed(offset: offset),
    );
  }

  static String format(String digits) {
    final buffer = StringBuffer();
    for (var i = 0; i < digits.length; i++) {
      if (i == 2 || i == 5 || i == 7) buffer.write(' ');
      buffer.write(digits[i]);
    }
    return buffer.toString();
  }
}
