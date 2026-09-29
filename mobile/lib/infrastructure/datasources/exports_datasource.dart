import 'package:finora/common/words/words.dart';
import 'package:finora/domain/facades/exports_facade.dart';
import 'package:finora/domain/models/api_failure.dart';
import 'package:finora/domain/models/exports/export_models.dart';
import 'package:injectable/injectable.dart';

import '../services/http/api_client.dart';

/// `/exports`: preview, then an async job polled until it is ready.
@LazySingleton(as: ExportsFacade)
class ExportsDatasource implements ExportsFacade {
  static const _poll = Duration(seconds: 2);
  static const _timeout = Duration(minutes: 1);

  final ApiClient _api;

  ExportsDatasource(this._api);

  @override
  Future<ExportPreview> preview(
    ExportPeriod period,
    ExportInclude include,
    ExportFormat format,
  ) async {
    final j = await _api.get(
      '/exports/preview',
      query: {
        'period': period.name,
        'include': include.join(','),
        'format': format.name,
      },
    );
    return ExportPreview(
      count: j['count'],
      income: j['income'],
      expenses: j['expenses'],
      net: j['net'],
      rangeLabel: j['range_label'],
      fileName: j['file_name'],
    );
  }

  @override
  Future<ExportFile> export(
    ExportPeriod period,
    ExportInclude include,
    ExportFormat format,
  ) async {
    var job = await _api.post(
      '/exports',
      data: {
        'period': period.name,
        'include': include.toList(),
        'format': format.name,
      },
    );
    final deadline = DateTime.now().add(_timeout);
    while (job['status'] == 'pending' && DateTime.now().isBefore(deadline)) {
      await Future.delayed(_poll);
      job = await _api.get('/exports/${job['id']}');
    }
    final url = job['download_url'];
    if (job['status'] != 'ready' || url == null) {
      throw ApiFailure(
        status: 0,
        code: job['error_code'] ?? 'export_failed',
        message: Words.exportFailed.str,
      );
    }
    return ExportFile(fileName: job['file_name'], downloadUrl: url);
  }
}
