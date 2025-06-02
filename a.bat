@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
:: ------------------------------
:: CẤU HÌNH VÀ THIẾT LẬP
:: ------------------------------

:: Xử lý đường dẫn
set "SCRIPT_PATH=%~dp0"
set "SCRIPT_PATH=%SCRIPT_PATH:~0,-1%"
set "CURRENT_PATH=%cd%"

echo Debug: SCRIPT_PATH=%SCRIPT_PATH%
echo Debug: CURRENT_PATH=%CURRENT_PATH%

:: Cấu hình đường dẫn thư viện
set "CRYPTOPP_ROOT=%SCRIPT_PATH%"
set "CRYPTOPP_INCLUDE=%CRYPTOPP_ROOT%\include\cryptopp"
set "CRYPTOPP_LIB_GCC=%CRYPTOPP_ROOT%\lib\cryptopp\gcc"
set "CRYPTOPP_LIB_CLANG=%CRYPTOPP_ROOT%\lib\cryptopp\clang"
set "CRYPTOPP_LIB_MSVC=%CRYPTOPP_ROOT%\lib\cryptopp\msvc"

:: Đường dẫn trình biên dịch
set "GCC=g++.exe"
set "CLANG=clang++.exe"
set "MSVC=cl.exe"
set "CSC=csc.exe"
set "JAVAC=javac.exe"
set "JAVA=java.exe"

:: Cấu hình số luồng cho biên dịch song song
set "MAX_THREADS=4"

:: Flags và options phổ biến
set "GCC_FLAGS=-g2 -O3 -DNDEBUG -D_WIN32_WINNT=0x0501 -Wall"
set "CLANG_FLAGS=-g2 -O3 -DNDEBUG -D_WIN32_WINNT=0x0501 -Wall"
set "MSVC_FLAGS=/MTd /GS /O2 /W4 /Zi /nologo /EHsc"
set "COMMON_LIBS=-lpthread -lcryptopp"
set "MSVC_LIBS=cryptlib.lib crypt32.lib ws2_32.lib"

:: Thiết lập JNI
if "%JAVA_HOME%"=="" (
    set "JAVA_HOME=C:\Program Files\Java\jdk-21"
)
set "JNI_INCLUDE=-I^"%JAVA_HOME%\include^" -I^"%JAVA_HOME%\include\win32^""

:: ===== CHƯƠNG TRÌNH CHÍNH =====
if "%1"=="" goto :help
if "%1"=="help" goto :help
if "%1"=="clean" goto :clean_all
if "%1"=="debug" goto :debug_file
if "%1"=="parallel" goto :parallel_build
if "%1"=="project" goto :build_project
if "%1"=="jni-build" goto :jni_build
if "%1"=="check" goto :check_env

:: Phân tích tham số
set "CMD=%1"
set "FILE_PATH=%2"
set "EXTRA_ARGS="
if not "%3"=="" set "EXTRA_ARGS=%3 %4 %5 %6 %7 %8 %9"

echo Debug: CMD=%CMD%
echo Debug: FILE_PATH=%FILE_PATH%

:: Kiểm tra đường dẫn file
if "%FILE_PATH%"=="" (
    echo Lỗi: Thiếu đường dẫn file. Sử dụng: %0 [command] [file_path]
    exit /b 1
)

:: Xử lý đường dẫn tương đối
if not exist "%FILE_PATH%" (
    if exist "%CURRENT_PATH%\%FILE_PATH%" (
        set "FILE_PATH=%CURRENT_PATH%\%FILE_PATH%"
        echo Debug: File found at %FILE_PATH%
    ) else (
        echo Lỗi: Không tìm thấy file '%FILE_PATH%'
        echo Debug: Tried %FILE_PATH% and %CURRENT_PATH%\%FILE_PATH%
        echo Kiểm tra lại đường dẫn file và thử lại
        exit /b 1
    )
)

:: Lấy thông tin file
for %%F in ("%FILE_PATH%") do (
    set "FILE_DIR=%%~dpF"
    set "FILE_NAME=%%~nF"
    set "FILE_EXT=%%~xF"
    set "FULL_PATH=%%~fF"
)

echo Debug: FILE_DIR=%FILE_DIR%
echo Debug: FILE_NAME=%FILE_NAME%
echo Debug: FILE_EXT=%FILE_EXT%
echo Debug: FULL_PATH=%FULL_PATH%

:: Tạo thư mục output nếu cần
set "OUTPUT_DIR=%FILE_DIR%%CMD%"
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

:: Xử lý dựa trên lệnh
call :%CMD%
if errorlevel 1 (
    echo Lỗi không xác định khi thực thi lệnh %CMD%
    exit /b 1
)
goto :eof

:: ===== LỆNH BIÊN DỊCH =====

:gcc
echo Biên dịch với GCC: %FILE_PATH%
%GCC% %GCC_FLAGS% -I"%CRYPTOPP_INCLUDE%" "%FULL_PATH%" -o "%OUTPUT_DIR%\%FILE_NAME%_gcc.exe" -L"%CRYPTOPP_LIB_GCC%" %COMMON_LIBS% %EXTRA_ARGS%
if errorlevel 1 (
    echo Lỗi khi biên dịch với GCC
    exit /b 1
)
echo Hoàn tất: %OUTPUT_DIR%\%FILE_NAME%_gcc.exe
goto :eof

:gcc-dll
echo Biên dịch DLL với GCC: %FILE_PATH%
%GCC% -shared %GCC_FLAGS% -I"%CRYPTOPP_INCLUDE%" "%FULL_PATH%" -o "%OUTPUT_DIR%\%FILE_NAME%_gcc.dll" -L"%CRYPTOPP_LIB_GCC%" %COMMON_LIBS% %EXTRA_ARGS%
if errorlevel 1 (
    echo Lỗi khi biên dịch DLL với GCC
    exit /b 1
)
echo Hoàn tất: %OUTPUT_DIR%\%FILE_NAME%_gcc.dll
goto :eof

