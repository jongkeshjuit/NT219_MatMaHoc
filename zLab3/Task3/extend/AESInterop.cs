using System;
using System.Runtime.InteropServices;
using System.Text;
using System.IO;

class AESInterop
{
    const int AES_KEY_SIZE = 16;
    const int AES_IV_SIZE = 16;
    const int MAX_BUFFER_SIZE = 8192;

    [DllImport("aes_dll.dll", CallingConvention = CallingConvention.Cdecl)]
    public static extern void GenerateAESKeyIV(byte[] key, byte[] iv);

    [DllImport("aes_dll.dll", CallingConvention = CallingConvention.Cdecl)]
    public static extern void SaveKeyToFile(string filename, byte[] key, byte[] iv);

    [DllImport("aes_dll.dll", CallingConvention = CallingConvention.Cdecl)]
    public static extern void LoadKeyFromFile(string filename, byte[] key, byte[] iv);

    [DllImport("aes_dll.dll", CallingConvention = CallingConvention.Cdecl)]
    public static extern void AESEncrypt(byte[] key, byte[] iv, string plaintext, StringBuilder outHex, int outSize);

    [DllImport("aes_dll.dll", CallingConvention = CallingConvention.Cdecl)]
    public static extern void AESDecrypt(byte[] key, byte[] iv, string hexCipher, StringBuilder outPlain, int outSize);

    static void PrintUsage()
    {
        Console.WriteLine("Usage:");
        Console.WriteLine("  AESInterop generate <keyfile>");
        Console.WriteLine("  AESInterop encrypt <keyfile> <plaintext> <outfile>");
        Console.WriteLine("  AESInterop decrypt <keyfile> <cipherfile> <outfile>");
    }

    static void Main(string[] args)
    {
        if (args.Length < 2)
        {
            PrintUsage();
            return;
        }

        string mode = args[0].ToLower();

        try
        {
            if (mode == "generate" && args.Length == 2)
            {
                string keyfile = args[1];
                byte[] key = new byte[AES_KEY_SIZE];
                byte[] iv = new byte[AES_IV_SIZE];

                GenerateAESKeyIV(key, iv);
                SaveKeyToFile(keyfile, key, iv);

                Console.WriteLine("[+] Generated Key: " + BitConverter.ToString(key).Replace("-", ""));
                Console.WriteLine("[+] Generated IV : " + BitConverter.ToString(iv).Replace("-", ""));
                Console.WriteLine("[+] Saved key to: " + keyfile);
            }
            else if (mode == "encrypt" && args.Length == 4)
            {
                string keyfile = args[1];
                string plaintext = args[2];
                string outfile = args[3];

                byte[] key = new byte[AES_KEY_SIZE];
                byte[] iv = new byte[AES_IV_SIZE];
                LoadKeyFromFile(keyfile, key, iv);

                StringBuilder outHex = new StringBuilder(MAX_BUFFER_SIZE);
                AESEncrypt(key, iv, plaintext, outHex, MAX_BUFFER_SIZE);

                File.WriteAllText(outfile, outHex.ToString());
                Console.WriteLine("[+] Encrypted to: " + outfile);
            }
            else if (mode == "decrypt" && args.Length == 4)
            {
                string keyfile = args[1];
                string cipherfile = args[2];
                string outfile = args[3];

                byte[] key = new byte[AES_KEY_SIZE];
                byte[] iv = new byte[AES_IV_SIZE];
                LoadKeyFromFile(keyfile, key, iv);

                string hexCipher = File.ReadAllText(cipherfile);
                StringBuilder outPlain = new StringBuilder(MAX_BUFFER_SIZE);
                AESDecrypt(key, iv, hexCipher, outPlain, MAX_BUFFER_SIZE);

                File.WriteAllText(outfile, outPlain.ToString());
                Console.WriteLine("[+] Decrypted to: " + outfile);
            }
            else
            {
                PrintUsage();
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[!] Error: {ex.Message}");
        }
    }
}