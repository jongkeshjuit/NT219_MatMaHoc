# NT219_MatMaHoc

## GUI 
#### Hiện tại khuyến khích python complex/ simple + winform simple, complex có bugs chưa fix được =))

## Setup nhanh
- Download từ: https://www.mingw-w64.org/
- Hoặc dùng MSYS2: <br>
 [] pacman -S mingw-w64-x86_64-gcc </br>
 [] winget install Python.Python.3.11 <br>


### Tạo winforms trên vsCode, chỉ cần chạy file exe trong bin
- Create Project
### Visual Studio 2019/2022
File → New → Project → Windows Forms App (.NET Framework) <br>
Project name: CryptoCompilerGUI

### Hoặc dùng .NET CLI
dotnet new winforms -n CryptoCompilerGUI <br>
cd CryptoCompilerGUI <br>
Install-Package System.Text.Json <br>
### Visual Studio: F5 hoặc Ctrl+F5 <br>
### CLI:
dotnet build (Không dùng cũng được) <br>
dotnet run
# Tóm tắt:
- python: <br> python3 ...py <br> 
- winforms:<br> dotnet new winforms --> paste code Form1.cs or Program.cs --> dotnet run

# Tổng hợp câu lệnh build từ Command Prompt

## Biến thay thế cần điền:
- `<file>`: Đường dẫn đầy đủ đến file source code (VD: "D:/WorkSpace/DES-CBC.cpp")
- `<fileDirname>`: Thư mục chứa file source (VD: "D:/WorkSpace")
- `<fileBasenameNoExtension>`: Tên file không có extension (VD: DES-CBC)
- `<workspaceFolder>`: Thư mục workspace/project root (VD: "D:/cryptopp-master")

---

## 1. CryptoPP Build Tasks

### 1.1. Build Executable với GCC (CryptoPP)
```bash
"C:\msys64\mingw64\bin\g++.exe" -g2 -O3 -DNDEBUG "<file>" -o "<fileDirname>\gcc\<fileBasenameNoExtension>.exe" -D_WIN32_WINNT=0x0501 -lpthread -L"<workspaceFolder>\lib\cryptopp\gcc" -lcryptopp -I"<workspaceFolder>\include\cryptopp" -Wall -std=c++17 && cd "<fileDirname>\gcc"
```

### 1.2. Build Executable với Clang (CryptoPP)
```bash
"C:\msys64\mingw64\bin\clang++.exe" -g2 -O3 -DNDEBUG "<file>" -o "<fileDirname>\clang\<fileBasenameNoExtension>.exe" -D_WIN32_WINNT=0x0501 -lpthread -L"<workspaceFolder>\lib\cryptopp\clang" -lcryptopp -I"<workspaceFolder>\include\cryptopp" -Wall && cd "<fileDirname>\clang" && "<fileBasenameNoExtension>.exe"
```

### 1.3. Build Executable với MSVC (CryptoPP)
```bash
cl.exe /MTd /GS /O2 /W4 /Zi /nologo /EHsc /I"<workspaceFolder>\include\cryptopp" /Fo"<fileDirname>\msvc\" /Fd"<fileDirname>\msvc\vc140.pdb" "<file>" /link /OUT:"<fileDirname>\msvc\<fileBasenameNoExtension>.exe" /LIBPATH:"<workspaceFolder>\lib\cryptopp\msvc" cryptlib.lib crypt32.lib ws2_32.lib /MACHINE:X64 && cd "<fileDirname>\msvc" && "<fileBasenameNoExtension>.exe"
```

### 1.4. Build Shared Library với GCC (CryptoPP)
```bash
"C:\msys64\mingw64\bin\g++.exe" -shared -g2 -O3 -DNDEBUG "<file>" -o "<fileDirname>\gcc\<fileBasenameNoExtension>.dll" -D_WIN32_WINNT=0x0501 -lpthread -L"<workspaceFolder>\lib\cryptopp\gcc" -lcryptopp -I"<workspaceFolder>\include\cryptopp" -Wall
```