:gcc-obj
echo Tạo object file với GCC: %FILE_PATH%
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
%GCC% -c %GCC_FLAGS% -I"%CRYPTOPP_INCLUDE%" "%FULL_PATH%" -o "%OUTPUT_DIR%\%FILE_NAME%.o" %EXTRA_ARGS%
if errorlevel 1 (
    echo Lỗi khi tạo object file với GCC
    exit /b 1
)
echo Hoàn tất: %OUTPUT_DIR%\%FILE_NAME%.o
goto :eof

:clang
echo Biên dịch với Clang: %FILE_PATH%
%CLANG% %CLANG_FLAGS% -I"%CRYPTOPP_INCLUDE%" "%FULL_PATH%" -o "%OUTPUT_DIR%\%FILE_NAME%_clang.exe" -L"%CRYPTOPP_LIB_CLANG%" %COMMON_LIBS% %EXTRA_ARGS%
if errorlevel 1 (
    echo Lỗi khi biên dịch với Clang
    exit /b 1
)
echo Hoàn tất: %OUTPUT_DIR%\%FILE_NAME%_clang.exe
goto :eof

:clang-dll
echo Biên dịch DLL với Clang: %FILE_PATH%
%CLANG% -shared %CLANG_FLAGS% -I"%CRYPTOPP_INCLUDE%" "%FULL_PATH%" -o "%OUTPUT_DIR%\%FILE_NAME%_clang.dll" -L"%CRYPTOPP_LIB_CLANG%" %COMMON_LIBS% %EXTRA_ARGS%
if errorlevel 1 (
    echo Lỗi khi biên dịch DLL với Clang
    exit /b 1
)
echo Hoàn tất: %OUTPUT_DIR%\%FILE_NAME%_clang.dll
goto :eof

:msvc
echo Biên dịch với MSVC: %FILE_PATH%
%MSVC% %MSVC_FLAGS% /I"%CRYPTOPP_INCLUDE%" "%FULL_PATH%" /Fe:"%OUTPUT_DIR%\%FILE_NAME%_msvc.exe" /link /LIBPATH:"%CRYPTOPP_LIB_MSVC%" %MSVC_LIBS% /MACHINE:X64 %EXTRA_ARGS%
if errorlevel 1 (
    echo Lỗi khi biên dịch với MSVC
    exit /b 1
)
echo Hoàn tất: %OUTPUT_DIR%\%FILE_NAME%_msvc.exe
goto :eof

:msvc-dll
echo Biên dịch DLL với MSVC: %FILE_PATH%
%MSVC% /LD %MSVC_FLAGS% /I"%CRYPTOPP_INCLUDE%" "%FULL_PATH%" /Fe:"%OUTPUT_DIR%\%FILE_NAME%_msvc.dll" /link /LIBPATH:"%CRYPTOPP_LIB_MSVC%" %MSVC_LIBS% /MACHINE:X64 %EXTRA_ARGS%
if errorlevel 1 (
    echo Lỗi khi biên dịch DLL với MSVC
    exit /b 1
)
echo Hoàn tất: %OUTPUT_DIR%\%FILE_NAME%_msvc.dll
goto :eof

:cs
echo Biên dịch C#: %FILE_PATH%
%CSC% /nologo /debug /optimize+ /warn:4 "%FULL_PATH%" /out:"%OUTPUT_DIR%\%FILE_NAME%_cs.exe" %EXTRA_ARGS%
if errorlevel 1 (
    echo Lỗi khi biên dịch C#
    exit /b 1
)
echo Hoàn tất: %OUTPUT_DIR%\%FILE_NAME%_cs.exe
goto :eof

:java
echo Biên dịch Java: %FILE_PATH%
%JAVAC% -d "%OUTPUT_DIR%" "%FULL_PATH%" %EXTRA_ARGS%
if errorlevel 1 (
    echo Lỗi khi biên dịch Java
    exit /b 1
)
echo Hoàn tất: Class files in %OUTPUT_DIR%
goto :eof

:jni
echo Tạo JNI Header từ Java: %FILE_PATH%
if not "%FILE_EXT%"==".java" (
    echo Lỗi: Cần file Java để tạo JNI header
    exit /b 1
)
%JAVAC% -h "%FILE_DIR%" "%FULL_PATH%" %EXTRA_ARGS%
if errorlevel 1 (
    echo Lỗi khi tạo JNI header
    exit /b 1
)
echo Hoàn tất: JNI header được tạo trong %FILE_DIR%
goto :eof

:jni-dll
echo Biên dịch JNI DLL: %FILE_PATH%
if not exist "%FILE_DIR%%FILE_NAME%.h" (
    echo Cảnh báo: Không tìm thấy JNI header %FILE_DIR%%FILE_NAME%.h
    echo Đang tìm header tự động...
   
    :: Tìm tên class từ file JNI
    for /f "tokens=*" %%L in ('findstr /i /c:"JNIEXPORT" "%FULL_PATH%"') do (
        set "JNI_LINE=%%L"
        for /f "tokens=2 delims=_" %%C in ("!JNI_LINE!") do (
            set "CLASS_NAME=%%C"
            goto :found_class
        )
    )
   
    :found_class
    if not "!CLASS_NAME!"=="" (
        echo Tìm thấy lớp Java: !CLASS_NAME!
        if exist "%FILE_DIR%!CLASS_NAME!.java" (
            echo Tạo JNI header từ !CLASS_NAME!.java...
            %JAVAC% -h "%FILE_DIR%" "%FILE_DIR%!CLASS_NAME!.java"
        ) else (
            echo Lỗi: Không tìm thấy file Java tương ứng
            exit /b 1
        )
    ) else (
        echo Lỗi: Không thể xác định lớp Java từ file JNI
        echo Hãy tạo JNI header trước với: %0 jni [your_java_file.java]
        exit /b 1
    )
)

