import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/words/words.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// 3×4 PIN keypad on `primary900` (docs/screens/PIN_SETUP_SCREENS.md §2).
///
/// The bottom-left key is Face ID when [onFace] is set, otherwise empty.
class PinKeypad extends StatelessWidget {
  final ValueChanged<String> onDigit;
  final VoidCallback onDelete;
  final VoidCallback? onFace;
  final bool enabled;

  const PinKeypad({
    super.key,
    required this.onDigit,
    required this.onDelete,
    this.onFace,
    this.enabled = true,
  });

  @override
  Widget build(BuildContext context) {
    Widget digit(String d) => _Key(
      semanticLabel: d,
      onTap: enabled ? () => onDigit(d) : null,
      child: Text(
        d,
        style: AppTypography.display.copyWith(
          fontSize: 28,
          height: 1,
          fontWeight: .w500,
          letterSpacing: 0,
          color: AppPalette.white,
        ),
      ),
    );

    final rows = [
      [digit('1'), digit('2'), digit('3')],
      [digit('4'), digit('5'), digit('6')],
      [digit('7'), digit('8'), digit('9')],
      [
        onFace == null
            ? const SizedBox(height: 68)
            : _Key(
                semanticLabel: 'Face ID',
                onTap: enabled ? onFace : null,
                child: const Icon(
                  FinoraIcons.faceId,
                  size: 28,
                  color: AppPalette.primary200,
                ),
              ),
        digit('0'),
        _Key(
          semanticLabel: Words.delete.str,
          onTap: enabled ? onDelete : null,
          child: const Icon(
            FinoraIcons.delete,
            size: 26,
            color: AppPalette.white,
          ),
        ),
      ],
    ];

    return Padding(
      padding: const .symmetric(horizontal: 12),
      child: Column(
        spacing: 10,
        children: [
          for (final row in rows)
            Row(
              spacing: 18,
              children: [for (final key in row) Expanded(child: key)],
            ),
        ],
      ),
    );
  }
}

class _Key extends StatefulWidget {
  final Widget child;
  final VoidCallback? onTap;
  final String semanticLabel;

  const _Key({
    required this.child,
    required this.onTap,
    required this.semanticLabel,
  });

  @override
  State<_Key> createState() => _KeyState();
}

class _KeyState extends State<_Key> {
  var _down = false;

  void _set(bool v) {
    if (widget.onTap != null && _down != v) setState(() => _down = v);
  }

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      label: widget.semanticLabel,
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTapDown: (_) => _set(true),
        onTapUp: (_) => _set(false),
        onTapCancel: () => _set(false),
        onTap: widget.onTap == null
            ? null
            : () {
                HapticFeedback.selectionClick();
                widget.onTap!();
              },
        child: Center(
          child: AnimatedScale(
            scale: _down ? 0.94 : 1,
            duration: const Duration(milliseconds: 120),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 120),
              width: 68,
              height: 68,
              alignment: .center,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: _down ? AppPalette.pinKeyPressed : Colors.transparent,
              ),
              child: ExcludeSemantics(child: widget.child),
            ),
          ),
        ),
      ),
    );
  }
}
