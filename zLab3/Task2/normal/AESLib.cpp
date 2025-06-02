#include <aes.h>
#include <osrng.h>
#include <modes.h>
#include <filters.h>
#include <hex.h>
#include <files.h>
#include <cstring>

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
    EXPORT void GenerateAESKey(byte *key, byte *iv)
    {
        AutoSeededRandomPool prng;
        prng.GenerateBlock(key, AES::DEFAULT_KEYLENGTH);
        prng.GenerateBlock(iv, AES::BLOCKSIZE);
    }

    // Save key/iv to binary file
    EXPORT void SaveKeyToFile(const char *filename, const byte *key, const byte *iv)
    {
        FileSink fs(filename, true);
        fs.Put(key, AES::DEFAULT_KEYLENGTH);
        fs.Put(iv, AES::BLOCKSIZE);
        fs.MessageEnd();
    }

    // Load key/iv from binary file
    EXPORT void LoadKeyFromFile(const char *filename, byte *key, byte *iv)
    {
        FileSource file(filename, false);
        file.Attach(new ArraySink(key, AES::DEFAULT_KEYLENGTH));
        file.Pump(AES::DEFAULT_KEYLENGTH);
        file.Attach(new ArraySink(iv, AES::BLOCKSIZE));
        file.Pump(AES::BLOCKSIZE);
    }

    // Encrypt plaintext using AES-CBC, output as hex string
    EXPORT void AESEncrypt(const byte *key, const byte *iv, const char *plaintext, char *outHex, int outSize)
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
    EXPORT void AESDecrypt(const byte *key, const byte *iv, const char *hexCipher, char *outPlain, int outSize)
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

    // For file operations
    EXPORT void AESEncryptFile(const byte *key, const byte *iv, const char *inFile, const char *outFile)
    {
        CBC_Mode<AES>::Encryption encryptor;
        encryptor.SetKeyWithIV(key, AES::DEFAULT_KEYLENGTH, iv);

        FileSource(inFile, true,
                   new StreamTransformationFilter(encryptor,
                                                  new FileSink(outFile)));
    }

    EXPORT void AESDecryptFile(const byte *key, const byte *iv, const char *inFile, const char *outFile)
    {
        CBC_Mode<AES>::Decryption decryptor;
        decryptor.SetKeyWithIV(key, AES::DEFAULT_KEYLENGTH, iv);

        FileSource(inFile, true,
                   new StreamTransformationFilter(decryptor,
                                                  new FileSink(outFile)));
    }

} // extern "C"