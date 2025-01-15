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

# Danh sách các package cần kiểm tra
required_packages = ["cryptography", "argparse", "getpass"]

# Đảm bảo tất cả các package cần thiết
for package in required_packages:
    ensure_package_installed(package)

# Import sau khi đảm bảo tất cả các package đã được cài đặt
import base64
import hashlib
from cryptography.fernet import Fernet
import argparse
import getpass

def decrypt_file(encrypted_file, output_file, password):
    # Tạo khóa từ mật khẩu
    key = base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())
    cipher = Fernet(key)

    # Đọc file mã hóa
    with open(encrypted_file, 'rb') as f:
        encrypted_data = f.read()

    # Giải mã và ghi vào file mới
    try:
        decrypted_data = cipher.decrypt(encrypted_data)
        with open(output_file, 'wb') as f:
            f.write(decrypted_data)
        print(f"File {encrypted_file} đã được giải mã thành {output_file}.")
    except Exception as e:
        print(f"Giải mã thất bại: {str(e)}")

if __name__ == "__main__":
    # Cấu hình argparse
    parser = argparse.ArgumentParser(description="Giải mã file JSON được mã hóa bằng mật khẩu.")
    parser.add_argument(
        "encrypted_file",
        nargs="?",
        default="secrets.json.enc",
        help="Đường dẫn đến file mã hóa (mặc định: secrets.json.enc).",
    )
    parser.add_argument(
        "output_file",
        nargs="?",
        default="secrets.json",
        help="Đường dẫn để lưu file đã giải mã (mặc định: secrets.json).",
    )

    args = parser.parse_args()

    # Yêu cầu nhập mật khẩu từ terminal
    password = getpass.getpass(prompt="Nhập mật khẩu để giải mã file: ")

    # Gọi hàm giải mã
    decrypt_file(args.encrypted_file, args.output_file, password)
