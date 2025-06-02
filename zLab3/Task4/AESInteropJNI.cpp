#include <jni.h>
#include <aes.h>
#include <osrng.h>
#include <modes.h>
#include <filters.h>
#include <hex.h>
#include <files.h>
#include <cstring>
#include <iostream>

using namespace CryptoPP;

// Cross-platform export macro
#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT __attribute__((visibility("default")))
#endif

extern "C"
{

    // Generate AES key and IV
    void GenerateAESKey(byte *key, byte *iv)
    {
        AutoSeededRandomPool prng;
        prng.GenerateBlock(key, AES::DEFAULT_KEYLENGTH);
        prng.GenerateBlock(iv, AES::BLOCKSIZE);
    }

    // Save key/iv to binary file
    void SaveKeyToFile(const char *filename, const byte *key, const byte *iv)
    {
        FileSink fs(filename, true);
        fs.Put(key, AES::DEFAULT_KEYLENGTH);
        fs.Put(iv, AES::BLOCKSIZE);
        fs.MessageEnd();
    }

    // Load key/iv from binary file
    void LoadKeyFromFile(const char *filename, byte *key, byte *iv)
    {
        FileSource file(filename, false);
        file.Attach(new ArraySink(key, AES::DEFAULT_KEYLENGTH));
        file.Pump(AES::DEFAULT_KEYLENGTH);
        file.Attach(new ArraySink(iv, AES::BLOCKSIZE));
        file.Pump(AES::BLOCKSIZE);
    }

    // Encrypt plaintext using AES-CBC, output as hex string
    void AESEncrypt(const byte *key, const byte *iv, const char *plaintext, char *outHex, int outSize)
    {
        std::string ciphertext;
        CBC_Mode<AES>::Encryption encryptor;
        encryptor.SetKeyWithIV(key, AES::DEFAULT_KEYLENGTH, iv);

        StringSource(plaintext, true,
                     new StreamTransformationFilter(encryptor,
                                                    new StringSink(ciphertext)));

        // Convert to hex for easier transport across language boundaries
        std::string encoded;
        StringSource(ciphertext, true, new HexEncoder(new StringSink(encoded)));

        // Copy result to output buffer with null termination
        strncpy(outHex, encoded.c_str(), outSize - 1);
        outHex[outSize - 1] = '\0';
    }

    // Decrypt hex-encoded ciphertext using AES-CBC
    void AESDecrypt(const byte *key, const byte *iv, const char *hexCipher, char *outPlain, int outSize)
    {
        std::string decoded, recovered;

        // Convert from hex
        StringSource(hexCipher, true, new HexDecoder(new StringSink(decoded)));

        // Decrypt
        CBC_Mode<AES>::Decryption decryptor;
        decryptor.SetKeyWithIV(key, AES::DEFAULT_KEYLENGTH, iv);

        StringSource(decoded, true,
                     new StreamTransformationFilter(decryptor,
                                                    new StringSink(recovered)));

        // Copy result to output buffer with null termination
        strncpy(outPlain, recovered.c_str(), outSize - 1);
        outPlain[outSize - 1] = '\0';
    }

    // JNI wrapper functions
    EXPORT JNIEXPORT void JNICALL Java_AESInterop_GenerateAESKey(JNIEnv *env, jobject, jbyteArray key, jbyteArray iv)
    {
        jbyte *keyPtr = env->GetByteArrayElements(key, NULL);
        jbyte *ivPtr = env->GetByteArrayElements(iv, NULL);

        GenerateAESKey(reinterpret_cast<byte *>(keyPtr), reinterpret_cast<byte *>(ivPtr));

        env->ReleaseByteArrayElements(key, keyPtr, 0);
        env->ReleaseByteArrayElements(iv, ivPtr, 0);
    }

    EXPORT JNIEXPORT void JNICALL Java_AESInterop_SaveKeyToFile(JNIEnv *env, jobject, jstring filename, jbyteArray key, jbyteArray iv)
    {
        const char *filenamePtr = env->GetStringUTFChars(filename, NULL);
        jbyte *keyPtr = env->GetByteArrayElements(key, NULL);
        jbyte *ivPtr = env->GetByteArrayElements(iv, NULL);

        SaveKeyToFile(filenamePtr, reinterpret_cast<const byte *>(keyPtr), reinterpret_cast<const byte *>(ivPtr));

        env->ReleaseStringUTFChars(filename, filenamePtr);
        env->ReleaseByteArrayElements(key, keyPtr, JNI_ABORT);
        env->ReleaseByteArrayElements(iv, ivPtr, JNI_ABORT);
    }

    EXPORT JNIEXPORT void JNICALL Java_AESInterop_LoadKeyFromFile(JNIEnv *env, jobject, jstring filename, jbyteArray key, jbyteArray iv)
    {
        const char *filenamePtr = env->GetStringUTFChars(filename, NULL);
        jbyte *keyPtr = env->GetByteArrayElements(key, NULL);
        jbyte *ivPtr = env->GetByteArrayElements(iv, NULL);

        LoadKeyFromFile(filenamePtr, reinterpret_cast<byte *>(keyPtr), reinterpret_cast<byte *>(ivPtr));

        env->ReleaseStringUTFChars(filename, filenamePtr);
        env->ReleaseByteArrayElements(key, keyPtr, 0);
        env->ReleaseByteArrayElements(iv, ivPtr, 0);
    }

    EXPORT JNIEXPORT void JNICALL Java_AESInterop_AESEncrypt(JNIEnv *env, jobject, jbyteArray key, jbyteArray iv, jstring plaintext, jbyteArray outHex, jint outSize)
    {
        jbyte *keyPtr = env->GetByteArrayElements(key, NULL);
        jbyte *ivPtr = env->GetByteArrayElements(iv, NULL);
        const char *plaintextPtr = env->GetStringUTFChars(plaintext, NULL);
        jbyte *outHexPtr = env->GetByteArrayElements(outHex, NULL);

        AESEncrypt(reinterpret_cast<const byte *>(keyPtr), reinterpret_cast<const byte *>(ivPtr),
                   plaintextPtr, reinterpret_cast<char *>(outHexPtr), outSize);

        env->ReleaseByteArrayElements(key, keyPtr, JNI_ABORT);
        env->ReleaseByteArrayElements(iv, ivPtr, JNI_ABORT);
        env->ReleaseStringUTFChars(plaintext, plaintextPtr);
        env->ReleaseByteArrayElements(outHex, outHexPtr, 0);
    }

    EXPORT JNIEXPORT void JNICALL Java_AESInterop_AESDecrypt(JNIEnv *env, jobject, jbyteArray key, jbyteArray iv, jstring hexCipher, jbyteArray outPlain, jint outSize)
    {
        jbyte *keyPtr = env->GetByteArrayElements(key, NULL);
        jbyte *ivPtr = env->GetByteArrayElements(iv, NULL);
        const char *hexCipherPtr = env->GetStringUTFChars(hexCipher, NULL);
        jbyte *outPlainPtr = env->GetByteArrayElements(outPlain, NULL);

        AESDecrypt(reinterpret_cast<const byte *>(keyPtr), reinterpret_cast<const byte *>(ivPtr),
                   hexCipherPtr, reinterpret_cast<char *>(outPlainPtr), outSize);

        env->ReleaseByteArrayElements(key, keyPtr, JNI_ABORT);
        env->ReleaseByteArrayElements(iv, ivPtr, JNI_ABORT);
        env->ReleaseStringUTFChars(hexCipher, hexCipherPtr);
        env->ReleaseByteArrayElements(outPlain, outPlainPtr, 0);
    }

} // extern "C"