### 1.5. Build Shared Library với Clang (CryptoPP)
```bash
"C:\msys64\mingw64\bin\clang++.exe" -shared -g2 -O3 -DNDEBUG "<file>" -o "<fileDirname>\clang\<fileBasenameNoExtension>.dll" -D_WIN32_WINNT=0x0501 -lpthread -L"<workspaceFolder>\lib\cryptopp\clang" -lcryptopp -I"<workspaceFolder>\include\cryptopp" -Wall
```

### 1.6. Build Shared Library với MSVC (CryptoPP)
```bash
cl.exe /MTd /GS /O2 /W4 /Zi /nologo /EHsc /I"<workspaceFolder>\include\cryptopp" /Fo"<fileDirname>\msvc\" /Fd"<fileDirname>\msvc\vc140.pdb" "<file>" /link /DLL /OUT:"<fileDirname>\msvc\<fileBasenameNoExtension>.dll" /PDB:"<fileDirname>\msvc\<fileBasenameNoExtension>.pdb" /LIBPATH:"<workspaceFolder>\lib\cryptopp\msvc" cryptlib.lib crypt32.lib ws2_32.lib /MACHINE:X64
```

---

## 2. OpenSSL Build Tasks

### 2.1. Build Executable với GCC (OpenSSL)
```bash
"C:\msys64\mingw64\bin\g++.exe" -g2 -O3 -DNDEBUG "<file>" -o "<fileDirname>\gcc\<fileBasenameNoExtension>_openssl.exe" -D_WIN32_WINNT=0x0501 -lpthread -L"<workspaceFolder>\openssl350\gcc\lib64" -lssl -lcrypto -lcrypt32 -lws2_32 -lpthread -I"<workspaceFolder>\openssl350\gcc\include" -Wall && cd "<fileDirname>\gcc" && "<fileBasenameNoExtension>_openssl.exe"
```

### 2.2. Build Executable với Clang (OpenSSL)
```bash
"C:\msys64\mingw64\bin\clang++.exe" -g2 -O3 -DNDEBUG "<file>" -o "<fileDirname>\clang\<fileBasenameNoExtension>_openssl.exe" -D_WIN32_WINNT=0x0501 -lpthread -L"<workspaceFolder>\openssl350\clang\lib64" -lssl -lcrypto -lcrypt32 -lws2_32 -lpthread -I"<workspaceFolder>\openssl350\clang\include" -Wall && cd "<fileDirname>\clang" && "<fileBasenameNoExtension>_openssl.exe"
```

### 2.3. Build Executable với MSVC (OpenSSL)
```bash
cl.exe /MTd /GS /O2 /W4 /Zi /nologo /EHsc /I"<workspaceFolder>\openssl350\msvc\include" /Fo"<fileDirname>\msvc\" /Fd"<fileDirname>\msvc\vc140.pdb" "<file>" /link /OUT:"<fileDirname>\msvc\<fileBasenameNoExtension>_openssl.exe" /LIBPATH:"<workspaceFolder>\openssl350\msvc\lib" libssl.lib libcrypto.lib crypt32.lib ws2_32.lib /MACHINE:X64 && cd "<fileDirname>\msvc" && "<fileBasenameNoExtension>_openssl.exe"
```

### 2.4. Build Shared Library với GCC (OpenSSL)
```bash
"C:\msys64\mingw64\bin\g++.exe" -shared -g2 -O3 -DNDEBUG "<file>" -o "<fileDirname>\gcc\<fileBasenameNoExtension>_openssl.dll" -D_WIN32_WINNT=0x0501 -lpthread -L"<workspaceFolder>\openssl350\gcc\lib64" -lssl -lcrypto -lcrypt32 -lws2_32 -lpthread -I"<workspaceFolder>\openssl350\gcc\include" -Wall
```

