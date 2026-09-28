import 'package:finora/presentation/routes/app_router.dart';
import 'package:easy_localization/easy_localization.dart';

extension DateTimeExtension on DateTime {
  String get dateStr => DateFormat(
    'dd.MM.yyyy',
    router.navigatorKey.currentContext?.locale.languageCode,
  ).format(this);

  String get dateTimeStr => DateFormat(
    'dd.MM.yyyy HH:mm',
    router.navigatorKey.currentContext?.locale.languageCode,
  ).format(this);
}

extension DateTimeParsingExtension on String {
  DateTime? get toDateTime => DateTime.tryParse(this);

  DateTime? get toDateOnly {
    final date = DateTime.tryParse(this);
    if (date == null) {
      return null;
    }
    return DateTime(date.year, date.month, date.day);
  }
}

/// Display formats from docs/DESIGN_SYSTEM.md §11. UI language is English.
extension DateTimeDisplayExtension on DateTime {
  /// `Today`, `Yesterday`, `28 Sep`, or `28 Sep 2025` for other years.
  String get relativeDay {
    final now = DateTime.now();
    final today = DateTime.utc(now.year, now.month, now.day);
    final date = DateTime.utc(year, month, day);
    final diff = today.difference(date).inDays;

    if (diff == 0) return 'Today';
    if (diff == 1) return 'Yesterday';
    if (year == now.year) return DateFormat('d MMM', 'en').format(this);
    return DateFormat('d MMM y', 'en').format(this);
  }

  /// 24h time: `14:20`.
  String get time24 => DateFormat('HH:mm', 'en').format(this);

  /// `Today, 14:20`.
  String get relativeDayTime => '$relativeDay, $time24';

  /// `Dec 2027`.
  String get monthYear => DateFormat('MMM y', 'en').format(this);
}
