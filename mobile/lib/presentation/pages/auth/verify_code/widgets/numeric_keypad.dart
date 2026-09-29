import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/words/words.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// In-app numeric keypad: `1 2 3 / 4 5 6 / 7 8 9 / _ 0 ⌫`.
/// The system keyboard never opens (docs/AUTH_SCREENS.md §5).
class NumericKeypad extends StatelessWidget {
  final ValueChanged<String> onDigit;
  final VoidCallback onDelete;
  final VoidCallback onClear;
  final bool enabled;

  const NumericKeypad({
    super.key,
    required this.onDigit,
    required this.onDelete,
    required this.onClear,
    this.enabled = true,
  });

  @override
  Widget build(BuildContext context) {
    const rows = [
      ['1', '2', '3'],
      ['4', '5', '6'],
      ['7', '8', '9'],
      ['', '0', '<'],
    ];

    return AnimatedOpacity(
      duration: AppMotion.fast,
      opacity: enabled ? 1 : 0.4,
      child: IgnorePointer(
        ignoring: !enabled,
        child: Column(
          spacing: 6,
          children: [
            for (final row in rows)
              Row(
                spacing: 6,
                children: [
                  for (final key in row)
                    Expanded(
                      child: switch (key) {
                        '' => const SizedBox(height: 56),
                        '<' => _Key(
                          semanticLabel: Words.delete.str,
                          onTap: onDelete,
                          onLongPress: onClear,
                          child: Icon(
                            FinoraIcons.delete,
                            size: 22,
                            color: context.appColors.textPrimary,
                          ),
                        ),
                        _ => _Key(
                          semanticLabel: key,
                          onTap: () => onDigit(key),
                          child: Text(
                            key,
                            style: AppTypography.title.copyWith(
                              fontSize: 24,
                              fontWeight: .w500,
                              color: context.appColors.textPrimary,
                            ),
                          ),
                        ),
                      },
                    ),
                ],
              ),
          ],
        ),
      ),
    );
  }
}

class _Key extends StatefulWidget {
  final Widget child;
  final String semanticLabel;
  final VoidCallback onTap;
  final VoidCallback? onLongPress;

  const _Key({
    required this.child,
    required this.semanticLabel,
    required this.onTap,
    this.onLongPress,
  });

  @override
  State<_Key> createState() => _KeyState();
}

class _KeyState extends State<_Key> {
  var _pressed = false;

  void _set(bool v) {
    if (_pressed != v) setState(() => _pressed = v);
  }

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      label: widget.semanticLabel,
      excludeSemantics: true,
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTapDown: (_) {
          _set(true);
          HapticFeedback.selectionClick();
        },
        onTapUp: (_) => _set(false),
        onTapCancel: () => _set(false),
        onTap: widget.onTap,
        onLongPress: widget.onLongPress == null
            ? null
            : () {
                _set(false);
                HapticFeedback.mediumImpact();
                widget.onLongPress!();
              },
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 100),
          height: 56,
          alignment: .center,
          decoration: BoxDecoration(
            color: _pressed ? context.appColors.background : Colors.transparent,
            borderRadius: .circular(AppRadius.md),
          ),
          child: widget.child,
        ),
      ),
    );
  }
}