### 2.5. Build Shared Library với Clang (OpenSSL)
```bash
"C:\msys64\mingw64\bin\clang++.exe" -shared -g2 -O3 -DNDEBUG "<file>" -o "<fileDirname>\clang\<fileBasenameNoExtension>_openssl.dll" -D_WIN32_WINNT=0x0501 -lpthread -L"<workspaceFolder>\openssl350\clang\lib64" -lssl -lcrypto -lcrypt32 -lws2_32 -lpthread -I"<workspaceFolder>\openssl350\clang\include" -Wall
```

### 2.6. Build Shared Library với MSVC (OpenSSL)
```bash
cl.exe /MTd /GS /O2 /W4 /Zi /nologo /EHsc /I"<workspaceFolder>\openssl350\msvc\include" /Fo"<fileDirname>\msvc\" /Fd"<fileDirname>\msvc\vc140.pdb" "<file>" /link /DLL /OUT:"<fileDirname>\msvc\<fileBasenameNoExtension>_openssl.dll" /PDB:"<fileDirname>\msvc\<fileBasenameNoExtension>_openssl.pdb" /LIBPATH:"<workspaceFolder>\openssl350\msvc\lib" libssl.lib libcrypto.lib crypt32.lib ws2_32.lib /MACHINE:X64
```

---

## 3. Build với cả CryptoPP và OpenSSL

### 3.1. Build Executable với GCC (CryptoPP + OpenSSL)
```bash
"C:\msys64\mingw64\bin\g++.exe" -g2 -O3 -DNDEBUG "<file>" -o "<fileDirname>\gcc\<fileBasenameNoExtension>_combined.exe" -D_WIN32_WINNT=0x0501 -lpthread -Wall -std=c++17 -I"<workspaceFolder>\include\cryptopp" -L"<workspaceFolder>\lib\cryptopp\gcc" -lcryptopp -I"<workspaceFolder>\openssl350\gcc\include" -L"<workspaceFolder>\openssl350\gcc\lib64" -lssl -lcrypto -lcrypt32 -lws2_32 && cd "<fileDirname>\gcc" && "<fileBasenameNoExtension>_combined.exe"
```

### 3.2. Build Executable với Clang (CryptoPP + OpenSSL)
```bash
"C:\msys64\mingw64\bin\clang++.exe" -g2 -O3 -DNDEBUG "<file>" -o "<fileDirname>\clang\<fileBasenameNoExtension>_combined.exe" -D_WIN32_WINNT=0x0501 -lpthread -Wall -I"<workspaceFolder>\include\cryptopp" -L"<workspaceFolder>\lib\cryptopp\clang" -lcryptopp -I"<workspaceFolder>\openssl350\clang\include" -L"<workspaceFolder>\openssl350\clang\lib64" -lssl -lcrypto -lcrypt32 -lws2_32 && cd "<fileDirname>\clang" && "<fileBasenameNoExtension>_combined.exe"
```

### 3.3. Build Executable với MSVC (CryptoPP + OpenSSL)
```bash
cl.exe /MTd /GS /O2 /W4 /Zi /nologo /EHsc /I"<workspaceFolder>\include\cryptopp" /I"<workspaceFolder>\openssl350\msvc\include" /Fo"<fileDirname>\msvc\" /Fd"<fileDirname>\msvc\vc140.pdb" "<file>" /link /OUT:"<fileDirname>\msvc\<fileBasenameNoExtension>_combined.exe" /LIBPATH:"<workspaceFolder>\lib\cryptopp\msvc" /LIBPATH:"<workspaceFolder>\openssl350\msvc\lib" cryptlib.lib libssl.lib libcrypto.lib crypt32.lib ws2_32.lib /MACHINE:X64 && cd "<fileDirname>\msvc" && "<fileBasenameNoExtension>_combined.exe"
```

### 3.4. Build Shared Library với GCC (CryptoPP + OpenSSL)
```bash
"C:\msys64\mingw64\bin\g++.exe" -shared -g2 -O3 -DNDEBUG "<file>" -o "<fileDirname>\gcc\<fileBasenameNoExtension>_combined.dll" -D_WIN32_WINNT=0x0501 -lpthread -Wall -I"<workspaceFolder>\include\cryptopp" -L"<workspaceFolder>\lib\cryptopp\gcc" -lcryptopp -I"<workspaceFolder>\openssl350\gcc\include" -L"<workspaceFolder>\openssl350\gcc\lib64" -lssl -lcrypto -lcrypt32 -lws2_32
```

