import requests
from bs4 import BeautifulSoup

URL = "https://m.asics.co.kr/p/AKR_112430207-002"
TARGET_TEXT = "품절"

def check_stock():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        resp = requests.get(URL, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        if TARGET_TEXT in soup.get_text():
            print("품절")
        else:
            print("입고")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_stock()