set "BASE_NAME=%FILE_NAME:InteropJNI=%"
set "CPP_FILE=%FILE_DIR%%BASE_NAME%.cpp"

if not exist "%CPP_FILE%" (
    echo Cảnh báo: Không tìm thấy file C++ cần thiết: %CPP_FILE%
    echo Sẽ chỉ biên dịch file JNI hiện tại
    set "CPP_FILE="
)

if not "%CPP_FILE%"=="" (
    %GCC% -shared %GCC_FLAGS% %JNI_INCLUDE% -I"%CRYPTOPP_INCLUDE%" "%FULL_PATH%" "%CPP_FILE%" -o "%OUTPUT_DIR%\%BASE_NAME%_jni.dll" -L"%CRYPTOPP_LIB_GCC%" %COMMON_LIBS% %EXTRA_ARGS%
) else (
    %GCC% -shared %GCC_FLAGS% %JNI_INCLUDE% -I"%CRYPTOPP_INCLUDE%" "%FULL_PATH%" -o "%OUTPUT_DIR%\%FILE_NAME%_jni.dll" -L"%CRYPTOPP_LIB_GCC%" %COMMON_LIBS% %EXTRA_ARGS%
)

if errorlevel 1 (
    echo Lỗi khi biên dịch JNI DLL
    exit /b 1
)

if not "%CPP_FILE%"=="" (
    echo Hoàn tất: %OUTPUT_DIR%\%BASE_NAME%_jni.dll
) else (
    echo Hoàn tất: %OUTPUT_DIR%\%FILE_NAME%_jni.dll
)
goto :eof

:: ===== TÍNH NĂNG MỚI =====

:debug_file
set "DEBUG_PATH=%2"
if "%DEBUG_PATH%"=="" (
    echo Lỗi: Thiếu đường dẫn file để debug. Sử dụng: %0 debug [file_path]
    exit /b 1
)

:: Lấy thông tin file
for %%F in ("%DEBUG_PATH%") do (
    set "DEBUG_DIR=%%~dpF"
    set "DEBUG_NAME=%%~nF"
    set "DEBUG_EXT=%%~xF"
    set "DEBUG_FULL=%%~fF"
    set "DEBUG_ATTR=%%~aF"
    set "DEBUG_SIZE=%%~zF"
    set "DEBUG_TIME=%%~tF"
)

echo === Debugging %DEBUG_PATH% ===
echo.
echo File:
echo  Đường dẫn đầy đủ: %DEBUG_FULL%
echo  Thư mục: %DEBUG_DIR%
echo  Tên file: %DEBUG_NAME%
echo  Phần mở rộng: %DEBUG_EXT%
echo  Thuộc tính: %DEBUG_ATTR%
echo  Kích thước: %DEBUG_SIZE% bytes
echo  Thời gian: %DEBUG_TIME%
echo.
echo Môi trường:
echo  Script path: %SCRIPT_PATH%
echo  Current path: %CURRENT_PATH%
echo  CryptoPP Include: %CRYPTOPP_INCLUDE%
echo  CryptoPP GCC Lib: %CRYPTOPP_LIB_GCC%
echo  CryptoPP Clang Lib: %CRYPTOPP_LIB_CLANG%
echo  CryptoPP MSVC Lib: %CRYPTOPP_LIB_MSVC%
echo.
echo Java/JNI:
echo  JAVA_HOME: %JAVA_HOME%
echo  JNI_INCLUDE: %JNI_INCLUDE%
echo.
echo File nội dung (20 dòng đầu):
echo ----------------------------------------
set /a line_count=0
for /f "tokens=*" %%L in (%DEBUG_PATH%) do (
    set /a line_count+=1
    if !line_count! leq 20 echo   %%L
)
echo ----------------------------------------
if %line_count% gtr 20 echo ... (còn nữa)
goto :eof

:parallel_build
echo === Biên dịch song song với %MAX_THREADS% luồng ===
set "BUILD_DIR=%~2"
set "COMPILER=%~3"
if "%BUILD_DIR%"=="" (
    echo Lỗi: Thiếu đường dẫn thư mục. Sử dụng: %0 parallel [build_dir] [compiler]
    echo Ví dụ: %0 parallel D:\code gcc
    exit /b 1
)
if "%COMPILER%"=="" set "COMPILER=gcc"

:: Kiểm tra đường dẫn
if not exist "%BUILD_DIR%" (
    echo Lỗi: Thư mục '%BUILD_DIR%' không tồn tại
    exit /b 1
)

:: Tạo script tạm thời
set "TEMP_SCRIPT=%TEMP%\parallel_build_%RANDOM%.bat"
echo @echo off > "%TEMP_SCRIPT%"
echo setlocal enabledelayedexpansion >> "%TEMP_SCRIPT%"
echo chcp 65001 ^> nul >> "%TEMP_SCRIPT%"
echo echo === Bắt đầu biên dịch song song === >> "%TEMP_SCRIPT%"

:: Tìm các file C++ và tạo lệnh biên dịch
set /a thread_count=0
set /a file_count=0
echo Tìm các file C++ trong %BUILD_DIR%...
for %%F in ("%BUILD_DIR%\*.cpp") do (
    set /a file_count+=1
    echo start /B cmd /c "%~f0 %COMPILER% %%F" >> "%TEMP_SCRIPT%"
    set /a thread_count+=1
    if !thread_count! geq %MAX_THREADS% (
        echo timeout /t 2 >> "%TEMP_SCRIPT%"
        set /a thread_count=0
    )
)

