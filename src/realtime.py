# -*- coding: utf-8 -*-

import datetime
import json
import time
import requests
import sys

from proxy import get_proxies
from csv_reader import twse

SESSION_URL = "http://mis.twse.com.tw/stock/index.jsp"
STOCKINFO_URL = "http://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch={stock_id}&_={time}"

# Toggle for mock data
mock = False


def fetch_session():
    """Establish a session for requests."""
    session = requests.Session()
    session.get(SESSION_URL, proxies=get_proxies())
    return session


def format_stock_info(data) -> dict:
    """Format stock information into a structured dictionary."""
    result = {
        "timestamp": int(data["tlong"]) / 1000,
        "info": {
            "code": data["c"],
            "channel": data["ch"],
            "name": data["n"],
            "fullname": data["nf"],
            "time": datetime.datetime.fromtimestamp(int(data["tlong"]) / 1000).strftime("%Y-%m-%d %H:%M:%S"),
        },
        "realtime": {
            "latest_trade_price": data.get("z"),
            "trade_volume": data.get("tv"),
            "accumulate_trade_volume": data.get("v"),
            "best_bid_price": split_best(data.get("b")),
            "best_bid_volume": split_best(data.get("g")),
            "best_ask_price": split_best(data.get("a")),
            "best_ask_volume": split_best(data.get("f")),
            "open": data.get("o"),
            "high": data.get("h"),
            "low": data.get("l"),
        },
        "success": True,
    }
    return result


def split_best(d):
    """Split best bid/ask data."""
    return d.strip("_").split("_") if d else d


def join_stock_id(stocks) -> str:
    """Join stock identifiers into a string for the request."""
    if isinstance(stocks, list):
        return "|".join([f"{('tse' if s in twse else 'otc')}_{s}.tw" for s in stocks])
    return f"{('tse' if stocks in twse else 'otc')}_{stocks}.tw"


def get_raw(stocks) -> dict:
    """Fetch raw stock data from the API."""
    try:
        session = fetch_session()
        response = session.get(STOCKINFO_URL.format(stock_id=join_stock_id(stocks), time=int(time.time()) * 1000))
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"rtmessage": str(e), "rtcode": "5002"}  # Network error
    except json.JSONDecodeError:
        return {"rtmessage": "json decode error", "rtcode": "5000"}


def get(stocks, retry=3):
    """Fetch and format stock information, with retry logic."""
    data = get_raw(stocks) if not mock else mock.get(stocks)
    data["success"] = False  # Initialize success flag

    # Handle JSON decode error
    if data.get("rtcode") == "5000" and retry:
        return get(stocks, retry - 1)

    # Check for empty response
    if "msgArray" not in data or not data["msgArray"]:
        data["rtmessage"] = "Empty Query."
        data["rtcode"] = "5001"
        return data

    # Return formatted stock data
    if isinstance(stocks, list):
        return {info["code"]: format_stock_info(info) for info in data["msgArray"]}
    return format_stock_info(data["msgArray"][0])


def run(argv):
    """Main function to execute the script."""
    stock_id = argv[0]
    realtime_stock_info = get(stock_id)
    print(realtime_stock_info)

    # Example
    # {'timestamp': 1728628200.0, 'info': {'code': '2330', 'channel': '2330.tw', 'name': '台積電', 'fullname': '台灣積體電路製造股份有限公司', 'time': '2024-10-11 14:30:00'}, 'realtime': {'latest_trade_price': '1045.0000', 'trade_volume': '3396', 'accumulate_trade_volume': '42848', 'best_bid_price': ['1045.0000', '1040.0000', '1035.0000', '1030.0000', '1025.0000'], 'best_bid_volume': ['694', '1050', '1103', '919', '869'], 'best_ask_price': ['1050.0000', '1055.0000', '1060.0000', '1065.0000', '1070.0000'], 'best_ask_volume': ['7657', '3342', '2452', '956', '1078'], 'open': '1025.0000', 'high': '1050.0000', 'low': '1020.0000'}, 'success': True}
   

# if __name__ == "__main__":
#     run(sys.argv)

 