import json
import subprocess
import os

def call_decode_script(decode_script, encrypted_file, output_file):
    """
    Gọi file decode.py để giải mã secrets.json.enc thành secrets.json.
    :param decode_script: Đường dẫn tới file decode.py.
    :param encrypted_file: Đường dẫn tới file mã hóa (ví dụ: secrets.json.enc).
    :param output_file: Đường dẫn tới file đã giải mã (ví dụ: secrets.json).
    """
    try:
        # Gọi file decode.py thông qua subprocess
        subprocess.run(
            ["python", decode_script, encrypted_file, output_file],
            check=True,
        )
        print(f"[SUCCESS] File {encrypted_file} đã được giải mã thành {output_file}.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Không thể giải mã file: {e}")
        exit(1)

def add_secrets_to_kaggle(decode_script, encrypted_file, secrets_file, competition=None):
    """
    Giải mã file mã hóa và thêm secrets từ file JSON vào Kaggle.
    :param decode_script: Đường dẫn tới file decode.py.
    :param encrypted_file: Đường dẫn tới file mã hóa (ví dụ: secrets.json.enc).
    :param secrets_file: Đường dẫn tới file JSON sau khi giải mã (ví dụ: secrets.json).
    :param competition: (Tùy chọn) Tên competition nếu muốn gắn secrets với một competition cụ thể.
    """
    # Bước 1: Gọi script decode.py để giải mã file
    call_decode_script(decode_script, encrypted_file, secrets_file)

    # Bước 2: Đọc file secrets.json
    if not os.path.exists(secrets_file):
        print(f"[ERROR] File {secrets_file} không tồn tại sau khi giải mã.")
        return

    try:
        with open(secrets_file, "r") as f:
            secrets = json.load(f)
    except Exception as e:
        print(f"[ERROR] Lỗi khi đọc file {secrets_file}: {str(e)}")
        return

    # Bước 3: Thêm từng secret vào Kaggle
    for key, value in secrets.items():
        command = f'kaggle secrets set {key} "{value}"'
        if competition:
            command += f" --competition {competition}"
        try:
            subprocess.run(command, shell=True, check=True)
            print(f"[SUCCESS] Đã thêm secret: {key}")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Không thể thêm secret: {key}. Error: {e}")

    print("Hoàn thành việc thêm tất cả secrets vào Kaggle.")

if __name__ == "__main__":
    # Đường dẫn tới file decode.py
    decode_script = "decode.py"

    # Đường dẫn tới file mã hóa và file giải mã
    encrypted_file = "secrets.json.enc"
    secrets_file = "secrets.json"

    # Tùy chọn: Gắn secrets với một competition cụ thể
    competition_name = None  # Thay bằng tên competition nếu cần, ví dụ: "titanic"

    # Thực hiện việc thêm secrets
    add_secrets_to_kaggle(decode_script, encrypted_file, secrets_file, competition=competition_name)