### 3.5. Build Shared Library với Clang (CryptoPP + OpenSSL)
```bash
"C:\msys64\mingw64\bin\clang++.exe" -shared -g2 -O3 -DNDEBUG "<file>" -o "<fileDirname>\clang\<fileBasenameNoExtension>_combined.dll" -D_WIN32_WINNT=0x0501 -lpthread -Wall -I"<workspaceFolder>\include\cryptopp" -L"<workspaceFolder>\lib\cryptopp\clang" -lcryptopp -I"<workspaceFolder>\openssl350\clang\include" -L"<workspaceFolder>\openssl350\clang\lib64" -lssl -lcrypto -lcrypt32 -lws2_32
```

### 3.6. Build Shared Library với MSVC (CryptoPP + OpenSSL)
```bash
cl.exe /MTd /GS /O2 /W4 /Zi /nologo /EHsc /I"<workspaceFolder>\include\cryptopp" /I"<workspaceFolder>\openssl350\msvc\include" /Fo"<fileDirname>\msvc\" /Fd"<fileDirname>\msvc\vc140.pdb" "<file>" /link /DLL /OUT:"<fileDirname>\msvc\<fileBasenameNoExtension>_combined.dll" /PDB:"<fileDirname>\msvc\<fileBasenameNoExtension>_combined.pdb" /LIBPATH:"<workspaceFolder>\lib\cryptopp\msvc" /LIBPATH:"<workspaceFolder>\openssl350\msvc\lib" cryptlib.lib libssl.lib libcrypto.lib crypt32.lib ws2_32.lib /MACHINE:X64
```

---

## 4. C# Build Tasks

### 4.1. Build với CSC (C# Compiler)
```bash
csc.exe /nologo /debug /optimize+ /warn:4 "<file>" /out:"<fileDirname>\<fileBasenameNoExtension>_cs.exe"
```

**Ví dụ thực tế:**
```bash
csc.exe /nologo /debug /optimize+ /warn:4 "D:/WorkSpace/NT219/zLab1/Program.cs" /out:"D:\WorkSpace\NT219\zLab1\Program_cs.exe"
```

---

## 5. Java Build Tasks

### 5.1. Compile Java
```bash
javac "<file>"
```

### 5.2. Run Java
```bash
java "<fileBasenameNoExtension>"
```

**Ví dụ thực tế:**
```bash
javac "D:/WorkSpace/NT219/zLab1/HelloWorld.java"
java "HelloWorld"
```

---

## 6. JNI (Java Native Interface) Build Tasks

### 6.1. Step 1: Compile Java file
```bash
javac "<fileBasenameNoExtension>.java"
```

### 6.2. Step 2: Generate JNI header
```bash
javac -h . "<fileBasenameNoExtension>.java"
```

### 6.3. Step 3: Compile C++ to DLL
```bash
"C:\msys64\mingw64\bin\g++.exe" -I"<JDK_PATH>\include" -I"<JDK_PATH>\include\win32" -I"<CRYPTOPP_PATH>\include\cryptopp" -shared -o "<fileBasenameNoExtension>Lib.dll" "<fileBasenameNoExtension>JNI.cpp" -L"<CRYPTOPP_PATH>\lib\cryptopp\gcc" -lcryptopp
```

### 6.4. Step 4: Run Java with native library
```bash
java --enable-native-access=ALL-UNNAMED -Djava.library.path=. "<fileBasenameNoExtension>"
```

**Ví dụ thực tế JNI:**
```bash
javac "CryptoJNI.java"
javac -h . "CryptoJNI.java"
"C:\msys64\mingw64\bin\g++.exe" -I"E:\jdk-11.0.27\include" -I"E:\jdk-11.0.27\include\win32" -I"D:\cryptopp-master\include\cryptopp" -shared -o "CryptoJNILib.dll" "CryptoJNIJNI.cpp" -L"D:\cryptopp-master\lib\cryptopp\gcc" -lcryptopp
java --enable-native-access=ALL-UNNAMED -Djava.library.path=. "CryptoJNI"
```