if %file_count% equ 0 (
    echo Không tìm thấy file C++ nào trong %BUILD_DIR%
    del "%TEMP_SCRIPT%" 2>nul
    exit /b 1
)

:: Thêm lệnh wait
echo echo Đang chờ tất cả các tiến trình hoàn thành... >> "%TEMP_SCRIPT%"
echo timeout /t 5 >> "%TEMP_SCRIPT%"
echo echo === Biên dịch song song hoàn tất === >> "%TEMP_SCRIPT%"

:: Chạy script
echo Tìm thấy %file_count% file C++. Đang biên dịch song song...
call "%TEMP_SCRIPT%"

:: Dọn dẹp
del "%TEMP_SCRIPT%" 2>nul
goto :eof

:build_project
echo === Xây dựng project: %FILE_PATH% ===

:: Kiểm tra xem FILE_PATH là file hay thư mục
set "IS_DIR=0"
if exist "%FILE_PATH%\" set "IS_DIR=1"

if "%IS_DIR%"=="1" (
    set "SRC_DIR=%FILE_PATH%"
) else (
    for %%F in ("%FILE_PATH%") do set "SRC_DIR=%%~dpF"
)

:: Tạo thư mục build nếu chưa có
set "BUILD_DIR=%SRC_DIR%build"
if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"

:: Tìm file chính (main)
set "MAIN_FILE="
for %%F in ("%SRC_DIR%\*.cpp") do (
    for /f "tokens=*" %%L in ('findstr /i /c:"main" "%%F"') do (
        set "MAIN_FILE=%%F"
        goto :found_main
    )
)

:found_main
if "%MAIN_FILE%"=="" (
    echo Cảnh báo: Không tìm thấy file chứa hàm main. Đang tìm file đầu tiên...
    for %%F in ("%SRC_DIR%\*.cpp") do (
        set "MAIN_FILE=%%F"
        goto :found_any
    )
)

:found_any
if "%MAIN_FILE%"=="" (
    echo Lỗi: Không tìm thấy file C++ nào trong thư mục %SRC_DIR%
    exit /b 1
)

echo Tìm thấy file chính: %MAIN_FILE%

:: Tìm tất cả các source file
echo Tìm các file source...
set "OBJ_FILES="
for %%F in ("%SRC_DIR%\*.cpp") do (
    echo Biên dịch %%F thành object file...
    for %%G in ("%%F") do (
        set "FILE_NAME=%%~nG"
        %GCC% -c %GCC_FLAGS% -I"%CRYPTOPP_INCLUDE%" -I"%SRC_DIR%" "%%F" -o "%BUILD_DIR%\!FILE_NAME!.o"
        if errorlevel 1 (
            echo Lỗi khi biên dịch %%F
            exit /b 1
        )
        set "OBJ_FILES=!OBJ_FILES! "%BUILD_DIR%\!FILE_NAME!.o""
    )
)

:: Liên kết tất cả các object file
echo Liên kết các object file...
for %%F in ("%MAIN_FILE%") do set "MAIN_NAME=%%~nF"
%GCC% %OBJ_FILES% -o "%BUILD_DIR%\%MAIN_NAME%.exe" -L"%CRYPTOPP_LIB_GCC%" %COMMON_LIBS%
if errorlevel 1 (
    echo Lỗi khi liên kết
    exit /b 1
)

echo Hoàn tất: %BUILD_DIR%\%MAIN_NAME%.exe
goto :eof

:jni_build
echo === Xây dựng JNI đầy đủ cho: %FILE_PATH% ===

:: 1. Kiểm tra file đầu vào là Java
if not "%FILE_EXT%"==".java" (
    echo Lỗi: Cần file Java để bắt đầu quy trình JNI
    exit /b 1
)

:: 2. Tạo thư mục build nếu chưa có
set "JNI_BUILD_DIR=%FILE_DIR%jni-build"
if not exist "%JNI_BUILD_DIR%" mkdir "%JNI_BUILD_DIR%"

:: 3. Biên dịch Java
echo [Bước 1/5] Biên dịch Java...
%JAVAC% -d "%JNI_BUILD_DIR%" "%FULL_PATH%"
if errorlevel 1 (
    echo Lỗi khi biên dịch Java
    exit /b 1
)

:: 4. Tạo JNI header
echo [Bước 2/5] Tạo JNI header...
%JAVAC% -h "%FILE_DIR%" "%FULL_PATH%"
if errorlevel 1 (
    echo Lỗi khi tạo JNI header
    exit /b 1
)

:: 5. Tìm file C++ tương ứng
set "JNI_IMPL_FILE=%FILE_DIR%%FILE_NAME%Impl.cpp"
set "JNI_NATIVE_FILE=%FILE_DIR%%FILE_NAME%Native.cpp"
set "JNI_INTEROP_FILE=%FILE_DIR%%FILE_NAME%InteropJNI.cpp"

