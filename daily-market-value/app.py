# -*- coding:utf-8 -*- 
import requests
import time
import telegram
import asyncio
import os

from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
chat_id = os.getenv('TELEGRAM_CHANNEL_ID_REPORT_ALARM')
token = os.getenv('TELEGRAM_BOT_TOKEN_REPORT_ALARM_SECRET')
itooza_api = os.getenv('itooza_api')

# 가공없이 텍스트를 발송합니다.
async def sendMarkDownText(token, chat_id, sendMessageText): 
    time.sleep(1)
    bot = telegram.Bot(token = token)
    await bot.sendMessage(chat_id = chat_id, text = sendMessageText, disable_web_page_preview = True, parse_mode = "Markdown")


def parse_decimal(element):
    """숫자와 소수를 결합하여 하나의 float 값으로 반환"""
    if not element:
        return 0.0
    # 정수 부분 추출
    integer_element = element.select_one("strong")
    integer_part = integer_element.get_text(strip=True).replace(",", "") if integer_element else "0"

    # 소수 부분 추출
    decimal_element = element.select_one(".decimal")
    decimal_part = decimal_element.get_text(strip=True) if decimal_element else ""

    # 정수와 소수를 결합하여 변환
    return float(f"{integer_part}{decimal_part}")

def extract_market_data(item):
    """마켓 데이터를 추출하여 포맷팅"""
    name = item.select_one(".name").get_text(strip=True)
    value = parse_decimal(item.select_one(".index-vlaue"))
    change_value = parse_decimal(item.select_one(".index-range .stock-up, .index-range .stock-down"))
    change_rate = parse_decimal(item.select_one(".index-rate .stock-up, .index-rate .stock-down"))

    change_type = "📈" if "stock-up" in item.select_one(".index-range span").get("class", []) else "📉"
    change_str = f"{change_type} {change_value:.2f} ({change_rate:.2f}%)"

    # PER, PBR, ROE 정보는 코스피 및 코스닥만 출력
    per_info = ""
    if name in ["코스피", "코스닥"]:
        per = parse_decimal(item.select_one(".per .market-value"))
        pbr = parse_decimal(item.select_one(".pbr .market-value"))
        roe = item.select_one(".roe .market-value strong")
        roe = roe.get_text(strip=True) if roe else "N/A"
        per_info = f"\nPER: {per:.2f} | PBR: {pbr:.2f} | ROE: {roe}"

    return f"======={name}=======\n지수: {value:.2f} {change_str}{per_info}"


async def main():
    sendMessageText = ''
    url = itooza_api

    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # 마켓 데이터 추출
    market_items = soup.select(".section-market .data-group .data-item")
    market_data = [extract_market_data(item) for item in market_items]

    # 날짜 정보 추출
    date_elements = soup.select(".date-reference .date-item")
    date_info = "\n".join([f"{item.select_one('.title').get_text(strip=True)}: {item.select_one('.date').get_text(strip=True)}" for item in date_elements])

    # 메시지 구성
    sendMessageText += f"*오늘의 마켓 데이터*\n\n"
    sendMessageText += f"*=======산출 기준 일자=======*\n\n"
    
    sendMessageText += f"{date_info}\n\n"
    
    for data in market_data:
        sendMessageText += data + "\n\n"

    print(sendMessageText)
    if sendMessageText:
        await sendMarkDownText(token=token,
                chat_id=chat_id,
                sendMessageText=sendMessageText)

if __name__ == "__main__":
    asyncio.run(main())
