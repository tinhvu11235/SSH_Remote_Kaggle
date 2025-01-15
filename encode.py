import subprocess
import sys

# Hàm kiểm tra và cài đặt package nếu cần thiết
def ensure_package_installed(package_name):
    try:
        __import__(package_name)
    except ImportError:
        print(f"Package '{package_name}' chưa được cài đặt. Đang tiến hành cài đặt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"Package '{package_name}' đã được cài đặt.")

# Đảm bảo tất cả các package cần thiết
required_packages = ["cryptography", "getpass"]
for package in required_packages:
    ensure_package_installed(package)

# Import các package sau khi đảm bảo đã được cài đặt
from cryptography.fernet import Fernet
import base64
import hashlib
import getpass

# Hàm mã hóa file
def encrypt_file(input_file, output_file, password):
    # Tạo khóa từ mật khẩu
    key = base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())
    cipher = Fernet(key)

    # Đọc nội dung file JSON
    with open(input_file, 'rb') as f:
        data = f.read()

    # Mã hóa và ghi vào file mới
    encrypted_data = cipher.encrypt(data)
    with open(output_file, 'wb') as f:
        f.write(encrypted_data)

    print(f"File {input_file} đã được mã hóa thành {output_file}.")

if __name__ == "__main__":
    # Yêu cầu nhập mật khẩu từ người dùng
    password = getpass.getpass(prompt="Nhập mật khẩu để mã hóa file: ")

    # Thực hiện mã hóa file
    encrypt_file("secrets.json", "secrets.json.enc", password)
