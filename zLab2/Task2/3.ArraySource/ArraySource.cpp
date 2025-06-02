#include <cryptlib.h>
#include <aes.h>
#include <modes.h>
#include <osrng.h>
#include <filters.h>
#include <secblock.h>
#include <iostream>

using namespace CryptoPP;

int main()
{
    AutoSeededRandomPool prng;
    byte key[AES::DEFAULT_KEYLENGTH], iv[AES::BLOCKSIZE];
    prng.GenerateBlock(key, sizeof(key));
    prng.GenerateBlock(iv, sizeof(iv));

    byte input[] = "Array input";
    byte output[64];
    size_t outputLen = 0;

    CBC_Mode<AES>::Encryption encryptor;
    encryptor.SetKeyWithIV(key, sizeof(key), iv);

    ArraySink sink(output, sizeof(output));
    ArraySource(input, sizeof(input) - 1, true,
                new StreamTransformationFilter(encryptor,
                                               new Redirector(sink)));

    outputLen = sink.TotalPutLength();

    std::cout << "Encrypted " << outputLen << " bytes using ArraySource → ArraySink." << std::endl;
    return 0;
}