package uz.finora.finora

import android.os.Build
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.security.keystore.StrongBoxUnavailableException
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import java.security.KeyPairGenerator
import java.security.KeyStore
import java.security.PrivateKey
import java.security.Signature
import java.security.spec.ECGenParameterSpec

class MainActivity : FlutterActivity() {
    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, DeviceKey.CHANNEL)
            .setMethodCallHandler { call, result ->
                try {
                    when (call.method) {
                        "publicKey" -> result.success(DeviceKey.publicKey())
                        "sign" -> result.success(DeviceKey.sign(call.arguments as ByteArray))
                        "delete" -> {
                            DeviceKey.delete()
                            result.success(null)
                        }
                        else -> result.notImplemented()
                    }
                } catch (e: Exception) {
                    result.error("device_key", e.message, null)
                }
            }
    }
}

/**
 * ECDSA P-256 device key in Android Keystore (StrongBox when available).
 * The private key never leaves the Keystore (docs/security/03-mobile.md).
 */
private object DeviceKey {
    const val CHANNEL = "uz.finora/device_key"
    private const val ALIAS = "finora_device_key"

    private fun keyStore() = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }

    /** X.509 SubjectPublicKeyInfo, DER. */
    fun publicKey(): ByteArray {
        val ks = keyStore()
        if (!ks.containsAlias(ALIAS)) generate()
        return ks.getCertificate(ALIAS).publicKey.encoded
    }

    /** SHA256withECDSA, DER-encoded signature. */
    fun sign(data: ByteArray): ByteArray {
        val ks = keyStore()
        if (!ks.containsAlias(ALIAS)) generate()
        val key = ks.getKey(ALIAS, null) as PrivateKey
        return Signature.getInstance("SHA256withECDSA").run {
            initSign(key)
            update(data)
            sign()
        }
    }

    fun delete() {
        val ks = keyStore()
        if (ks.containsAlias(ALIAS)) ks.deleteEntry(ALIAS)
    }

    private fun generate() {
        try {
            generate(strongBox = Build.VERSION.SDK_INT >= Build.VERSION_CODES.P)
        } catch (e: StrongBoxUnavailableException) {
            generate(strongBox = false)
        }
    }

    private fun generate(strongBox: Boolean) {
        val spec = KeyGenParameterSpec.Builder(ALIAS, KeyProperties.PURPOSE_SIGN)
            .setAlgorithmParameterSpec(ECGenParameterSpec("secp256r1"))
            .setDigests(KeyProperties.DIGEST_SHA256)
            .apply {
                if (strongBox && Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                    setIsStrongBoxBacked(true)
                }
            }
            .build()
        KeyPairGenerator.getInstance(KeyProperties.KEY_ALGORITHM_EC, "AndroidKeyStore").run {
            initialize(spec)
            generateKeyPair()
        }
    }
}
