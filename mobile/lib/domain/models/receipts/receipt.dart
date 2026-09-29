/// Scanned receipt (`ReceiptOut`), not saved as a transaction yet.
class Receipt {
  /// Passed as `receipt_id` when the transaction is saved; unconfirmed
  /// receipts are removed by the server after 24 h.
  final String id;
  final String? merchant;
  final DateTime? date;
  final num? total;
  final String? suggestedCategoryId;
  final List<ReceiptItem> items;

  const Receipt({
    required this.id,
    required this.items,
    this.merchant,
    this.date,
    this.total,
    this.suggestedCategoryId,
  });
}

class ReceiptItem {
  final String name;
  final num quantity;
  final num price;

  const ReceiptItem(this.name, this.quantity, this.price);
}
