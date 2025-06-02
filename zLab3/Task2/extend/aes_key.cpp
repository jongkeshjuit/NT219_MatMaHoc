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
#include <secblock.h>

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
    key.CleanNew(AES::DEFAULT_KEYLENGTH);
    iv.CleanNew(AES::BLOCKSIZE);

    prng.GenerateBlock(key.BytePtr(), key.size());
    prng.GenerateBlock(iv.BytePtr(), iv.size());
}

// Save key and IV to binary file using FileSink
void SaveKeyToFile(const std::string &filename, const CryptoPP::SecByteBlock &key, const CryptoPP::SecByteBlock &iv)
{
    FileSink file(filename.c_str(), true);
    file.Put(key.BytePtr(), key.size());
    file.Put(iv.BytePtr(), iv.size());
    file.MessageEnd();
    std::cout << "Key and IV saved to: " << filename << std::endl;
}

// Load key and IV from binary file using FileSource and ArraySink
void LoadKeyFromFile(const std::string &filename, CryptoPP::byte key[], CryptoPP::byte iv[])
{
    try
    {
        FileSource file(filename.c_str(), false); // Don't PumpAll yet

        // Read key
        file.Attach(new ArraySink(key, AES::DEFAULT_KEYLENGTH));
        file.Pump(AES::DEFAULT_KEYLENGTH);

        // Reposition and read IV
        file.Attach(new ArraySink(iv, AES::BLOCKSIZE));
        file.Pump(AES::BLOCKSIZE);

        std::cout << "Key and IV loaded from file: " << filename << std::endl;
        PrintHex("Loaded Key", key, AES::DEFAULT_KEYLENGTH);
        PrintHex("Loaded IV", iv, AES::BLOCKSIZE);
    }
    catch (const CryptoPP::Exception &e)
    {
        std::cerr << "Error loading key and IV: " << e.what() << std::endl;
    }
}

// Save key and IV to memory buffer using ArraySink
void SaveKeyToBuffer(SecByteBlock &buffer, const CryptoPP::byte key[], const CryptoPP::byte iv[])
{
    buffer.CleanNew(AES::DEFAULT_KEYLENGTH + AES::BLOCKSIZE);
    memcpy(buffer, key, AES::DEFAULT_KEYLENGTH);
    memcpy(buffer + AES::DEFAULT_KEYLENGTH, iv, AES::BLOCKSIZE);
    std::cout << "Key and IV saved to memory buffer." << std::endl;
    PrintHex("Saved Key to Buffer", key, AES::DEFAULT_KEYLENGTH);
    PrintHex("Saved IV to Buffer", iv, AES::BLOCKSIZE);
}

// Load key and IV from memory buffer
void LoadKeyFromBuffer(const SecByteBlock &buffer, byte key[], byte iv[])
{
    ArraySource source(buffer, buffer.size(), true);
    source.Get(key, AES::DEFAULT_KEYLENGTH);
    source.Get(iv, AES::BLOCKSIZE);
    std::cout << "Key and IV loaded from memory buffer." << std::endl;
    PrintHex("Loaded Key from Buffer", key, AES::DEFAULT_KEYLENGTH);
    PrintHex("Loaded IV from Buffer", iv, AES::BLOCKSIZE);
}

int main()
{
    // Create SecByteBlock objects for key and IV
    SecByteBlock key(AES::DEFAULT_KEYLENGTH);
    SecByteBlock iv(AES::BLOCKSIZE);

    // Generate AES key and IV
    GenerateAESKey(key, iv);
    PrintHex("Generated Key", key.BytePtr(), key.size());
    PrintHex("Generated IV", iv.BytePtr(), iv.size());

    // Save and Load via file
    SaveKeyToFile("keydata.bin", key, iv);
    byte fileKey[AES::DEFAULT_KEYLENGTH], fileIV[AES::BLOCKSIZE];
    LoadKeyFromFile("keydata.bin", fileKey, fileIV);

    // Save and Load via memory buffer
    SecByteBlock buffer;
    SaveKeyToBuffer(buffer, key.BytePtr(), iv.BytePtr());
    byte bufKey[AES::DEFAULT_KEYLENGTH], bufIV[AES::BLOCKSIZE];
    LoadKeyFromBuffer(buffer, bufKey, bufIV);

    return 0;
}