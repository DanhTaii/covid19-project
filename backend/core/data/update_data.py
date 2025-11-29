import urllib.request
from pathlib import Path
import socket

URL = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
RAW_FILE = Path(__file__).parent / "owid-covid-data.csv"

def download_latest():
    if RAW_FILE.exists():
        size_mb = RAW_FILE.stat().st_size // 1024 // 1024
        print(f"Đã có file cũ: {RAW_FILE.name} ({size_mb} MB)")

    print("Đang thử tải dữ liệu mới nhất từ OWID...")
    try:
        # Dùng request + timeout thủ công (cách đúng nhất Python 3.11+)
        req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            with open(RAW_FILE, 'wb') as out_file:
                out_file.write(response.read())
        size_mb = RAW_FILE.stat().st_size // 1024 // 1024
        print(f"ĐÃ TẢI XONG MỚI NHẤT! → owid-covid-data.csv ({size_mb} MB)")
    except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError) as e:
        print("Không có mạng hoặc bị chặn OWID → dùng file cũ!")
        if not RAW_FILE.exists():
            print("LỖI: Không có file owid-covid-data.csv nào cả!")
            print("Vui lòng tải tay từ: https://covid.ourworldindata.org/data/owid-covid-data.csv")
            print("và đặt vào thư mục backend/covid_app/data/")
            exit(1)
        else:
            print("Tiếp tục dùng file cũ để preprocessing...")

if __name__ == "__main__":
    download_latest()