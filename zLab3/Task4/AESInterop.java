import java.nio.charset.StandardCharsets;

public class AESInterop {
    private static final int AES_KEY_SIZE = 16;
    private static final int AES_IV_SIZE = 16;
    private static final int MAX_BUFFER_SIZE = 1024;

    // Load thư viện native
    static {
        try {
            System.loadLibrary("AESInteropLib"); // Sẽ tìm AESLib.dll trên Windows hoặc libAESLib.so trên Linux
            System.out.println("DLL loaded successfully");
        } catch (UnsatisfiedLinkError e) {
            System.err.println("Error loading DLL: " + e.getMessage());
            System.exit(1);
        }
    }

    // Khai báo các native methods
    public native void GenerateAESKey(byte[] key, byte[] iv);
    public native void SaveKeyToFile(String filename, byte[] key, byte[] iv);
    public native void LoadKeyFromFile(String filename, byte[] key, byte[] iv);
    public native void AESEncrypt(byte[] key, byte[] iv, String plaintext, 
                                  byte[] outHex, int outSize);
    public native void AESDecrypt(byte[] key, byte[] iv, String hexCipher, 
                                  byte[] outPlain, int outSize);

    // Phương thức wrapper để generate và save key
    public void generateKey(String keyFile) {
        byte[] key = new byte[AES_KEY_SIZE];
        byte[] iv = new byte[AES_IV_SIZE];
        
        GenerateAESKey(key, iv);
        SaveKeyToFile(keyFile, key, iv);
        
        System.out.println("Key: " + bytesToHex(key));
        System.out.println("IV : " + bytesToHex(iv));
        System.out.println("Key and IV saved to " + keyFile);
    }

    // Phương thức encrypt text
    public String encryptText(String keyFile, String plaintext) {
        byte[] key = new byte[AES_KEY_SIZE];
        byte[] iv = new byte[AES_IV_SIZE];
        
        LoadKeyFromFile(keyFile, key, iv);
        System.out.println("Loaded key from " + keyFile);
        
        byte[] outBuffer = new byte[MAX_BUFFER_SIZE];
        AESEncrypt(key, iv, plaintext, outBuffer, MAX_BUFFER_SIZE);
        
        // Chuyển byte array thành string, bỏ các byte null ở cuối
        String result = new String(outBuffer, StandardCharsets.UTF_8);
        return result.trim().replaceAll("\0", "");
    }

    // Phương thức decrypt text
    public String decryptText(String keyFile, String cipherHex) {
        byte[] key = new byte[AES_KEY_SIZE];
        byte[] iv = new byte[AES_IV_SIZE];
        
        LoadKeyFromFile(keyFile, key, iv);
        
        byte[] outBuffer = new byte[MAX_BUFFER_SIZE];
        AESDecrypt(key, iv, cipherHex, outBuffer, MAX_BUFFER_SIZE);
        
        // Chuyển byte array thành string, bỏ các byte null ở cuối
        String result = new String(outBuffer, StandardCharsets.UTF_8);
        return result.trim().replaceAll("\0", "");
    }

    // Utility method để chuyển byte array thành hex string
    private String bytesToHex(byte[] bytes) {
        StringBuilder result = new StringBuilder();
        for (byte b : bytes) {
            result.append(String.format("%02X", b));
        }
        return result.toString();
    }

    public static void main(String[] args) {
        try {
            AESInterop aes = new AESInterop();
            
            // Example usage
            String keyFile = "aes_key.bin";
            aes.generateKey(keyFile);
            
            String plaintext = "Hello, AES encryption from Java!";
            String cipher = aes.encryptText(keyFile, plaintext);
            System.out.println("Encrypted: " + cipher);
            
            String decrypted = aes.decryptText(keyFile, cipher);
            System.out.println("Decrypted: " + decrypted);
            
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}