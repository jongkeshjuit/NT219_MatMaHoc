#include <iostream>
#include <string>

// Crypto++ Headers
#include <cryptlib.h>
#include <hex.h>
#include <filters.h>
#include <aes.h>
#include <modes.h>
#include <osrng.h>
#include <files.h>
#include <secblock.h> //bytes

using namespace CryptoPP;

// Helper function to print byte arrays in hex format
void PrintHex(const std::string &label, const CryptoPP::byte *data, size_t length)
{
    std::string encoded;
    StringSource(data, length, true,
                 new HexEncoder(
                     new StringSink(encoded)));
    std::cout << label << ": " << encoded << std::endl;
}

// Generate random AES key and IV
void GenerateAESKey(CryptoPP::SecByteBlock &key, CryptoPP::SecByteBlock &iv)
{
    AutoSeededRandomPool prng;
    prng.GenerateBlock(key, key.size());
    prng.GenerateBlock(iv, iv.size());
}

// Save key and IV to binary file
void SaveKeyToFile(const std::string &filename, const CryptoPP::SecByteBlock &key, const CryptoPP::SecByteBlock &iv)
{
    FileSink file(filename.c_str(), true);
    file.Put(key.BytePtr(), key.size());
    file.Put(iv.BytePtr(), iv.size());
    file.MessageEnd();
    std::cout << "Key and IV saved to: " << filename << std::endl;
}

// Load key and IV from binary file
void LoadKeyFromFile(const std::string &filename, CryptoPP::SecByteBlock &key, CryptoPP::SecByteBlock &iv)
{
    try
    {
        FileSource file(filename.c_str(), false);
        file.Attach(new ArraySink(key.BytePtr(), key.size()));
        file.Pump(AES::DEFAULT_KEYLENGTH);
        file.Attach(new ArraySink(iv.BytePtr(), iv.size()));
        file.Pump(AES::BLOCKSIZE);

        std::cout << "Key and IV loaded from file: " << filename << std::endl;
        PrintHex("Loaded Key", key.BytePtr(), key.size());
        PrintHex("Loaded IV", iv.BytePtr(), iv.size());
    }
    catch (const CryptoPP::Exception &e)
    {
        std::cerr << "Error loading key and IV: " << e.what() << std::endl;
    }
}

// Save key and IV to buffer
void SaveKeyToBuffer(SecByteBlock &buffer, const SecByteBlock &key, const SecByteBlock &iv)
{
    memcpy(buffer.BytePtr(), key.BytePtr(), key.size());
    memcpy(buffer.BytePtr() + key.size(), iv.BytePtr(), iv.size());
    std::cout << "Key and IV saved to memory buffer." << std::endl;
}

// Load key and IV from memory buffer
void LoadKeyFromBuffer(const SecByteBlock &buffer, SecByteBlock &key, SecByteBlock &iv)
{
    memcpy(key.BytePtr(), buffer.BytePtr(), key.size());
    memcpy(iv.BytePtr(), buffer.BytePtr() + key.size(), iv.size());
    std::cout << "Key and IV loaded from memory buffer." << std::endl;
    PrintHex("Loaded Key from Buffer", key.BytePtr(), key.size());
    PrintHex("Loaded IV from Buffer", iv.BytePtr(), iv.size());
}

int main()
{
    SecByteBlock key(AES::DEFAULT_KEYLENGTH);
    SecByteBlock iv(AES::BLOCKSIZE);

    // Generate AES key and IV
    GenerateAESKey(key, iv);

    // Save and Load via file
    SaveKeyToFile("keydata.bin", key, iv);
    SecByteBlock fileKey(AES::DEFAULT_KEYLENGTH);
    SecByteBlock fileIV(AES::BLOCKSIZE);
    LoadKeyFromFile("keydata.bin", fileKey, fileIV);

    // Save and Load via memory buffer
    SecByteBlock buffer(AES::DEFAULT_KEYLENGTH + AES::BLOCKSIZE);
    SaveKeyToBuffer(buffer, key, iv);
    SecByteBlock bufKey(AES::DEFAULT_KEYLENGTH);
    SecByteBlock bufIV(AES::BLOCKSIZE);
    LoadKeyFromBuffer(buffer, bufKey, bufIV);

    return 0;
}
