import 'package:flutter/widgets.dart';

import 'icons.dart';
import 'palette.dart';

/// Spending categories with their brand color and icon (§2.4).
enum AppCategory {
  groceries('Groceries', AppPalette.catGroceries, FinoraIcons.groceries),
  food('Food & drinks', AppPalette.catFood, FinoraIcons.food),
  transport('Transport', AppPalette.catTransport, FinoraIcons.transport),
  bills('Bills', AppPalette.catBills, FinoraIcons.bills),
  health('Health', AppPalette.catHealth, FinoraIcons.health),
  shopping('Shopping', AppPalette.catShopping, FinoraIcons.shopping),
  housing('Housing', AppPalette.catHousing, FinoraIcons.housing),
  subscriptions('Subscriptions', AppPalette.catSubs, FinoraIcons.subscriptions),
  transfers('Transfers', AppPalette.catTransfer, FinoraIcons.transfer);

  final String label;
  final Color color;
  final IconData icon;

  const AppCategory(this.label, this.color, this.icon);

  /// Icon container background: [color] at 12%.
  Color get tint => AppPalette.tintOf(color);

  static AppCategory? byName(String? name) =>
      values.where((e) => e.name == name).firstOrNull;
}

/// Bank card backgrounds (§2.5).
enum AppBankCard {
  kapitalbankUzcard('Kapitalbank', 'Uzcard', AppPalette.cardKapitalbank),
  hamkorbankHumo('Hamkorbank', 'Humo', AppPalette.cardHamkorbank),
  tbcVisa('TBC', 'Visa', AppPalette.cardTbc);

  final String bank;
  final String network;
  final Color background;

  const AppBankCard(this.bank, this.network, this.background);
}
