import 'package:finora/common/theme/core/functions.dart';
import 'package:flutter/widgets.dart';

// AI insights mock data (docs/screens/STATS_INSIGHTS.md §2).
// TODO: `/ai/recommendations` and `POST /ai/ask`.

enum RecAction { setBudget, remindMe, review, turnOn }

class Recommendation {
  final String id;
  final IconData icon;
  final Color color;
  final String title;
  final String body;
  final num? saving;
  final RecAction action;

  const Recommendation(
    this.id,
    this.icon,
    this.color,
    this.title,
    this.body,
    this.saving,
    this.action,
  );
}

/// Backend part of "potential savings" not tied to a visible tip.
const insightsBaseSavings = 321000;

const recommendations = [
  Recommendation(
    'food',
    FinoraIcons.food,
    AppPalette.catFood,
    'Cook at home more often',
    'You ordered delivery 14 times this month (920 000 UZS). Cooking three more evenings a week could save about 380 000 UZS.',
    380000,
    RecAction.setBudget,
  ),
  Recommendation(
    'taxi',
    FinoraIcons.transport,
    AppPalette.catTransport,
    'Take the metro on weekdays',
    'Taxi rides cost 460 000 UZS this month. Using the metro for weekday commutes would save around 300 000 UZS.',
    300000,
    RecAction.setBudget,
  ),
  Recommendation(
    'groc',
    FinoraIcons.groceries,
    AppPalette.catGroceries,
    'Shop on discount days',
    'Most of your grocery spending happens on weekends. Moving the big shop to Tuesday discounts can cut about 150 000 UZS.',
    150000,
    RecAction.remindMe,
  ),
  Recommendation(
    'subs',
    FinoraIcons.subscriptions,
    AppPalette.catSubs,
    'Overlapping subscriptions',
    'You pay for two streaming services and a music app. Cancelling one saves 89 000 UZS a month.',
    89000,
    RecAction.review,
  ),
  Recommendation(
    'auto',
    FinoraIcons.savings,
    AppPalette.catTransfer,
    'Automate your savings',
    'Your salary arrives on the 28th. Moving 10% to Emergency fund the same day keeps you on track for December 2027.',
    null,
    RecAction.turnOn,
  ),
];

const aiSuggestions = [
  'Where do I overspend?',
  'How much can I save?',
  'Compare with last month',
];

/// Mock answer for [question].
String mockAiAnswer(String question) => switch (question) {
  'Where do I overspend?' =>
    'Food & drinks is 15% over its 800 000 UZS budget, mostly from delivery on weekday evenings. Shopping comes next: Uzum Market orders make up 62% of it.',
  'How much can I save?' =>
    'About 1 240 000 UZS this month if you follow the tips below. The biggest wins are cooking at home and taking the metro on weekdays.',
  'Compare with last month' =>
    'You spent 8% less than last month. Groceries and transport went down, while shopping went up by 150 000 UZS.',
  _ =>
    'Based on your last 90 days, your biggest categories are groceries and shopping. Setting a limit for them is the easiest way to save.',
};
