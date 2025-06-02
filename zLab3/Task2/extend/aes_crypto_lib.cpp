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

    // Generate random AES key and IV
    EXPORT void GenerateAESKey(byte *key, byte *iv)
    {
        AutoSeededRandomPool prng;
        prng.GenerateBlock(key, AES::DEFAULT_KEYLENGTH);
        prng.GenerateBlock(iv, AES::BLOCKSIZE);
    }

    // Save key and IV to file
    EXPORT void SaveKeyToFile(const char *filename, const byte *key, const byte *iv)
    {
        FileSink fs(filename);
        fs.Put(key, AES::DEFAULT_KEYLENGTH);
        fs.Put(iv, AES::BLOCKSIZE);
        fs.MessageEnd();
    }

    // Load key and IV from file
    EXPORT void LoadKeyFromFile(const char *filename, byte *key, byte *iv)
    {
        FileSource file(filename, false);
        file.Attach(new ArraySink(key, AES::DEFAULT_KEYLENGTH));
        file.Pump(AES::DEFAULT_KEYLENGTH);
        file.Attach(new ArraySink(iv, AES::BLOCKSIZE));
        file.Pump(AES::BLOCKSIZE);
    }

    // AES-CBC Encryption (directly to file)
    EXPORT void AESEncryptFile(const char *inFilename, const char *outFilename, const byte *key, const byte *iv)
    {
        try
        {
            CBC_Mode<AES>::Encryption encryptor;
            encryptor.SetKeyWithIV(key, AES::DEFAULT_KEYLENGTH, iv);

            FileSource(inFilename, true,
                       new StreamTransformationFilter(encryptor,
                                                      new FileSink(outFilename)));
        }
        catch (const Exception &e)
        {
            // In a real library, you might want to handle this differently
            // For simplicity, we just re-throw
            throw e;
        }
    }

    // AES-CBC Decryption (directly from file)
    EXPORT void AESDecryptFile(const char *inFilename, const char *outFilename, const byte *key, const byte *iv)
    {
        try
        {
            CBC_Mode<AES>::Decryption decryptor;
            decryptor.SetKeyWithIV(key, AES::DEFAULT_KEYLENGTH, iv);

            FileSource(inFilename, true,
                       new StreamTransformationFilter(decryptor,
                                                      new FileSink(outFilename)));
        }
        catch (const Exception &e)
        {
            // In a real library, you might want to handle this differently
            throw e;
        }
    }

} // extern "C"