import 'package:finora/domain/facades/receipts_facade.dart';
import 'package:finora/domain/models/receipts/receipt.dart';
import 'package:injectable/injectable.dart';

import '../dto/finance_dto.dart';
import '../services/http/api_client.dart';

/// `/receipts`. Without an OCR / tax API provider the server answers
/// `503 ocr_unavailable`; the message is shown as is.
@LazySingleton(as: ReceiptsFacade)
class ReceiptsDatasource implements ReceiptsFacade {
  final ApiClient _api;

  ReceiptsDatasource(this._api);

  @override
  Future<Receipt> scan(List<int> image, {required String contentType}) async =>
      _map(
        await _api.postBytes(
          '/receipts/scan',
          image,
          contentType: contentType,
        ),
      );

  @override
  Future<Receipt> fromQr(String payload) async => _map(
    await _api.post('/receipts/qr', idempotent: true, data: {'payload': payload}),
  );

  static Receipt _map(Json j) {
    final at = j['occurred_at'] as String?;
    return Receipt(
      id: j['receipt_id'] ?? j['id'],
      merchant: j['merchant'],
      date: at == null ? null : DateTime.parse(at).toLocal(),
      total: j['total'],
      suggestedCategoryId: j['suggested_category_id'],
      items: [
        for (final i in j['items'])
          ReceiptItem(i['name'], i['quantity'], i['price']),
      ],
    );
  }
}
