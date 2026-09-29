import 'package:flutter/widgets.dart';

/// Builds spans from a localized template with `{name}` slots, so word order
/// can differ per language:
///
/// ```dart
/// templateSpans('Sent to {phone}. {change}', {
///   'phone': TextSpan(text: phone, style: bold),
///   'change': TextSpan(text: 'Change', recognizer: ...),
/// })
/// ```
List<InlineSpan> templateSpans(String template, Map<String, InlineSpan> slots) {
  final spans = <InlineSpan>[];
  var start = 0;
  for (final m in RegExp(r'\{(\w+)\}').allMatches(template)) {
    final slot = slots[m.group(1)];
    if (slot == null) continue;
    if (m.start > start) {
      spans.add(TextSpan(text: template.substring(start, m.start)));
    }
    spans.add(slot);
    start = m.end;
  }
  if (start < template.length) {
    spans.add(TextSpan(text: template.substring(start)));
  }
  return spans;
}
