import 'package:finora/domain/models/exports/export_models.dart';

abstract class ExportsFacade {
  Future<ExportPreview> preview(
    ExportPeriod period,
    ExportInclude include,
    ExportFormat format,
  );

  /// `POST /exports`, then waits until the file is rendered.
  Future<ExportFile> export(
    ExportPeriod period,
    ExportInclude include,
    ExportFormat format,
  );
}
