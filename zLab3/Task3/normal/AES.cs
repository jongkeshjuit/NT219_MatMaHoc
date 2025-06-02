using System;
using System.Runtime.InteropServices;
using System.Text;

public class AESLib
{
    private const int AES_KEY_SIZE = 16;
    private const int AES_IV_SIZE = 16;
    private const int MAX_BUFFER_SIZE = 1024;

    // Import the DLL functions
    [DllImport("AESLib.dll", CallingConvention = CallingConvention.Cdecl)]
    private static extern void GenerateAESKey(byte[] key, byte[] iv);

    [DllImport("AESLib.dll", CallingConvention = CallingConvention.Cdecl)]
    private static extern void SaveKeyToFile(string filename, byte[] key, byte[] iv);

    [DllImport("AESLib.dll", CallingConvention = CallingConvention.Cdecl)]
    private static extern void LoadKeyFromFile(string filename, byte[] key, byte[] iv);

    [DllImport("AESLib.dll", CallingConvention = CallingConvention.Cdecl)]
    private static extern void AESEncrypt(byte[] key, byte[] iv, string plaintext,
                                          StringBuilder outHex, int outSize);

    [DllImport("AESLib.dll", CallingConvention = CallingConvention.Cdecl)]
    private static extern void AESDecrypt(byte[] key, byte[] iv, string hexCipher,
                                          StringBuilder outPlain, int outSize);

    // Public wrapper methods
    public static void GenerateAndSaveKey(string keyfile)
    {
        byte[] key = new byte[AES_KEY_SIZE];
        byte[] iv = new byte[AES_IV_SIZE];

        GenerateAESKey(key, iv);
        SaveKeyToFile(keyfile, key, iv);

        Console.WriteLine("Generated Key: " + BitConverter.ToString(key).Replace("-", ""));
        Console.WriteLine("Generated IV : " + BitConverter.ToString(iv).Replace("-", ""));
        Console.WriteLine($"Key and IV saved to {keyfile}");
    }

    public static string EncryptText(string keyfile, string plaintext)
    {
        byte[] key = new byte[AES_KEY_SIZE];
        byte[] iv = new byte[AES_IV_SIZE];

        LoadKeyFromFile(keyfile, key, iv);
        Console.WriteLine($"Loaded key from {keyfile}");

        StringBuilder outBuffer = new StringBuilder(MAX_BUFFER_SIZE);
        AESEncrypt(key, iv, plaintext, outBuffer, MAX_BUFFER_SIZE);

        return outBuffer.ToString();
    }

    public static string DecryptText(string keyfile, string cipherHex)
    {
        byte[] key = new byte[AES_KEY_SIZE];
        byte[] iv = new byte[AES_IV_SIZE];

        LoadKeyFromFile(keyfile, key, iv);

        StringBuilder outBuffer = new StringBuilder(MAX_BUFFER_SIZE);
        AESDecrypt(key, iv, cipherHex, outBuffer, MAX_BUFFER_SIZE);

        return outBuffer.ToString();
    }

    static void Main(string[] args)
    {
        try
        {
            // Example usage
            string keyfile = "aes_key.bin";
            GenerateAndSaveKey(keyfile);

            string plaintext = "Hello, AES encryption from C#!";
            string cipher = EncryptText(keyfile, plaintext);
            Console.WriteLine($"Encrypted: {cipher}");

            string decrypted = DecryptText(keyfile, cipher);
            Console.WriteLine($"Decrypted: {decrypted}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
    }
}