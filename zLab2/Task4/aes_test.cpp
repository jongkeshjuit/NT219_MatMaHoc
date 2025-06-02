#include <iostream>
#include <string>
#include <cryptlib.h>
#include <hex.h>
#include <filters.h>
#include <aes.h>
#include <modes.h>
#include <osrng.h>
#include <files.h>
#include <secblock.h>

using namespace CryptoPP;

// Function to generate AES key and IV
void GenerateAESKey(SecByteBlock &key, SecByteBlock &iv)
{
    AutoSeededRandomPool prng;
    key.CleanNew(AES::DEFAULT_KEYLENGTH); // 16 bytes for AES-128
    iv.CleanNew(AES::BLOCKSIZE);          // 16 bytes for IV
    prng.GenerateBlock(key.BytePtr(), key.size());
    prng.GenerateBlock(iv.BytePtr(), iv.size());
}

// Function to save key and IV to a file
void SaveKeyToFile(const std::string &filename, const SecByteBlock &key, const SecByteBlock &iv)
{
    FileSink file(filename.c_str(), true);
    file.Put(key.BytePtr(), key.size());
    file.Put(iv.BytePtr(), iv.size());
    file.MessageEnd();
    std::cout << "Key and IV saved to: " << filename << std::endl;
}

// Function to load key and IV from a file
void LoadKeyFromFile(const std::string &filename, CryptoPP::byte key[], CryptoPP::byte iv[])
{
    FileSource file(filename.c_str(), false);
    file.Attach(new ArraySink(key, AES::DEFAULT_KEYLENGTH));
    file.Pump(AES::DEFAULT_KEYLENGTH);
    file.Attach(new ArraySink(iv, AES::BLOCKSIZE));
    file.Pump(AES::BLOCKSIZE);
    std::cout << "Key and IV loaded from file: " << filename << std::endl;
}

// Function to save key and IV to a memory buffer
void SaveKeyToBuffer(SecByteBlock &buffer, const std::string &filename)
{
    FileSource file(filename.c_str(), true);
    size_t size = file.MaxRetrievable();
    buffer.CleanNew(size);
    file.Get(buffer, size);
    std::cout << "Key and IV loaded into memory buffer from file: " << filename << std::endl;
}

// Function to load key and IV from a memory buffer
void LoadKeyFromBuffer(const SecByteBlock &buffer, CryptoPP::byte key[], CryptoPP::byte iv[])
{
    ArraySource source(buffer, buffer.size(), true);
    source.Get(key, AES::DEFAULT_KEYLENGTH);
    source.Get(iv, AES::BLOCKSIZE);
    std::cout << "Key and IV loaded from memory buffer." << std::endl;
}

// Function to encrypt plaintext using AES in CBC mode
std::string AESEncrypt(const std::string &plaintext, const CryptoPP::byte key[], const CryptoPP::byte iv[])
{
    std::string ciphertext;
    try
    {
        CBC_Mode<AES>::Encryption encryptor;
        encryptor.SetKeyWithIV(key, AES::DEFAULT_KEYLENGTH, iv);
        StringSource(plaintext, true,
                     new StreamTransformationFilter(encryptor,
                                                    new StringSink(ciphertext),
                                                    BlockPaddingSchemeDef::PKCS_PADDING));
    }
    catch (const Exception &e)
    {
        std::cerr << "Encryption Error: " << e.what() << std::endl;
    }
    return ciphertext;
}

// Function to decrypt ciphertext using AES in CBC mode
std::string AESDecrypt(const std::string &ciphertext, const CryptoPP::byte key[], const CryptoPP::byte iv[])
{
    std::string decryptedText;
    try
    {
        CBC_Mode<AES>::Decryption decryptor;
        decryptor.SetKeyWithIV(key, AES::DEFAULT_KEYLENGTH, iv);
        StringSource(ciphertext, true,
                     new StreamTransformationFilter(decryptor,
                                                    new StringSink(decryptedText),
                                                    BlockPaddingSchemeDef::PKCS_PADDING));
    }
    catch (const Exception &e)
    {
        std::cerr << "Decryption Error: " << e.what() << std::endl;
    }
    return decryptedText;
}

// Function to print data in hexadecimal format
void PrintHex(const std::string &label, const std::string &data)
{
    std::string encoded;
    StringSource(data, true, new HexEncoder(new StringSink(encoded)));
    std::cout << label << encoded << std::endl;
}

int main(int argc, char *argv[])
{
    if (argc < 2)
    {
        std::cerr << "Usage:\n"
                  << "  " << argv[0] << " generate <keyfile>\n"
                  << "  " << argv[0] << " load <keyfile>\n"
                  << "  " << argv[0] << " encrypt <keyfile> <plaintext>\n"
                  << "  " << argv[0] << " decrypt <keyfile> <ciphertext>\n";
        return 1;
    }

    std::string mode = argv[1];

    if (mode == "generate")
    {
        if (argc != 3)
        {
            std::cerr << "Usage: " << argv[0] << " generate <keyfile>\n";
            return 1;
        }
        std::string filename = argv[2];
        SecByteBlock key(AES::DEFAULT_KEYLENGTH);
        SecByteBlock iv(AES::BLOCKSIZE);
        GenerateAESKey(key, iv);
        SaveKeyToFile(filename, key, iv);
    }
    else if (mode == "load")
    {
        if (argc != 3)
        {
            std::cerr << "Usage: " << argv[0] << " load <keyfile>\n";
            return 1;
        }
        std::string filename = argv[2];
        CryptoPP::byte key[AES::DEFAULT_KEYLENGTH], iv[AES::BLOCKSIZE];
        LoadKeyFromFile(filename, key, iv);
    }
    else if (mode == "encrypt")
    {
        if (argc != 4)
        {
            std::cerr << "Usage: " << argv[0] << " encrypt <keyfile> <plaintext>\n";
            return 1;
        }
        std::string filename = argv[2];
        std::string plaintext = argv[3];
        CryptoPP::byte key[AES::DEFAULT_KEYLENGTH], iv[AES::BLOCKSIZE];
        LoadKeyFromFile(filename, key, iv);
        std::string ciphertext = AESEncrypt(plaintext, key, iv);
        PrintHex("Ciphertext (Hex): ", ciphertext);
    }
    else if (mode == "decrypt")
    {
        if (argc != 4)
        {
            std::cerr << "Usage: " << argv[0] << " decrypt <keyfile> <ciphertext>\n";
            return 1;
        }
        std::string filename = argv[2];
        std::string ciphertextHex = argv[3];
        std::string ciphertext;
        StringSource(ciphertextHex, true, new HexDecoder(new StringSink(ciphertext)));
        CryptoPP::byte key[AES::DEFAULT_KEYLENGTH], iv[AES::BLOCKSIZE];
        LoadKeyFromFile(filename, key, iv);
        std::string decryptedText = AESDecrypt(ciphertext, key, iv);
        std::cout << "Decrypted Text: " << decryptedText << std::endl;
    }
    else
    {
        std::cerr << "Invalid mode! Use: generate, load, encrypt, or decrypt\n";
        return 1;
    }

    return 0;
}