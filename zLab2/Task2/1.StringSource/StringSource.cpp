#include <cryptlib.h>
#include <aes.h>
#include <modes.h>
#include <osrng.h>
#include <filters.h>
#include <hex.h>
#include <iostream>

using namespace CryptoPP;

int main()
{
    AutoSeededRandomPool prng;
    byte key[AES::DEFAULT_KEYLENGTH], iv[AES::BLOCKSIZE];
    prng.GenerateBlock(key, sizeof(key));
    prng.GenerateBlock(iv, sizeof(iv));

    std::string plaintext = "Crypto++ StringSource example";
    std::string ciphertext, hexEncoded;

    CBC_Mode<AES>::Encryption encryptor;
    encryptor.SetKeyWithIV(key, sizeof(key), iv);

    StringSource(plaintext, true,
                 new StreamTransformationFilter(encryptor,
                                                new StringSink(ciphertext)));

    StringSource(ciphertext, true,
                 new HexEncoder(new StringSink(hexEncoded)));

    std::cout << "Encrypted (hex): " << hexEncoded << std::endl;
    return 0;
}