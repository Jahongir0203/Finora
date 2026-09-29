import 'package:finora/domain/models/receipts/receipt.dart';

abstract class ReceiptsFacade {
  /// `POST /receipts/scan`: OCR of a photo (JPEG / PNG / HEIC).
  Future<Receipt> scan(List<int> image, {required String contentType});

  /// `POST /receipts/qr`: fiscal receipt QR payload.
  Future<Receipt> fromQr(String payload);
}
