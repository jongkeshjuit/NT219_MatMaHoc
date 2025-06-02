import ctypes
import os
import sys
from ctypes import c_char_p, c_ubyte, POINTER, create_string_buffer

AES_KEY_LEN = 16
AES_BLOCK_SIZE = 16
MAX_BUFFER_SIZE = 1024

# Load DLL (adjust path as needed)
try:
    # Try to add dependency directories if needed
    if sys.platform == "win32":
        os.add_dll_directory("C:\\msys64\\mingw64\\bin")  # Adjust path if needed
    
    # Load the library with mode=3 to resolve dependencies immediately
    lib = ctypes.CDLL(r"D:\WorkSpace\NT219\zLab3\Task2\gcc\AESLib_gcc.dll", mode=3)
    print("DLL loaded successfully")
except Exception as e:
    print(f"Error loading DLL: {e}")
    sys.exit(1)
    
required_functions = ["GenerateAESKey", "SaveKeyToFile", "LoadKeyFromFile", "AESEncryptFile", "AESDecryptFile"]
for fname in required_functions:
    try:
        getattr(lib, fname)
        print(f"[ OK ] Found function: {fname}")
    except AttributeError:
        print(f"[FAIL] Function not found: {fname}")
        sys.exit(1)

# Define function prototypes
lib.GenerateAESKey.argtypes = [POINTER(c_ubyte), POINTER(c_ubyte)]
lib.GenerateAESKey.restype = None

lib.SaveKeyToFile.argtypes = [c_char_p, POINTER(c_ubyte), POINTER(c_ubyte)]
lib.SaveKeyToFile.restype = None

lib.LoadKeyFromFile.argtypes = [c_char_p, POINTER(c_ubyte), POINTER(c_ubyte)]
lib.LoadKeyFromFile.restype = None

lib.AESEncrypt.argtypes = [POINTER(c_ubyte), POINTER(c_ubyte), c_char_p, c_char_p, ctypes.c_int]
lib.AESEncrypt.restype = None

lib.AESDecrypt.argtypes = [POINTER(c_ubyte), POINTER(c_ubyte), c_char_p, c_char_p, ctypes.c_int]
lib.AESDecrypt.restype = None

def generate_key(key_file):
    """Generate and save a new AES key and IV"""
    key = (c_ubyte * AES_KEY_LEN)()
    iv = (c_ubyte * AES_BLOCK_SIZE)()
    
    lib.GenerateAESKey(key, iv)
    lib.SaveKeyToFile(key_file.encode(), key, iv)
    
    print(f"Key: {bytes(key).hex().upper()}")
    print(f"IV : {bytes(iv).hex().upper()}")
    print(f"Key and IV saved to {key_file}")

def encrypt_text(key_file, plaintext):
    """Encrypt text using the AES key and IV from file"""
    key = (c_ubyte * AES_KEY_LEN)()
    iv = (c_ubyte * AES_BLOCK_SIZE)()
    
    lib.LoadKeyFromFile(key_file.encode(), key, iv)
    print(f"Loaded key from {key_file}")
    
    out_buffer = create_string_buffer(MAX_BUFFER_SIZE)
    lib.AESEncrypt(key, iv, plaintext.encode(), out_buffer, MAX_BUFFER_SIZE)
    
    return out_buffer.value.decode()

def decrypt_text(key_file, cipher_hex):
    """Decrypt hex-encoded ciphertext using the AES key and IV from file"""
    key = (c_ubyte * AES_KEY_LEN)()
    iv = (c_ubyte * AES_BLOCK_SIZE)()
    
    lib.LoadKeyFromFile(key_file.encode(), key, iv)
    
    out_buffer = create_string_buffer(MAX_BUFFER_SIZE)
    lib.AESDecrypt(key, iv, cipher_hex.encode(), out_buffer, MAX_BUFFER_SIZE)
    
    return out_buffer.value.decode()

if __name__ == "__main__":
    # Example usage
    generate_key("aes_key.bin")
    cipher = encrypt_text("aes_key.bin", "Hello, AES encryption!")
    print(f"Encrypted: {cipher}")
    plaintext = decrypt_text("aes_key.bin", cipher)
    print(f"Decrypted: {plaintext}")