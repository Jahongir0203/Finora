import 'package:finora/common/extensions/format_extensions.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Labeled text input (docs/DESIGN_SYSTEM.md §6.2).
///
/// Label above (13 SemiBold), 50px field, error text below.
class AppTextField extends StatelessWidget {
  final String? label;
  final String? hint;
  final String? errorText;
  final TextEditingController? controller;
  final FocusNode? focusNode;
  final ValueChanged<String>? onChanged;
  final ValueChanged<String>? onSubmitted;
  final TextInputType? keyboardType;
  final TextInputAction? textInputAction;
  final List<TextInputFormatter>? inputFormatters;
  final bool obscureText;
  final bool enabled;
  final bool autofocus;
  final int maxLines;
  final Widget? prefix;
  final Widget? suffix;

  const AppTextField({
    super.key,
    this.label,
    this.hint,
    this.errorText,
    this.controller,
    this.focusNode,
    this.onChanged,
    this.onSubmitted,
    this.keyboardType,
    this.textInputAction,
    this.inputFormatters,
    this.obscureText = false,
    this.enabled = true,
    this.autofocus = false,
    this.maxLines = 1,
    this.prefix,
    this.suffix,
  });

  /// Search field: `search` icon on the left.
  factory AppTextField.search({
    Key? key,
    String hint = 'Search',
    TextEditingController? controller,
    ValueChanged<String>? onChanged,
  }) => AppTextField(
    key: key,
    hint: hint,
    controller: controller,
    onChanged: onChanged,
    textInputAction: TextInputAction.search,
    prefix: const Icon(FinoraIcons.search, size: AppSizes.iconTrailing),
  );

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final styles = context.textStyles;

    return Column(
      crossAxisAlignment: .start,
      mainAxisSize: .min,
      spacing: 6,
      children: [
        if (label != null)
          Text(
            label!,
            style: styles.caption.copyWith(
              fontWeight: .w600,
              color: c.textSecondary,
            ),
          ),
        TextField(
          controller: controller,
          focusNode: focusNode,
          onChanged: onChanged,
          onSubmitted: onSubmitted,
          keyboardType: keyboardType,
          textInputAction: textInputAction,
          inputFormatters: inputFormatters,
          obscureText: obscureText,
          enabled: enabled,
          autofocus: autofocus,
          maxLines: maxLines,
          style: styles.body,
          decoration: InputDecoration(
            hintText: hint,
            errorText: errorText,
            constraints: maxLines == 1
                ? const BoxConstraints(minHeight: AppSizes.input)
                : null,
            prefixIcon: prefix == null
                ? null
                : Padding(
                    padding: const .only(left: 14, right: 8),
                    child: prefix,
                  ),
            prefixIconConstraints: const BoxConstraints(minWidth: 40),
            suffixIcon: suffix,
          ),
        ),
      ],
    );
  }
}

/// Large amount input: 34 Bold digits, `UZS` on the right (§6.2).
///
/// Formats as the user types: `1250000` → `1 250 000`.
/// Read the value with [AppAmountField.parse].
class AppAmountField extends StatelessWidget {
  final TextEditingController controller;
  final String? label;
  final String? errorText;
  final FocusNode? focusNode;
  final ValueChanged<int>? onChanged;
  final bool autofocus;

  const AppAmountField({
    super.key,
    required this.controller,
    this.label,
    this.errorText,
    this.focusNode,
    this.onChanged,
    this.autofocus = false,
  });

  static int parse(String text) =>
      int.tryParse(text.replaceAll(RegExp(r'\D'), '')) ?? 0;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final styles = context.textStyles;

    return Column(
      crossAxisAlignment: .start,
      mainAxisSize: .min,
      spacing: 6,
      children: [
        if (label != null)
          Text(
            label!,
            style: styles.caption.copyWith(
              fontWeight: .w600,
              color: c.textSecondary,
            ),
          ),
        TextField(
          controller: controller,
          focusNode: focusNode,
          autofocus: autofocus,
          keyboardType: TextInputType.number,
          inputFormatters: const [SpacedDigitsFormatter()],
          onChanged: (v) => onChanged?.call(parse(v)),
          style: AppTypography.display.copyWith(
            fontSize: 34,
            height: 1.2,
            color: c.textPrimary,
          ),
          decoration: InputDecoration(
            hintText: '0',
            errorText: errorText,
            constraints: const BoxConstraints(minHeight: AppSizes.inputAmount),
            contentPadding: const .symmetric(horizontal: 18, vertical: 12),
            hintStyle: AppTypography.display.copyWith(
              fontSize: 34,
              color: c.textDisabled,
            ),
            suffixIcon: Padding(
              padding: const .only(right: 18),
              child: Text(
                AppFormat.currency,
                style: styles.titleSmall.copyWith(
                  fontWeight: .w500,
                  color: c.textTertiary,
                ),
              ),
            ),
            suffixIconConstraints: const BoxConstraints(),
            border: _border(c.border, 1),
            enabledBorder: _border(c.border, 1),
            focusedBorder: _border(c.primary, AppSizes.borderThick),
            errorBorder: _border(c.danger, AppSizes.borderThick),
            focusedErrorBorder: _border(c.danger, AppSizes.borderThick),
          ),
        ),
      ],
    );
  }

  static OutlineInputBorder _border(Color color, double width) =>
      OutlineInputBorder(
        borderRadius: .circular(18),
        borderSide: BorderSide(color: color, width: width),
      );
}

