# monitor_nimbus26.py
import os
import requests
from bs4 import BeautifulSoup

MOBILE_URL = os.getenv("TARGET_URL",  "https://m.asics.co.kr/p/AKR_122532006-001")
DESKTOP_URL = os.getenv("FALLBACK_URL","https://asics.co.kr/p/AKR_122532006-001")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# 판정 키워드
OOS_KEYWORDS     = ["품절", "일시품절", "SOLD OUT"]
INSTOCK_KEYWORDS = ["구매하기", "장바구니", "BUY NOW", "ADD TO CART"]

def fetch(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.text

def decide(text: str) -> tuple[str, list[str], list[str]]:
    low = text.lower()
    found_in  = [k for k in INSTOCK_KEYWORDS if k.lower() in low]
    found_oos = [k for k in OOS_KEYWORDS     if k.lower() in low]

    # 보수 원칙: "입고" 키워드를 확실히 보지 못하면 품절로 간주
    if found_in and not found_oos:
        return "입고", found_in, found_oos
    if found_oos:
        return "품절", found_in, found_oos
    # 키워드가 아무것도 안 보이면 기본을 품절로
    return "품절", found_in, found_oos

if __name__ == "__main__":
    try:
        html_m = fetch(MOBILE_URL)
        html_d = fetch(DESKTOP_URL)
        soup = BeautifulSoup(html_m + "\n" + html_d, "lxml")
        text = soup.get_text(" ", strip=True)

        status, found_in, found_oos = decide(text)
        # GitHub Actions와 연동되는 단 한 줄 출력 (입고/품절/모니터링 문제)
        print(status)

        # 디버그 정보는 로그 파일로만 남김
        with open("last_check_debug.txt", "w", encoding="utf-8") as f:
            f.write(
                f"status={status}\n"
                f"found_in={found_in}\n"
                f"found_oos={found_oos}\n"
                f"mobile_len={len(html_m)}, desktop_len={len(html_d)}\n"
            )
    except Exception as e:
        print("모니터링 문제")
        with open("last_check_debug.txt", "w", encoding="utf-8") as f:
            f.write(f"error={repr(e)}\n")
