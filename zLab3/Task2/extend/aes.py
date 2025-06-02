import ctypes
import os
import sys
import argparse
from pathlib import Path

# Constants for AES
AES_KEY_LENGTH = 16
AES_BLOCK_SIZE = 16

def find_dll():
    """Find the AES crypto DLL in common locations"""
    search_paths = [
        ".",  # Current directory 
        Path(__file__).parent,  # Script directory
        "D:/WorkSpace/code"  # Project directory
    ]
    
    dll_names = ["aes_crypto_lib.dll", "libaes_crypto_lib.so"]
    
    for path in search_paths:
        for name in dll_names:
            full_path = Path(path) / name
            if full_path.exists():
                return str(full_path)
                
    raise FileNotFoundError("Could not find AES crypto library")

def load_library():
    """Load the AES crypto library and define function signatures"""
    try:
        # Add DLL search paths for dependencies if needed
        if sys.platform == "win32":
            os.add_dll_directory("C:/msys64/mingw64/bin")
            
        dll_path = find_dll()
        lib = ctypes.CDLL(dll_path, mode=3)  # mode=3 enables immediate resolution of dependencies
        
        # Define function prototypes
        lib.GenerateAESKey.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.POINTER(ctypes.c_ubyte)
        ]
        
        lib.SaveKeyToFile.argtypes = [
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.POINTER(ctypes.c_ubyte)
        ]
        
        lib.LoadKeyFromFile.argtypes = [
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.POINTER(ctypes.c_ubyte)
        ]
        
        lib.AESEncryptFile.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.POINTER(ctypes.c_ubyte)
        ]
        
        lib.AESDecryptFile.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.POINTER(ctypes.c_ubyte)
        ]
        
        # Verify all required functions exist
        required_functions = [
            "GenerateAESKey", 
            "SaveKeyToFile", 
            "LoadKeyFromFile", 
            "AESEncryptFile", 
            "AESDecryptFile"
        ]
        
        for fname in required_functions:
            try:
                getattr(lib, fname)
                print(f"[ OK ] Found function: {fname}")
            except AttributeError:
                print(f"[FAIL] Function not found: {fname}")
                sys.exit(1)
                
        return lib
        
    except Exception as e:
        print(f"Error loading AES library: {e}")
        sys.exit(1)

# Load the library
lib = load_library()

def generate_key(keyfile):
    """Generate a new AES key/IV pair and save to file"""
    key = (ctypes.c_ubyte * AES_KEY_LENGTH)()
    iv = (ctypes.c_ubyte * AES_BLOCK_SIZE)()
    
    lib.GenerateAESKey(key, iv)
    lib.SaveKeyToFile(keyfile.encode(), key, iv)
    
    print(f"Generated and saved new AES key/IV to: {keyfile}")
    print(f"Key: {bytes(key).hex().upper()}")
    print(f"IV : {bytes(iv).hex().upper()}")

def load_key(keyfile):
    """Load and display an AES key/IV pair from file"""
    key = (ctypes.c_ubyte * AES_KEY_LENGTH)()
    iv = (ctypes.c_ubyte * AES_BLOCK_SIZE)()
    
    lib.LoadKeyFromFile(keyfile.encode(), key, iv)
    
    print(f"Loaded AES key/IV from: {keyfile}")
    print(f"Key: {bytes(key).hex().upper()}")
    print(f"IV : {bytes(iv).hex().upper()}")
    
    return key, iv

def encrypt_file(keyfile, infile, outfile):
    """Encrypt a file using AES"""
    key, iv = load_key(keyfile)
    
    lib.AESEncryptFile(
        infile.encode(),
        outfile.encode(),
        key,
        iv
    )
    
    print(f"Encrypted {infile} to {outfile}")

def decrypt_file(keyfile, infile, outfile):
    """Decrypt a file using AES"""
    key, iv = load_key(keyfile)
    
    lib.AESDecryptFile(
        infile.encode(),
        outfile.encode(),
        key,
        iv
    )
    
    print(f"Decrypted {infile} to {outfile}")

def main():
    parser = argparse.ArgumentParser(description="AES Encryption/Decryption Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate key command
    parser_generate = subparsers.add_parser("generate", help="Generate new AES key/IV pair")
    parser_generate.add_argument("keyfile", help="Key file to save")
    
    # Load key command
    parser_load = subparsers.add_parser("load", help="Load and display AES key/IV")
    parser_load.add_argument("keyfile", help="Key file to load")
    
    # Encrypt command
    parser_encrypt = subparsers.add_parser("encrypt", help="Encrypt a file")
    parser_encrypt.add_argument("keyfile", help="Key file to use")
    parser_encrypt.add_argument("infile", help="Input file to encrypt")
    parser_encrypt.add_argument("outfile", help="Output file for encrypted data")
    
    # Decrypt command
    parser_decrypt = subparsers.add_parser("decrypt", help="Decrypt a file")
    parser_decrypt.add_argument("keyfile", help="Key file to use")
    parser_decrypt.add_argument("infile", help="Input file to decrypt")
    parser_decrypt.add_argument("outfile", help="Output file for decrypted data")
    
    args = parser.parse_args()
    
    if args.command == "generate":
        generate_key(args.keyfile)
    elif args.command == "load":
        load_key(args.keyfile)
    elif args.command == "encrypt":
        encrypt_file(args.keyfile, args.infile, args.outfile)
    elif args.command == "decrypt":
        decrypt_file(args.keyfile, args.infile, args.outfile)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()