/// Borderless, unfilled decoration for text fields drawn inside custom
/// boxes (the theme's outline borders would otherwise still apply).
InputDecoration bareInputDecoration({String? hint, TextStyle? hintStyle}) =>
    InputDecoration.collapsed(hintText: hint, hintStyle: hintStyle).copyWith(
      filled: false,
      enabledBorder: InputBorder.none,
      focusedBorder: InputBorder.none,
      disabledBorder: InputBorder.none,
    );

/// Digits only, grouped with spaces: `12500000` → `12 500 000`.
class SpacedDigitsFormatter extends TextInputFormatter {
  final int maxDigits;

  const SpacedDigitsFormatter({this.maxDigits = 15});

  static int parse(String text) =>
      int.tryParse(text.replaceAll(RegExp(r'\D'), '')) ?? 0;

  @override
  TextEditingValue formatEditUpdate(
    TextEditingValue oldValue,
    TextEditingValue newValue,
  ) {
    var digits = newValue.text.replaceAll(RegExp(r'\D'), '');
    digits = digits.replaceFirst(RegExp(r'^0+(?=\d)'), '');
    if (digits.length > maxDigits) return oldValue;
    if (digits.isEmpty) return const TextEditingValue();

    final text = AppFormat.spaced(int.parse(digits));
    return TextEditingValue(
      text: text,
      selection: .collapsed(offset: text.length),
    );
  }
}

/// Sets [controller] to [value] formatted with spaces, cursor at the end.
void setSpacedAmount(TextEditingController controller, num value) {
  final text = value <= 0 ? '' : AppFormat.spaced(value);
  controller.value = TextEditingValue(
    text: text,
    selection: .collapsed(offset: text.length),
  );
}

/// 13/600 label + 50px field, radius 14 (sheet forms).
class AppFormField extends StatelessWidget {
  final String label;
  final String hint;
  final TextEditingController controller;
  final String? errorText;
  final int? maxLength;
  final ValueChanged<String>? onChanged;
  final bool autofocus;

  const AppFormField({
    super.key,
    required this.label,
    required this.hint,
    required this.controller,
    this.errorText,
    this.maxLength,
    this.onChanged,
    this.autofocus = false,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return _Labeled(
      label: label,
      errorText: errorText,
      child: TextField(
        controller: controller,
        autofocus: autofocus,
        onChanged: onChanged,
        textCapitalization: TextCapitalization.sentences,
        inputFormatters: [
          if (maxLength != null) LengthLimitingTextInputFormatter(maxLength),
        ],
        style: context.textStyles.body,
        decoration: InputDecoration(
          hintText: hint,
          constraints: const BoxConstraints(minHeight: AppSizes.input),
          contentPadding: const .symmetric(horizontal: 16, vertical: 14),
          enabledBorder: errorText != null
              ? _border(c.danger, AppSizes.borderThick)
              : null,
          focusedBorder: errorText != null
              ? _border(c.danger, AppSizes.borderThick)
              : null,
        ),
      ),
    );
  }
}

/// 13/600 label + 50px amount field: 17/600 tabular digits, `UZS` suffix.
class AppInlineAmountField extends StatelessWidget {
  final String label;
  final TextEditingController controller;
  final String? errorText;
  final String hint;
  final int maxDigits;
  final ValueChanged<int>? onChanged;

  const AppInlineAmountField({
    super.key,
    required this.label,
    required this.controller,
    this.errorText,
    this.hint = '0',
    this.maxDigits = 11,
    this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final digits = AppTypography.titleSmall.copyWith(
      color: c.textPrimary,
      fontFeatures: const [FontFeature.tabularFigures()],
    );

    return _Labeled(
      label: label,
      errorText: errorText,
      child: TextField(
        controller: controller,
        keyboardType: TextInputType.number,
        inputFormatters: [SpacedDigitsFormatter(maxDigits: maxDigits)],
        onChanged: (v) => onChanged?.call(SpacedDigitsFormatter.parse(v)),
        style: digits,
        decoration: InputDecoration(
          hintText: hint,
          hintStyle: digits.copyWith(color: c.textTertiary),
          constraints: const BoxConstraints(minHeight: AppSizes.input),
          contentPadding: const .symmetric(horizontal: 16, vertical: 13),
          suffixIcon: Padding(
            padding: const .only(right: 16),
            child: Text(
              AppFormat.currency,
              style: AppTypography.bodyMedium.copyWith(
                fontSize: 14,
                color: c.textTertiary,
              ),
            ),
          ),
          suffixIconConstraints: const BoxConstraints(),
          enabledBorder: errorText != null
              ? _border(c.danger, AppSizes.borderThick)
              : null,
          focusedBorder: errorText != null
              ? _border(c.danger, AppSizes.borderThick)
              : null,
        ),
      ),
    );
  }
}

/// Big boxed amount (Starting balance, Current balance sheet):
/// [fontSize] Bold digits, `UZS` 17 SemiBold on the right. The border turns
/// `primary500` once focused or filled.
class AppBoxedAmountField extends StatefulWidget {
  final TextEditingController controller;
  final double height;
  final double fontSize;
  final int maxDigits;
  final bool autofocus;
  final bool enabled;
  final ValueChanged<String>? onSubmitted;

