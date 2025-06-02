#include <iostream>
#include <fstream>
#include <string>
#include <cryptlib.h>
#include <hex.h>
#include <files.h>
#include <filters.h>
#include <aes.h>
#include <modes.h>
#include <osrng.h>
#include <secblock.h>

using namespace CryptoPP;

class AESTool
{
private:
    SecByteBlock key;
    SecByteBlock iv;
    AutoSeededRandomPool prng;

public:
    AESTool() : key(AES::DEFAULT_KEYLENGTH),
                iv(AES::BLOCKSIZE) {}

    // Generate new AES key and IV
    void generateKey()
    {
        prng.GenerateBlock(key.BytePtr(), key.size());
        prng.GenerateBlock(iv.BytePtr(), iv.size());
    }

    // Save key and IV to file
    void saveKeyToFile(const std::string &filename)
    {
        std::ofstream file(filename, std::ios::binary);
        file.write(reinterpret_cast<char *>(key.BytePtr()), key.size());
        file.write(reinterpret_cast<char *>(iv.BytePtr()), iv.size());
        file.close();
        std::cout << "Key saved to: " << filename << std::endl;
    }

    // Load key and IV from file
    void loadKeyFromFile(const std::string &filename)
    {
        std::ifstream file(filename, std::ios::binary);
        if (!file)
        {
            throw std::runtime_error("Cannot open key file");
        }
        file.read(reinterpret_cast<char *>(key.BytePtr()), key.size());
        file.read(reinterpret_cast<char *>(iv.BytePtr()), iv.size());
        file.close();
        std::cout << "Key loaded from: " << filename << std::endl;
    }

    // Encrypt string
    std::string encrypt(const std::string &plaintext)
    {
        std::string ciphertext;
        try
        {
            CBC_Mode<AES>::Encryption encryptor;
            encryptor.SetKeyWithIV(key.BytePtr(), key.size(), iv.BytePtr());

            StringSource(plaintext, true,
                         new StreamTransformationFilter(encryptor,
                                                        new StringSink(ciphertext),
                                                        BlockPaddingSchemeDef::PKCS_PADDING));
        }
        catch (const Exception &e)
        {
            std::cerr << "Encryption error: " << e.what() << std::endl;
        }
        return ciphertext;
    }

    // Decrypt string
    std::string decrypt(const std::string &ciphertext)
    {
        std::string decrypted;
        try
        {
            CBC_Mode<AES>::Decryption decryptor;
            decryptor.SetKeyWithIV(key.BytePtr(), key.size(), iv.BytePtr());

            StringSource(ciphertext, true,
                         new StreamTransformationFilter(decryptor,
                                                        new StringSink(decrypted),
                                                        BlockPaddingSchemeDef::PKCS_PADDING));
        }
        catch (const Exception &e)
        {
            std::cerr << "Decryption error: " << e.what() << std::endl;
        }
        return decrypted;
    }

    // Utility: Print key in hex
    void printKeyHex()
    {
        std::string encoded_key, encoded_iv;
        StringSource(key.BytePtr(), key.size(), true,
                     new HexEncoder(new StringSink(encoded_key)));
        StringSource(iv.BytePtr(), iv.size(), true,
                     new HexEncoder(new StringSink(encoded_iv)));
        std::cout << "Key (Hex): " << encoded_key << std::endl;
        std::cout << "IV  (Hex): " << encoded_iv << std::endl;
    }
};

int main(int argc, char *argv[])
{
    AESTool aes;

    if (argc < 2)
    {
        std::cerr << "Usage:\n"
                  << "  " << argv[0] << " generate <keyfile>\n"
                  << "  " << argv[0] << " encrypt <keyfile> <plaintext>\n"
                  << "  " << argv[0] << " decrypt <keyfile> <ciphertext>\n";
        return 1;
    }

    std::string mode = argv[1];

    try
    {
        if (mode == "generate")
        {
            if (argc != 3)
            {
                std::cerr << "Usage: " << argv[0] << " generate <keyfile>\n";
                return 1;
            }
            aes.generateKey();
            aes.printKeyHex();
            aes.saveKeyToFile(argv[2]);
        }
        else if (mode == "encrypt")
        {
            if (argc != 4)
            {
                std::cerr << "Usage: " << argv[0] << " encrypt <keyfile> <plaintext>\n";
                return 1;
            }
            aes.loadKeyFromFile(argv[2]);
            std::string ciphertext = aes.encrypt(argv[3]);
            std::string encoded;
            StringSource(ciphertext, true, new HexEncoder(new StringSink(encoded)));
            std::cout << "Ciphertext: " << encoded << std::endl;
        }
        else if (mode == "decrypt")
        {
            if (argc != 4)
            {
                std::cerr << "Usage: " << argv[0] << " decrypt <keyfile> <ciphertext>\n";
                return 1;
            }
            aes.loadKeyFromFile(argv[2]);
            std::string decrypted = aes.decrypt(argv[3]);
            std::cout << "Decrypted: " << decrypted << std::endl;
        }
        else
        {
            std::cerr << "Invalid mode. Use generate, encrypt, or decrypt.\n";
            return 1;
        }
    }
    catch (const std::exception &e)
    {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}