---

## 7. Lưu ý quan trọng

### 7.1. Tạo thư mục trước khi build:
```bash
mkdir "<fileDirname>\gcc"
mkdir "<fileDirname>\clang"
mkdir "<fileDirname>\msvc"
```

### 7.2. Đường dẫn phổ biến cần thay thế:
- **CryptoPP path**: `D:/cryptopp-master`
- **OpenSSL path**: `D:/Labs_Crypto/openssl350`
- **MSYS2 GCC**: `C:\msys64\mingw64\bin\g++.exe`
- **MSYS2 Clang**: `C:\msys64\mingw64\bin\clang++.exe`
- **JDK path**: `E:\jdk-11.0.27`

### 7.3. Compiler flags giải thích:
**GCC/Clang:**
- `-g2`: Debug information level 2
- `-O3`: Highest optimization level
- `-DNDEBUG`: Define NDEBUG macro (disable assertions)
- `-Wall`: Enable all warnings
- `-std=c++17`: Use C++17 standard
- `-shared`: Create shared library (.dll)
- `-lpthread`: Link pthread library

**MSVC:**
- `/MTd`: Multi-threaded debug runtime
- `/GS`: Buffer security check
- `/O2`: Optimize for speed
- `/W4`: Warning level 4
- `/Zi`: Generate debug info
- `/nologo`: Suppress startup banner
- `/EHsc`: Exception handling model
- `/DLL`: Create dynamic link library
- `/MACHINE:X64`: Target x64 architecture

### 7.4. Thứ tự linking libraries:
1. `-lcryptopp` / `cryptlib.lib` (CryptoPP)
2. `-lssl -lcrypto` / `libssl.lib libcrypto.lib` (OpenSSL)
3. `-lcrypt32 -lws2_32` / `crypt32.lib ws2_32.lib` (Windows system)
4. `-lpthread` (Threading support for GCC/Clang)

---

## 8. Quick Templates

### 8.1. Simple C++ (GCC)
```bash
"C:\msys64\mingw64\bin\g++.exe" -g2 -O3 -Wall -std=c++17 "<SOURCE_FILE>" -o "<OUTPUT_FILE>.exe"
```

### 8.2. C++ với CryptoPP (GCC)
```bash
"C:\msys64\mingw64\bin\g++.exe" -g2 -O3 -DNDEBUG -Wall -std=c++17 "<SOURCE_FILE>" -o "<OUTPUT_FILE>.exe" -I"<CRYPTOPP_PATH>\include\cryptopp" -L"<CRYPTOPP_PATH>\lib\cryptopp\gcc" -lcryptopp -D_WIN32_WINNT=0x0501 -lpthread
```

### 8.3. C++ với OpenSSL (GCC)
```bash
"C:\msys64\mingw64\bin\g++.exe" -g2 -O3 -DNDEBUG -Wall "<SOURCE_FILE>" -o "<OUTPUT_FILE>.exe" -I"<OPENSSL_PATH>\include" -L"<OPENSSL_PATH>\lib64" -lssl -lcrypto -lcrypt32 -lws2_32 -D_WIN32_WINNT=0x0501 -lpthread
```

### 8.4. C++ với cả CryptoPP và OpenSSL (GCC)
```bash
"C:\msys64\mingw64\bin\g++.exe" -g2 -O3 -DNDEBUG -Wall -std=c++17 "<SOURCE_FILE>" -o "<OUTPUT_FILE>.exe" -I"<CRYPTOPP_PATH>\include\cryptopp" -L"<CRYPTOPP_PATH>\lib\cryptopp\gcc" -lcryptopp -I"<OPENSSL_PATH>\include" -L"<OPENSSL_PATH>\lib64" -lssl -lcrypto -lcrypt32 -lws2_32 -D_WIN32_WINNT=0x0501 -lpthread
```