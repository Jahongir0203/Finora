import 'dart:async';

import 'package:bloc/bloc.dart';
import 'package:finora/domain/facades/finance_facade.dart';
import 'package:finora/domain/models/finance/finance_models.dart';
import 'package:injectable/injectable.dart';

/// Live [FinanceSnapshot] for the signed-in screens. Writes go through
/// [facade]; the new snapshot arrives via its change stream.
@Injectable()
class FinanceCubit extends Cubit<FinanceSnapshot> {
  final FinanceFacade facade;
  late final StreamSubscription<FinanceSnapshot> _sub;

  FinanceCubit(this.facade) : super(facade.snapshot) {
    _sub = facade.changes.listen(emit);
  }

  @override
  Future<void> close() {
    _sub.cancel();
    return super.close();
  }
}
