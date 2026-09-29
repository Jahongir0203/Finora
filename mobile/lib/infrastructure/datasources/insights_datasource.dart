import 'package:finora/domain/facades/insights_facade.dart';
import 'package:finora/domain/models/insights/insight.dart';
import 'package:injectable/injectable.dart';

import '../services/http/api_client.dart';

@LazySingleton(as: InsightsFacade)
class InsightsDatasource implements InsightsFacade {
  static const _actions = {
    'set_budget': InsightAction.setBudget,
    'remind_me': InsightAction.remindMe,
    'review': InsightAction.review,
    'turn_on_autosave': InsightAction.turnOn,
  };

  final ApiClient _api;

  InsightsDatasource(this._api);

  @override
  Future<InsightList> getInsights({bool includeDismissed = false}) async {
    final j = await _api.get(
      '/insights',
      query: {'include_dismissed': includeDismissed},
    );
    return InsightList([
      for (final i in j['items'])
        Insight(
          id: i['id'],
          icon: i['icon'],
          categoryId: i['category_id'],
          title: i['title'],
          body: i['body'],
          saving: i['saving'],
          action: _actions[i['action']] ?? InsightAction.review,
          dismissed: i['status'] == 'dismissed',
        ),
    ], j['potential_saving'] ?? 0);
  }

  @override
  Future<void> act(String id) => _api.post('/insights/$id/action');

  @override
  Future<void> dismiss(String id) => _api.post('/insights/$id/dismiss');

  @override
  Future<List<String>> suggestions() async {
    final j = await _api.get('/ai/suggestions');
    return [...(j['items'] as List).cast<String>()];
  }

  @override
  Future<String> ask(String question) async {
    final j = await _api.post('/ai/ask', data: {'question': question});
    return j['answer'];
  }
}
