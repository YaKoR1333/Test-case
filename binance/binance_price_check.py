import requests
import json
import time
import threading

high_price = 0


def get_price() -> float:
    response = requests.get(url="https://api2.binance.com/api/v3/ticker/price?symbol=XRPUSDT")
    response_data = json.loads(response.text)
    return round(float(response_data['price']), 4)


def update_max_price_per_hour():
    global high_price
    threading.Timer(3600, update_max_price_per_hour).start()
    high_price = get_price()
    return print('Установлена новая пиковая цена за час')


def main():
    global high_price
    update_max_price_per_hour()
    while True:
        current_price = get_price()
        if current_price > high_price:
            high_price = current_price
        elif high_price - current_price >= high_price * 0.01:
            print('Цена упала на 1% или более')
        time.sleep(0.1)


if __name__ == '__main__':
    main()
