import 'package:injectable/injectable.dart';

/// Face ID / fingerprint unlock.
///
/// TODO: implement with `local_auth` (needs NSFaceIDUsageDescription on iOS
/// and FlutterFragmentActivity on Android). Until then the Face ID key on
/// the lock screen stays hidden.
@LazySingleton()
class BiometricService {
  Future<bool> isAvailable() async => false;

  Future<bool> authenticate() async => false;
}
