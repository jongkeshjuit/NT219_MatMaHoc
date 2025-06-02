#include <rsa.h>
#include <osrng.h>
#include <queue.h>
#include <files.h>
#include <base64.h>
#include <filters.h>

using namespace CryptoPP;
// Lưu key dạng DER
template <class KEY>
void SaveKeyToDERFile(const KEY &key, const std::string &filename)
{
    ByteQueue queue;
    key.Save(queue);
    FileSink file(filename.c_str());
    queue.CopyTo(file);
    file.MessageEnd();
}

// Chuyển DER sang PEM
void DERToPEM(const std::string &derFilename, const std::string &pemFilename,
              const std::string &header, const std::string &footer)
{
    std::ifstream derFile(derFilename, std::ios::binary);
    std::vector<char> derData((std::istreambuf_iterator<char>(derFile)),
                              std::istreambuf_iterator<char>());
    derFile.close();

    std::string base64Data;
    StringSource ss(reinterpret_cast<const byte *>(derData.data()), derData.size(), true,
                    new Base64Encoder(new StringSink(base64Data), true, 64));

    std::ofstream pemFile(pemFilename);
    pemFile << header << std::endl;
    pemFile << base64Data;
    pemFile << footer << std::endl;
    pemFile.close();
}
int main()
{
    try
    {
        // Tạo random generator
        AutoSeededRandomPool rng;

        // Tạo khóa RSA 3072-bit
        RSA::PrivateKey privateKey;
        privateKey.GenerateRandomWithKeySize(rng, 3072);

        // Trích xuất public key
        RSA::PublicKey publicKey;
        publicKey.AssignFrom(privateKey);

        // Kiểm tra tính hợp lệ
        if (!privateKey.Validate(rng, 3) || !publicKey.Validate(rng, 3))
        {
            std::cerr << "Key validation failed" << std::endl;
            return 1;
        }

        // Lưu keys dạng DER
        SaveKeyToDERFile(privateKey, "private_key.der");
        SaveKeyToDERFile(publicKey, "public_key.der");

        // Chuyển sang PEM
        DERToPEM("private_key.der", "private_key.pem",
                 "-----BEGIN RSA PRIVATE KEY-----",
                 "-----END RSA PRIVATE KEY-----");

        DERToPEM("public_key.der", "public_key.pem",
                 "-----BEGIN PUBLIC KEY-----",
                 "-----END PUBLIC KEY-----");

        std::cout << "Keys generated and saved successfully." << std::endl;
    }
    catch (const Exception &e)
    {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}