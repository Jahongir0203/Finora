import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_pressable.dart';
import 'package:finora/common/words/words.dart';
import 'package:flutter/material.dart';

/// "Upcoming payments" / "Recent transactions" + "See all".
class HomeSectionHeader extends StatelessWidget {
  final String title;
  final VoidCallback onSeeAll;

  const HomeSectionHeader({
    super.key,
    required this.title,
    required this.onSeeAll,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Row(
      children: [
        Expanded(
          child: Semantics(
            header: true,
            child: Text(title, style: context.textStyles.titleSmall),
          ),
        ),
        AppPressable(
          onTap: onSeeAll,
          child: Padding(
            padding: const .symmetric(vertical: AppSpacing.xs),
            child: Text(
              Words.seeAll.str,
              style: AppTypography.button.copyWith(
                fontSize: 14,
                height: 20 / 14,
                color: c.primaryText,
              ),
            ),
          ),
        ),
      ],
    );
  }
}