  const AppBoxedAmountField({
    super.key,
    required this.controller,
    this.height = 72,
    this.fontSize = 32,
    this.maxDigits = 12,
    this.autofocus = false,
    this.enabled = true,
    this.onSubmitted,
  });

  @override
  State<AppBoxedAmountField> createState() => _AppBoxedAmountFieldState();
}

class _AppBoxedAmountFieldState extends State<AppBoxedAmountField> {
  final _focus = FocusNode();

  @override
  void initState() {
    super.initState();
    _focus.addListener(_refresh);
    widget.controller.addListener(_refresh);
  }

  void _refresh() => setState(() {});

  @override
  void dispose() {
    widget.controller.removeListener(_refresh);
    _focus.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final active =
        _focus.hasFocus ||
        SpacedDigitsFormatter.parse(widget.controller.text) > 0;
    final style = AppTypography.display.copyWith(
      fontSize: widget.fontSize,
      height: 1.2,
      letterSpacing: -widget.fontSize * 0.02,
      color: c.textPrimary,
    );

    return AnimatedContainer(
      duration: const Duration(milliseconds: 200),
      height: widget.height,
      padding: const .symmetric(horizontal: 18),
      decoration: BoxDecoration(
        color: c.surface,
        borderRadius: .circular(18),
        border: Border.all(
          color: active ? c.primary : c.border,
          width: AppSizes.borderThick,
        ),
      ),
      child: Row(
        spacing: AppSpacing.md,
        children: [
          Expanded(
            child: TextField(
              controller: widget.controller,
              focusNode: _focus,
              autofocus: widget.autofocus,
              enabled: widget.enabled,
              keyboardType: TextInputType.number,
              textInputAction: TextInputAction.done,
              inputFormatters: [
                SpacedDigitsFormatter(maxDigits: widget.maxDigits),
              ],
              onSubmitted: widget.onSubmitted,
              cursorColor: c.primary,
              style: style,
              decoration: bareInputDecoration(hint: '0',
                hintStyle: style.copyWith(color: c.textTertiary),
              ),
            ),
          ),
          Text(
            AppFormat.currency,
            style: AppTypography.titleSmall.copyWith(color: c.textTertiary),
          ),
        ],
      ),
    );
  }
}

/// +100K · +1M · +5M style chips that add to an amount.
class AmountQuickChips extends StatelessWidget {
  final List<(int, String)> presets;
  final ValueChanged<int> onAdd;
  final double height;

  const AmountQuickChips({
    super.key,
    required this.onAdd,
    this.presets = const [
      (100000, '+100K'),
      (1000000, '+1M'),
      (5000000, '+5M'),
    ],
    this.height = 38,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Row(
      spacing: AppSpacing.sm,
      children: [
        for (final (value, label) in presets)
          Expanded(
            child: GestureDetector(
              behavior: HitTestBehavior.opaque,
              onTap: () {
                HapticFeedback.selectionClick();
                onAdd(value);
              },
              child: Container(
                height: height,
                alignment: .center,
                decoration: BoxDecoration(
                  color: c.background,
                  borderRadius: .circular(12),
                ),
                child: Text(
                  label,
                  style: AppTypography.button.copyWith(
                    fontSize: 14,
                    color: c.textPrimary,
                  ),
                ),
              ),
            ),
          ),
      ],
    );
  }
}

class _Labeled extends StatelessWidget {
  final String label;
  final String? errorText;
  final Widget child;

  const _Labeled({required this.label, required this.child, this.errorText});

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Column(
      crossAxisAlignment: .stretch,
      mainAxisSize: .min,
      spacing: 6,
      children: [
        Text(
          label,
          style: AppTypography.caption.copyWith(
            fontWeight: .w600,
            color: c.textSecondary,
          ),
        ),
        child,
        // An empty [errorText] only turns the border red.
        if (errorText?.isNotEmpty ?? false)
          Text(
            errorText!,
            style: AppTypography.caption.copyWith(
              fontWeight: .w500,
              color: c.danger,
            ),
          ),
      ],
    );
  }
}

OutlineInputBorder _border(Color color, double width) => OutlineInputBorder(
  borderRadius: .circular(AppRadius.md),
  borderSide: BorderSide(color: color, width: width),
);
