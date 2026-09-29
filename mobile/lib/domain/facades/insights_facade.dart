import 'package:finora/domain/models/insights/insight.dart';

abstract class InsightsFacade {
  /// `GET /insights`.
  Future<InsightList> getInsights({bool includeDismissed = false});

  /// `POST /insights/{id}/action`: sets the budget / reminder / auto-save.
  Future<void> act(String id);

  /// `POST /insights/{id}/dismiss`.
  Future<void> dismiss(String id);

  /// `GET /ai/suggestions`: quick questions for the chat.
  Future<List<String>> suggestions();

  /// `POST /ai/ask`. Plain-text answer.
  Future<String> ask(String question);
}
