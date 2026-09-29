/// `GET /currencies` (rates from the Central Bank, daily).
class Currency {
  final String code;
  final String symbol;
  final String name;

  /// UZS for one unit, `null` for UZS itself.
  final num? rateToUzs;

  const Currency({
    required this.code,
    required this.symbol,
    required this.name,
    this.rateToUzs,
  });
}

class FaqItem {
  final String question;
  final String answer;

  const FaqItem(this.question, this.answer);
}

/// `GET /help/contacts`.
class SupportContacts {
  final String email;
  final String phone;

  /// Username without `@`.
  final String telegram;
  final bool liveChat;

  const SupportContacts({
    required this.email,
    required this.phone,
    required this.telegram,
    required this.liveChat,
  });
}
