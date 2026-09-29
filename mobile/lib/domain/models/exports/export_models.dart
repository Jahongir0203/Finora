enum ExportPeriod { daily, weekly, monthly, yearly }

enum ExportFormat { pdf, xlsx, csv }

/// Transaction types to include: `expense`, `income`, `transfer`.
typedef ExportInclude = Set<String>;

/// `GET /exports/preview`.
class ExportPreview {
  final int count;
  final num income;
  final num expenses;
  final num net;

  /// Localized by the server, e.g. `September 2026`.
  final String rangeLabel;
  final String fileName;

  const ExportPreview({
    required this.count,
    required this.income,
    required this.expenses,
    required this.net,
    required this.rangeLabel,
    required this.fileName,
  });
}

/// Ready report: [downloadUrl] is signed, one-time and valid for 5 minutes.
class ExportFile {
  final String fileName;
  final String downloadUrl;

  const ExportFile({required this.fileName, required this.downloadUrl});
}