set "CPP_FILE="
if exist "%JNI_IMPL_FILE%" (
    set "CPP_FILE=%JNI_IMPL_FILE%"
    echo Tìm thấy file implementation: %JNI_IMPL_FILE%
) else if exist "%JNI_NATIVE_FILE%" (
    set "CPP_FILE=%JNI_NATIVE_FILE%"
    echo Tìm thấy file native: %JNI_NATIVE_FILE%
) else if exist "%JNI_INTEROP_FILE%" (
    set "CPP_FILE=%JNI_INTEROP_FILE%"
    echo Tìm thấy file interop: %JNI_INTEROP_FILE%
) else (
    echo [Bước 3/5] Tạo file C++ mẫu...
    echo // JNI Implementation for %FILE_NAME% > "%JNI_IMPL_FILE%"
    echo // Auto-generated by BuildHelper >> "%JNI_IMPL_FILE%"
    echo #include "%FILE_NAME%.h" >> "%JNI_IMPL_FILE%"
    echo #include ^<stdio.h^> >> "%JNI_IMPL_FILE%"
    echo. >> "%JNI_IMPL_FILE%"
   
    :: Extract method signatures from the header file
    for /f "tokens=*" %%L in ('findstr /n /i "JNIEXPORT" "%FILE_DIR%%FILE_NAME%.h"') do (
        set "JNI_LINE=%%L"
        set "JNI_LINE=!JNI_LINE:*JNIEXPORT=JNIEXPORT!"
        set "JNI_LINE=!JNI_LINE:*)=*){"
        echo !JNI_LINE! >> "%JNI_IMPL_FILE%"
        echo     printf^("JNI method called\\n"^); >> "%JNI_IMPL_FILE%"
        echo     // TODO: Implement this method >> "%JNI_IMPL_FILE%"
        echo } >> "%JNI_IMPL_FILE%"
        echo. >> "%JNI_IMPL_FILE%"
    )
    set "CPP_FILE=%JNI_IMPL_FILE%"
    echo Đã tạo file C++ mẫu: %JNI_IMPL_FILE%
)

:: 6. Biên dịch JNI DLL
echo [Bước 4/5] Biên dịch JNI DLL...
%GCC% -shared %GCC_FLAGS% %JNI_INCLUDE% -I"%CRYPTOPP_INCLUDE%" "%CPP_FILE%" -o "%JNI_BUILD_DIR%\%FILE_NAME%_jni.dll" -L"%CRYPTOPP_LIB_GCC%" %COMMON_LIBS%
if errorlevel 1 (
    echo Lỗi khi biên dịch JNI DLL
    exit /b 1
)

:: 7. Tạo file chạy thử
echo [Bước 5/5] Tạo batch file để chạy thử...
echo @echo off > "%JNI_BUILD_DIR%\run_%FILE_NAME%.bat"
echo set "PATH=%JNI_BUILD_DIR%;%%PATH%%" >> "%JNI_BUILD_DIR%\run_%FILE_NAME%.bat"
echo cd /d "%JNI_BUILD_DIR%" >> "%JNI_BUILD_DIR%\run_%FILE_NAME%.bat"
echo java %FILE_NAME% >> "%JNI_BUILD_DIR%\run_%FILE_NAME%.bat"
echo pause >> "%JNI_BUILD_DIR%\run_%FILE_NAME%.bat"

echo === JNI build hoàn tất ===
echo.
echo File output:
echo  - Java class: %JNI_BUILD_DIR%\%FILE_NAME%.class
echo  - JNI header: %FILE_DIR%%FILE_NAME%.h
echo  - C++ impl  : %CPP_FILE%
echo  - JNI DLL   : %JNI_BUILD_DIR%\%FILE_NAME%_jni.dll
echo  - Run script: %JNI_BUILD_DIR%\run_%FILE_NAME%.bat
echo.
echo Để chạy thử, thực thi: %JNI_BUILD_DIR%\run_%FILE_NAME%.bat
goto :eof


:: ===== TÍNH NĂNG MỚI =====


:debug_file
set "DEBUG_PATH=%2"
if "%DEBUG_PATH%"=="" (
    echo Lỗi: Thiếu đường dẫn file để debug. Sử dụng: %0 debug [file_path]
    exit /b 1
)


:: Lấy thông tin file
for %%F in ("%DEBUG_PATH%") do (
    set "DEBUG_DIR=%%~dpF"
    set "DEBUG_NAME=%%~nF"
    set "DEBUG_EXT=%%~xF"
    set "DEBUG_FULL=%%~fF"
    set "DEBUG_ATTR=%%~aF"
    set "DEBUG_SIZE=%%~zF"
    set "DEBUG_TIME=%%~tF"
)


echo === Debugging %DEBUG_PATH% ===
echo.
echo File:
echo  Đường dẫn đầy đủ: %DEBUG_FULL%
echo  Thư mục: %DEBUG_DIR%
echo  Tên file: %DEBUG_NAME%
echo  Phần mở rộng: %DEBUG_EXT%
echo  Thuộc tính: %DEBUG_ATTR%
echo  Kích thước: %DEBUG_SIZE% bytes
echo  Thời gian: %DEBUG_TIME%
echo.
echo Môi trường:
echo  Script path: %SCRIPT_PATH%
echo  Current path: %CURRENT_PATH%
echo  CryptoPP Include: %CRYPTOPP_INCLUDE%
echo  CryptoPP GCC Lib: %CRYPTOPP_LIB_GCC%
echo  CryptoPP Clang Lib: %CRYPTOPP_LIB_CLANG%
echo  CryptoPP MSVC Lib: %CRYPTOPP_LIB_MSVC%
echo.
echo Java/JNI:
echo  JAVA_HOME: %JAVA_HOME%
echo  JNI_INCLUDE: %JNI_INCLUDE%
echo.
echo File nội dung (20 dòng đầu):
echo ----------------------------------------
set /a line_count=0
for /f "tokens=*" %%L in (%DEBUG_PATH%) do (
    set /a line_count+=1
    if !line_count! leq 20 echo   %%L
)
echo ----------------------------------------
if %line_count% gtr 20 echo ... (còn nữa)
goto :eof


:parallel_build
echo === Biên dịch song song với %MAX_THREADS% luồng ===
set "BUILD_DIR=%~2"
set "COMPILER=%~3"
if "%BUILD_DIR%"=="" (
    echo Lỗi: Thiếu đường dẫn thư mục. Sử dụng: %0 parallel [build_dir] [compiler]
    echo Ví dụ: %0 parallel D:\code gcc
    exit /b 1
)
if "%COMPILER%"=="" set "COMPILER=gcc"


