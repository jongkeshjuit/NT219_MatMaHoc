## Nếu không dùng UI có thể export biến môi trường trên window để đặt alias, chỉ cần gọi và thực hiện các câu lệnh sau

BuildHelper - Công cụ biên dịch đơn giản cho CryptoPP
===================================================
Phiên bản: 1.0 by Vương Thành Đạt

Sử dụng: "D:\WorkSpace\NT219\a.bat" [command] [file_path] [extra_args]

Lệnh biên dịch cơ bản:
  gcc         Biên dịch exe với GCC
  gcc-dll     Biên dịch dll với GCC  
  gcc-obj     Tạo object file với GCC
  clang       Biên dịch exe với Clang
  clang-dll   Biên dịch dll với Clang
  msvc        Biên dịch exe với MSVC 
  msvc-dll    Biên dịch dll với MSVC 
  cs          Biên dịch C#
  java        Biên dịch Java

Lệnh JNI:
  jni         Tạo JNI header từ file Java
  jni-dll     Biên dịch JNI DLL từ file C++

Lệnh nâng cao:
  parallel    Biên dịch song song nhiều file với GCC
  check       Kiểm tra trình biên dịch và môi trường
  debug       Hiển thị thông tin debug về file
  clean       Dọn dẹp file và thư mục output
  help        Hiển thị trợ giúp này

Ví dụ:
  "D:\WorkSpace\NT219\a.bat" gcc test.cpp                    - Biên dịch test.cpp với GCC
  "D:\WorkSpace\NT219\a.bat" gcc test.cpp -O3 -std=c++17     - Thêm flags compiler
  "D:\WorkSpace\NT219\a.bat" jni-build CryptoJNI.java        - Build JNI đầy đủ
  "D:\WorkSpace\NT219\a.bat" parallel D:\code\src gcc        - Build song song nhiều file
  "D:\WorkSpace\NT219\a.bat" clean D:\code                   - Dọn dẹp thư mục cụ thể

Lưu ý:
  - Đường dẫn tương đối và tuyệt đối đều được hỗ trợ
  - Kết quả được lưu trong thư mục con tương ứng với lệnh
The system cannot find the path specified.
  - Thư mục lib\cryptopp sẽ KHÔNG bị ảnh hưởng khi dọn dẹp
  - Thêm parameters cho compiler bằng cách thêm vào sau file_path

Xem thêm ví dụ sử dụng: "D:\WorkSpace\NT219\a.bat" help examples