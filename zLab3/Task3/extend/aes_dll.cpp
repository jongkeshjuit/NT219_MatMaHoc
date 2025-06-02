#include <aes.h>
#include <osrng.h>
#include <modes.h>
#include <filters.h>
#include <hex.h>
#include <files.h>
#include <cstring>

using namespace CryptoPP;

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

extern "C"
{

    // Exported: Generate AES key and IV (16 bytes each)
    EXPORT void GenerateAESKeyIV(byte *key, byte *iv)
    {
        AutoSeededRandomPool prng;
        prng.GenerateBlock(key, AES::DEFAULT_KEYLENGTH);
        prng.GenerateBlock(iv, AES::BLOCKSIZE);
    }

    // Exported: Save key/iv to binary file
    EXPORT void SaveKeyToFile(const char *filename, const byte *key, const byte *iv)
    {
        FileSink fs(filename);
        fs.Put(key, AES::DEFAULT_KEYLENGTH);
        fs.Put(iv, AES::BLOCKSIZE);
        fs.MessageEnd();
    }

    // Exported: Load key/iv from binary file
    EXPORT void LoadKeyFromFile(const char *filename, byte *key, byte *iv)
    {
        FileSource file(filename, false);
        file.Attach(new ArraySink(key, AES::DEFAULT_KEYLENGTH));
        file.Pump(AES::DEFAULT_KEYLENGTH);
        file.Attach(new ArraySink(iv, AES::BLOCKSIZE));
        file.Pump(AES::BLOCKSIZE);
    }

    // Exported: Encrypt plaintext to hex string
    EXPORT void AESEncrypt(const byte *key, const byte *iv, const char *plaintext, char *outHex, int outSize)
    {
        std::string ciphertext;
        CBC_Mode<AES>::Encryption encryptor(key, AES::DEFAULT_KEYLENGTH, iv);

        StringSource ss(plaintext, true,
                        new StreamTransformationFilter(encryptor,
                                                       new StringSink(ciphertext)));

        std::string encoded;
        StringSource(ciphertext, true, new HexEncoder(new StringSink(encoded)));

        strncpy(outHex, encoded.c_str(), outSize - 1);
        outHex[outSize - 1] = '\0';
    }

    // Exported: Decrypt hex string to plaintext
    EXPORT void AESDecrypt(const byte *key, const byte *iv, const char *hexCipher, char *outPlain, int outSize)
    {
        std::string decoded, recovered;
        StringSource(hexCipher, true, new HexDecoder(new StringSink(decoded)));

        CBC_Mode<AES>::Decryption decryptor(key, AES::DEFAULT_KEYLENGTH, iv);
        StringSource ss(decoded, true,
                        new StreamTransformationFilter(decryptor,
                                                       new StringSink(recovered)));

        strncpy(outPlain, recovered.c_str(), outSize - 1);
        outPlain[outSize - 1] = '\0';
    }

} // extern "C"