:: Kiểm tra đường dẫn
if not exist "%BUILD_DIR%" (
    echo Lỗi: Thư mục '%BUILD_DIR%' không tồn tại
    exit /b 1
)


:: Tạo script tạm thời
set "TEMP_SCRIPT=%TEMP%\parallel_build_%RANDOM%.bat"
echo @echo off > "%TEMP_SCRIPT%"
echo setlocal enabledelayedexpansion >> "%TEMP_SCRIPT%"
echo chcp 65001 ^> nul >> "%TEMP_SCRIPT%"
echo echo === Bắt đầu biên dịch song song === >> "%TEMP_SCRIPT%"


:: Tìm các file C++ và tạo lệnh biên dịch
set /a thread_count=0
set /a file_count=0
echo Tìm các file C++ trong %BUILD_DIR%...
for %%F in ("%BUILD_DIR%\*.cpp") do (
    set /a file_count+=1
    echo start /B cmd /c "%~f0 %COMPILER% %%F" >> "%TEMP_SCRIPT%"
    set /a thread_count+=1
    if !thread_count! geq %MAX_THREADS% (
        echo timeout /t 2 >> "%TEMP_SCRIPT%"
        set /a thread_count=0
    )
)


if %file_count% equ 0 (
    echo Không tìm thấy file C++ nào trong %BUILD_DIR%
    del "%TEMP_SCRIPT%" 2>nul
    exit /b 1
)


:: Thêm lệnh wait
echo echo Đang chờ tất cả các tiến trình hoàn thành... >> "%TEMP_SCRIPT%"
echo timeout /t 5 >> "%TEMP_SCRIPT%"
echo echo === Biên dịch song song hoàn tất === >> "%TEMP_SCRIPT%"


:: Chạy script
echo Tìm thấy %file_count% file C++. Đang biên dịch song song...
call "%TEMP_SCRIPT%"


:: Dọn dẹp
del "%TEMP_SCRIPT%" 2>nul
goto :eof


:build_project
echo === Xây dựng project: %FILE_PATH% ===


:: Kiểm tra xem FILE_PATH là file hay thư mục
set "IS_DIR=0"
if exist "%FILE_PATH%\" set "IS_DIR=1"


if "%IS_DIR%"=="1" (
    set "SRC_DIR=%FILE_PATH%"
) else (
    for %%F in ("%FILE_PATH%") do set "SRC_DIR=%%~dpF"
)


:: Tạo thư mục build nếu chưa có
set "BUILD_DIR=%SRC_DIR%build"
if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"


:: Tìm file chính (main)
set "MAIN_FILE="
for %%F in ("%SRC_DIR%\*.cpp") do (
    for /f "tokens=*" %%L in ('findstr /i /c:"main" "%%F"') do (
        set "MAIN_FILE=%%F"
        goto :found_main
    )
)


:found_main
if "%MAIN_FILE%"=="" (
    echo Cảnh báo: Không tìm thấy file chứa hàm main. Đang tìm file đầu tiên...
    for %%F in ("%SRC_DIR%\*.cpp") do (
        set "MAIN_FILE=%%F"
        goto :found_any
    )
)


:found_any
if "%MAIN_FILE%"=="" (
    echo Lỗi: Không tìm thấy file C++ nào trong thư mục %SRC_DIR%
    exit /b 1
)


echo Tìm thấy file chính: %MAIN_FILE%


:: Tìm tất cả các source file
echo Tìm các file source...
set "OBJ_FILES="
for %%F in ("%SRC_DIR%\*.cpp") do (
    echo Biên dịch %%F thành object file...
    for %%G in ("%%F") do (
        set "FILE_NAME=%%~nG"
        %GCC% -c %GCC_FLAGS% -I"%CRYPTOPP_INCLUDE%" -I"%SRC_DIR%" "%%F" -o "%BUILD_DIR%\!FILE_NAME!.o"
        if errorlevel 1 (
            echo Lỗi khi biên dịch %%F
            exit /b 1
        )
        set "OBJ_FILES=!OBJ_FILES! "%BUILD_DIR%\!FILE_NAME!.o""
    )
)


:: Liên kết tất cả các object file
echo Liên kết các object file...
for %%F in ("%MAIN_FILE%") do set "MAIN_NAME=%%~nF"
%GCC% %OBJ_FILES% -o "%BUILD_DIR%\%MAIN_NAME%.exe" -L"%CRYPTOPP_LIB_GCC%" %COMMON_LIBS%
if errorlevel 1 (
    echo Lỗi khi liên kết
    exit /b 1
)


echo Hoàn tất: %BUILD_DIR%\%MAIN_NAME%.exe
goto :eof


:jni_build
echo === Xây dựng JNI đầy đủ cho: %FILE_PATH% ===


:: 1. Kiểm tra file đầu vào là Java
if not "%FILE_EXT%"==".java" (
    echo Lỗi: Cần file Java để bắt đầu quy trình JNI
    exit /b 1
)


:: 2. Tạo thư mục build nếu chưa có
set "JNI_BUILD_DIR=%FILE_DIR%jni-build"
if not exist "%JNI_BUILD_DIR%" mkdir "%JNI_BUILD_DIR%"


:: 3. Biên dịch Java
echo [Bước 1/5] Biên dịch Java...
%JAVAC% -d "%JNI_BUILD_DIR%" "%FULL_PATH%"
if errorlevel 1 (
    echo Lỗi khi biên dịch Java
    exit /b 1
)


:: 4. Tạo JNI header
echo [Bước 2/5] Tạo JNI header...
%JAVAC% -h "%FILE_DIR%" "%FULL_PATH%"
if errorlevel 1 (
    echo Lỗi khi tạo JNI header
    exit /b 1
)


