#include <cryptlib.h>
#include <aes.h>
#include <modes.h>
#include <osrng.h>
#include <filters.h>
#include <files.h>
#include <iostream>

using namespace CryptoPP;

int main()
{
    AutoSeededRandomPool prng;
    byte key[AES::DEFAULT_KEYLENGTH], iv[AES::BLOCKSIZE];
    prng.GenerateBlock(key, sizeof(key));
    prng.GenerateBlock(iv, sizeof(iv));

    CBC_Mode<AES>::Encryption encryptor;
    encryptor.SetKeyWithIV(key, sizeof(key), iv);

    FileSource("plaintext.txt", true,
               new StreamTransformationFilter(encryptor,
                                              new FileSink("ciphertext.bin")));

    std::cout << "File encrypted and saved as ciphertext.bin" << std::endl;
    return 0;
}
