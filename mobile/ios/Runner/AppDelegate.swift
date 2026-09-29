import Flutter
import Security
import UIKit

@main
@objc class AppDelegate: FlutterAppDelegate, FlutterImplicitEngineDelegate {
  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }

  func didInitializeImplicitFlutterEngine(_ engineBridge: FlutterImplicitEngineBridge) {
    GeneratedPluginRegistrant.register(with: engineBridge.pluginRegistry)
    if let registrar = engineBridge.pluginRegistry.registrar(forPlugin: "FinoraDeviceKey") {
      DeviceKey.register(messenger: registrar.messenger())
    }
  }
}

/// ECDSA P-256 device key in the Secure Enclave (software Keychain key on the
/// simulator). The private key never leaves the device (docs/security/03-mobile.md).
enum DeviceKey {
  static let channel = "uz.finora/device_key"
  private static let tag = "uz.finora.device_key".data(using: .utf8)!

  /// SubjectPublicKeyInfo prefix for an uncompressed P-256 point.
  private static let spkiPrefix: [UInt8] = [
    0x30, 0x59, 0x30, 0x13, 0x06, 0x07, 0x2A, 0x86, 0x48, 0xCE, 0x3D, 0x02, 0x01,
    0x06, 0x08, 0x2A, 0x86, 0x48, 0xCE, 0x3D, 0x03, 0x01, 0x07, 0x03, 0x42, 0x00,
  ]

  static func register(messenger: FlutterBinaryMessenger) {
    FlutterMethodChannel(name: channel, binaryMessenger: messenger)
      .setMethodCallHandler { call, result in
        do {
          switch call.method {
          case "publicKey":
            result(FlutterStandardTypedData(bytes: try publicKey()))
          case "sign":
            guard let data = call.arguments as? FlutterStandardTypedData else {
              return result(FlutterError(code: "device_key", message: "no data", details: nil))
            }
            result(FlutterStandardTypedData(bytes: try sign(data.data)))
          case "delete":
            delete()
            result(nil)
          default:
            result(FlutterMethodNotImplemented)
          }
        } catch {
          result(FlutterError(code: "device_key", message: "\(error)", details: nil))
        }
      }
  }

  /// X.509 SubjectPublicKeyInfo, DER.
  static func publicKey() throws -> Data {
    let key = try privateKey()
    guard let pub = SecKeyCopyPublicKey(key) else { throw KeyError.noPublicKey }
    var error: Unmanaged<CFError>?
    guard let raw = SecKeyCopyExternalRepresentation(pub, &error) as Data? else {
      throw error!.takeRetainedValue() as Error
    }
    return Data(spkiPrefix) + raw
  }

  /// ECDSA-SHA256, DER (X9.62) signature.
  static func sign(_ data: Data) throws -> Data {
    var error: Unmanaged<CFError>?
    guard
      let sig = SecKeyCreateSignature(
        try privateKey(), .ecdsaSignatureMessageX962SHA256, data as CFData, &error) as Data?
    else { throw error!.takeRetainedValue() as Error }
    return sig
  }

  static func delete() {
    SecItemDelete(
      [
        kSecClass: kSecClassKey,
        kSecAttrApplicationTag: tag,
      ] as CFDictionary)
  }

  private static func privateKey() throws -> SecKey {
    var item: CFTypeRef?
    let status = SecItemCopyMatching(
      [
        kSecClass: kSecClassKey,
        kSecAttrApplicationTag: tag,
        kSecAttrKeyType: kSecAttrKeyTypeECSECPrimeRandom,
        kSecReturnRef: true,
      ] as CFDictionary, &item)
    if status == errSecSuccess, let item { return item as! SecKey }
    return try generate()
  }

  private static func generate() throws -> SecKey {
    var error: Unmanaged<CFError>?
    var privateAttrs: [CFString: Any] = [
      kSecAttrIsPermanent: true,
      kSecAttrApplicationTag: tag,
    ]
    var attributes: [CFString: Any] = [
      kSecAttrKeyType: kSecAttrKeyTypeECSECPrimeRandom,
      kSecAttrKeySizeInBits: 256,
    ]
    #if targetEnvironment(simulator)
      privateAttrs[kSecAttrAccessible] = kSecAttrAccessibleWhenUnlockedThisDeviceOnly
    #else
      guard
        let access = SecAccessControlCreateWithFlags(
          nil, kSecAttrAccessibleWhenUnlockedThisDeviceOnly, .privateKeyUsage, &error)
      else { throw error!.takeRetainedValue() as Error }
      privateAttrs[kSecAttrAccessControl] = access
      attributes[kSecAttrTokenID] = kSecAttrTokenIDSecureEnclave
    #endif
    attributes[kSecPrivateKeyAttrs] = privateAttrs

    guard let key = SecKeyCreateRandomKey(attributes as CFDictionary, &error) else {
      throw error!.takeRetainedValue() as Error
    }
    return key
  }

  enum KeyError: Error { case noPublicKey }
}