:: 5. Tìm file C++ tương ứng
set "JNI_IMPL_FILE=%FILE_DIR%%FILE_NAME%Impl.cpp"
set "JNI_NATIVE_FILE=%FILE_DIR%%FILE_NAME%Native.cpp"
set "JNI_INTEROP_FILE=%FILE_DIR%%FILE_NAME%InteropJNI.cpp"


set "CPP_FILE="
if exist "%JNI_IMPL_FILE%" (
    set "CPP_FILE=%JNI_IMPL_FILE%"
    echo Tìm thấy file implementation: %JNI_IMPL_FILE%
) else if exist "%JNI_NATIVE_FILE%" (
    set "CPP_FILE=%JNI_NATIVE_FILE%"
    echo Tìm thấy file native: %JNI_NATIVE_FILE%
) else if exist "%JNI_INTEROP_FILE%" (
    set "CPP_FILE=%JNI_INTEROP_FILE%"
    echo Tìm thấy file interop: %JNI_INTEROP_FILE%
) else (
    echo [Bước 3/5] Tạo file C++ mẫu...
    echo // JNI Implementation for %FILE_NAME% > "%JNI_IMPL_FILE%"
    echo // Auto-generated by BuildHelper >> "%JNI_IMPL_FILE%"
    echo #include "%FILE_NAME%.h" >> "%JNI_IMPL_FILE%"
    echo #include ^<stdio.h^> >> "%JNI_IMPL_FILE%"
    echo. >> "%JNI_IMPL_FILE%"
   
    :: Extract method signatures from the header file
    for /f "tokens=*" %%L in ('findstr /n /i "JNIEXPORT" "%FILE_DIR%%FILE_NAME%.h"') do (
        set "JNI_LINE=%%L"
        set "JNI_LINE=!JNI_LINE:*JNIEXPORT=JNIEXPORT!"
        set "JNI_LINE=!JNI_LINE:*)=*){"
        echo !JNI_LINE! >> "%JNI_IMPL_FILE%"
        echo     printf^("JNI method called\\n"^); >> "%JNI_IMPL_FILE%"
        echo     // TODO: Implement this method >> "%JNI_IMPL_FILE%"
        echo } >> "%JNI_IMPL_FILE%"
        echo. >> "%JNI_IMPL_FILE%"
    )
    set "CPP_FILE=%JNI_IMPL_FILE%"
    echo Đã tạo file C++ mẫu: %JNI_IMPL_FILE%
)


:: 6. Biên dịch JNI DLL
echo [Bước 4/5] Biên dịch JNI DLL...
%GCC% -shared %GCC_FLAGS% %JNI_INCLUDE% -I"%CRYPTOPP_INCLUDE%" "%CPP_FILE%" -o "%JNI_BUILD_DIR%\%FILE_NAME%_jni.dll" -L"%CRYPTOPP_LIB_GCC%" %COMMON_LIBS%
if errorlevel 1 (
    echo Lỗi khi biên dịch JNI DLL
    exit /b 1
)


:: 7. Tạo file chạy thử
echo [Bước 5/5] Tạo batch file để chạy thử...
echo @echo off > "%JNI_BUILD_DIR%\run_%FILE_NAME%.bat"
echo set "PATH=%JNI_BUILD_DIR%;%%PATH%%" >> "%JNI_BUILD_DIR%\run_%FILE_NAME%.bat"
echo cd /d "%JNI_BUILD_DIR%" >> "%JNI_BUILD_DIR%\run_%FILE_NAME%.bat"
echo java %FILE_NAME% >> "%JNI_BUILD_DIR%\run_%FILE_NAME%.bat"
echo pause >> "%JNI_BUILD_DIR%\run_%FILE_NAME%.bat"


echo === JNI build hoàn tất ===
echo.
echo File output:
echo  - Java class: %JNI_BUILD_DIR%\%FILE_NAME%.class
echo  - JNI header: %FILE_DIR%%FILE_NAME%.h
echo  - C++ impl  : %CPP_FILE%
echo  - JNI DLL   : %JNI_BUILD_DIR%\%FILE_NAME%_jni.dll
echo  - Run script: %JNI_BUILD_DIR%\run_%FILE_NAME%.bat
echo.
echo Để chạy thử, thực thi: %JNI_BUILD_DIR%\run_%FILE_NAME%.bat
goto :eof


:: ===== TÍNH NĂNG MỚI =====


:check_env
echo === Kiểm tra môi trường phát triển ===
where g++.exe >nul 2>&1 && echo GCC: Có sẵn || echo GCC: Không tìm thấy
where clang++.exe >nul 2>&1 && echo Clang: Có sẵn || echo Clang: Không tìm thấy
where cl.exe >nul 2>&1 && echo MSVC: Có sẵn || echo MSVC: Không tìm thấy
where javac.exe >nul 2>&1 && echo Java: Có sẵn || echo Java: Không tìm thấy
where csc.exe >nul 2>&1 && echo C#: Có sẵn || echo C#: Không tìm thấy


echo.
echo === Thông tin thư mục ===
echo Script path: %SCRIPT_PATH%
echo Current path: %CURRENT_PATH%


echo.
echo === Thư viện CryptoPP ===
if exist "%CRYPTOPP_INCLUDE%" (
    echo CryptoPP Include: %CRYPTOPP_INCLUDE% [✓]
) else (
    echo CryptoPP Include: %CRYPTOPP_INCLUDE% [✗]
)
goto :eof

:clean_all
echo ===== Dọn dẹp các thư mục output =====


