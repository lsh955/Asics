import requests
from bs4 import BeautifulSoup
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# 모니터링할 상품 URL (아식스 공식몰)
PRODUCT_URL = "https://asics.co.kr/p/AKR_112430207-002"

# Slack 설정
SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = "#stock-monitor"

def check_stock():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/114.0.0.0 Safari/537.36"
    }
    response = requests.get(PRODUCT_URL, headers=headers)
    if response.status_code != 200:
        return f"상품 페이지 요청 실패: {response.status_code}", False

    soup = BeautifulSoup(response.text, "html.parser")

    # 아식스 공식몰 기준 재고 문구 확인
    # (예: '품절' 또는 '일시품절' 텍스트를 찾아 상태 판단)
    if "품절" in soup.text or "일시품절" in soup.text:
        return "품절 상태입니다.", False
    else:
        return "재고가 있습니다!", True

def capture_screenshot(url, file_path="screenshot.png"):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(3)
    driver.save_screenshot(file_path)
    driver.quit()
    return file_path

def send_slack_message(message, file_path=None):
    client = WebClient(token=SLACK_TOKEN)
    try:
        if file_path:
            client.files_upload(
                channels=SLACK_CHANNEL,
                file=file_path,
                initial_comment=message
            )
        else:
            client.chat_postMessage(channel=SLACK_CHANNEL, text=message)
    except SlackApiError as e:
        print(f"Slack API 에러: {e.response['error']}")

if __name__ == "__main__":
    status_message, in_stock = check_stock()
    if in_stock:
        screenshot_path = capture_screenshot(PRODUCT_URL)
        send_slack_message(f"[재고 알림] {status_message}\n{PRODUCT_URL}", screenshot_path)
    else:
        send_slack_message(f"[재고 알림] {status_message}\n{PRODUCT_URL}")
