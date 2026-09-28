import 'dart:async';

import 'package:finora/di.dart';
import 'package:finora/infrastructure/services/security/auto_lock_service.dart';
import 'package:finora/presentation/pages/pin/pin_lock_page.dart';
import 'package:finora/presentation/routes/app_router.dart';
import 'package:flutter/widgets.dart';

/// Locks the signed-in area after inactivity or a long stay in the
/// background (docs/screens/PIN_SETUP_SCREENS.md §4, Auto-lock).
///
/// Every tap resets the timer. Screens outside [child] (auth, setup, lock)
/// are not covered, as the spec requires.
class AutoLockGuard extends StatefulWidget {
  final Widget child;

  const AutoLockGuard({super.key, required this.child});

  @override
  State<AutoLockGuard> createState() => _AutoLockGuardState();
}

class _AutoLockGuardState extends State<AutoLockGuard>
    with WidgetsBindingObserver {
  final _service = di<AutoLockService>();
  Timer? _timer;
  var _resumed = true;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _service.touch();
    _timer = Timer.periodic(const Duration(seconds: 1), (_) => _check());
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    _resumed = state == AppLifecycleState.resumed;
    if (_resumed) _check();
  }

  void _check() {
    if (!_resumed || !_service.expired) return;
    _service.locked = true;
    router.push(PinLockRoute(reason: LockReason.autoLock));
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Listener(
      behavior: HitTestBehavior.translucent,
      onPointerDown: (_) => _service.touch(),
      onPointerSignal: (_) => _service.touch(),
      child: widget.child,
    );
  }
}
