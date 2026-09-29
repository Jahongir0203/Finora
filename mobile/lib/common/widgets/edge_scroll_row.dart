import 'package:flutter/material.dart';

/// Horizontal scroller that bleeds past its parent's [inset] padding so
/// items scroll edge to edge (chips in sheets, day pickers).
class EdgeScrollRow extends StatelessWidget {
  final double height;
  final double inset;
  final double spacing;
  final List<Widget> children;

  const EdgeScrollRow({
    super.key,
    required this.height,
    required this.children,
    this.inset = 20,
    this.spacing = 8,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final width = constraints.maxWidth + inset * 2;
        return SizedBox(
          height: height,
          child: OverflowBox(
            minWidth: width,
            maxWidth: width,
            child: ListView(
              scrollDirection: Axis.horizontal,
              padding: .symmetric(horizontal: inset),
              children: [
                for (var i = 0; i < children.length; i++) ...[
                  if (i > 0) SizedBox(width: spacing),
                  children[i],
                ],
              ],
            ),
          ),
        );
      },
    );
  }
}
