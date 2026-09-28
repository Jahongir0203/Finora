class VerifyResult {
  final bool isNewUser;

  /// Whether a PIN already exists on this device.
  final bool hasPin;

  const VerifyResult({required this.isNewUser, required this.hasPin});
}