:: Xử lý tham số đường dẫn (nếu có)
set "CLEAN_PATH=%2"
if not "%CLEAN_PATH%"=="" (
    if not exist "%CLEAN_PATH%" (
        echo Lỗi: Không tìm thấy đường dẫn '%CLEAN_PATH%'
        exit /b 1
    )
    set "CLEAN_ROOT=%CLEAN_PATH%"
) else (
    set "CLEAN_ROOT=%CRYPTOPP_ROOT%"
)


:: Chỉ xóa các thư mục output trừ những thư mục trong lib/cryptopp
for /d /r "%CLEAN_ROOT%" %%D in (gcc gcc-dll clang clang-dll msvc msvc-dll java cs build jni-build) do (
    set "DIR_PATH=%%D"
    echo "!DIR_PATH!" | findstr /i "\lib\cryptopp\\" >nul || (
        if exist "%%D" (
            echo Xóa thư mục: %%D
            rmdir /s /q "%%D"
        )
    )
)


echo Xóa các file tạm...
:: Chỉ xóa ở thư mục hiện tại, không xóa trong thư mục lib và include
for %%E in (obj pdb ilk exp class) do (
    for /f "tokens=*" %%F in ('dir /s /b "%CLEAN_ROOT%\*.%%E" 2^>nul') do (
        echo "%%F" | findstr /i "\lib\\" >nul || (
            echo "%%F" | findstr /i "\include\\" >nul || (
                echo Xóa: %%F
                del "%%F" 2>nul
            )
        )
    )
)


:: Xóa các file header JNI tự động tạo (tùy chọn)
echo Xóa các file header JNI tự động tạo...
for /f "tokens=*" %%F in ('dir /s /b "%CLEAN_ROOT%\*_jni.h" "%CLEAN_ROOT%\*JNI.h" 2^>nul') do (
    echo "%%F" | findstr /i "\lib\\" >nul || (
        echo "%%F" | findstr /i "\include\\" >nul || (
            echo Xóa: %%F
            del "%%F" 2>nul
        )
    )
)


echo ===== Dọn dẹp hoàn tất =====
goto :eof


:help
echo.
echo BuildHelper - Công cụ biên dịch đơn giản cho CryptoPP
echo ===================================================
echo Phiên bản: 2.1
echo.
echo Sử dụng: %0 [command] [file_path] [extra_args]
echo.
echo Lệnh biên dịch cơ bản:
echo   gcc         Biên dịch exe với GCC
echo   gcc-dll     Biên dịch dll với GCC
echo   gcc-obj     Tạo object file với GCC
echo   clang       Biên dịch exe với Clang
echo   clang-dll   Biên dịch dll với Clang
echo   msvc        Biên dịch exe với MSVC
echo   msvc-dll    Biên dịch dll với MSVC
echo   cs          Biên dịch C#
echo   java        Biên dịch Java
echo.
echo Lệnh JNI:
echo   jni         Tạo JNI header từ file Java
echo   jni-dll     Biên dịch JNI DLL từ file C++
echo   jni-build   Quy trình JNI đầy đủ (Java -> Header -> DLL)
echo.
echo Lệnh nâng cao:
echo   parallel    Biên dịch song song nhiều file với GCC
echo   check       Kiểm tra trình biên dịch và môi trường
echo   debug       Hiển thị thông tin debug về file
echo   clean       Dọn dẹp file và thư mục output
echo   help        Hiển thị trợ giúp này
echo.
echo Ví dụ:
echo   %0 gcc test.cpp                    - Biên dịch test.cpp với GCC
echo   %0 gcc test.cpp -O3 -std=c++17     - Thêm flags compiler
echo   %0 jni-build CryptoJNI.java        - Build JNI đầy đủ
echo   %0 parallel D:\code\src gcc        - Build song song nhiều file
echo   %0 clean D:\code                   - Dọn dẹp thư mục cụ thể
echo.
echo Lưu ý:
echo   - Đường dẫn tương đối và tuyệt đối đều được hỗ trợ
echo   - Kết quả được lưu trong thư mục con tương ứng với lệnh
echo     Ví dụ: test.cpp -> gcc\test_gcc.exe, clang\test_clang.exe
echo   - Thư mục lib\cryptopp sẽ KHÔNG bị ảnh hưởng khi dọn dẹp
echo   - Thêm parameters cho compiler bằng cách thêm vào sau file_path
echo.
echo Xem thêm ví dụ sử dụng: %0 help examples
if "%2"=="examples" goto :help_examples
goto :eof


:help_examples
echo.
echo Ví dụ chi tiết:
echo ===================================================
echo.
echo 1. Biên dịch C++ đơn giản:
echo    %0 gcc D:\code\main.cpp
echo    %0 clang test.cpp -std=c++17
echo    %0 msvc Project.cpp /EHsc
echo.
echo 2. Biên dịch thư viện DLL:
echo    %0 gcc-dll MyLib.cpp
echo    %0 msvc-dll CryptoLib.cpp
echo.
echo 3. JNI workflow:
echo    %0 jni-build CryptoJNI.java       - Quy trình đầy đủ tự động
echo    - HOẶC thủ công từng bước -
echo    %0 java CryptoJNI.java            - Biên dịch Java
echo    %0 jni CryptoJNI.java             - Tạo JNI header
echo    %0 jni-dll CryptoJNIImpl.cpp      - Biên dịch JNI DLL
echo.
echo 4. Build song song:
echo    %0 parallel D:\code\src gcc       - Biên dịch với GCC
echo    %0 parallel D:\code\src clang     - Biên dịch với Clang
echo.
echo 5. Các lệnh mới:
echo    %0 check                          - Kiểm tra môi trường
echo.
echo 6. Các lệnh tiện ích:
echo    %0 debug MyClass.java             - Xem thông tin chi tiết về file
echo    %0 clean                          - Dọn dẹp tất cả
echo    %0 clean D:\code\project          - Dọn dẹp thư mục cụ thể
echo.
goto :eof