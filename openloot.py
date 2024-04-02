from curl_cffi import requests
from dotenv import load_dotenv
import os

load_dotenv()

headers = {
    "authority": "api.openloot.com",
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9",
    "content-type": "application/json",
    "cookie": os.getenv("COOKIE"),
    "origin": "https://openloot.com",
    "sec-ch-ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "X-Client-Id:": "marketplace",
    "X-Device-Id": os.getenv("X-DEVICE-ID"),
    "X-Is-Mobile": "false",
    "X-Session-Id": os.getenv("X-SESSION-ID"),
    "X-User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
}


def move_items_to_market(items, timeout=3):
    url = f"https://api.openloot.com/v2/market/items/actions/move"
    data = {
        "to": "unlocked",
        "itemIds": items
    }
    r = requests.post(
        url,
        headers=headers,
        json=data,
        impersonate="chrome120",
        timeout=timeout,
    )
    return r


def get_in_game_items(page=1, timeout=3):
    url = f"https://api.openloot.com/v2/market/items/in-game?gameId=56a149cf-f146-487a-8a1c-58dc9ff3a15c&nftTags=NFT.Hourglass&page={page}&pageSize=1000&sort=name%3Aasc"
    r = requests.get(
        url,
        headers=headers,
        impersonate="chrome120",
        timeout=timeout,
    )
    return r
