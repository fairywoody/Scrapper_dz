import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import os


def get_usd_rate_cbr():
    try:
        url = 'https://www.cbr.ru/scripts/XML_daily.asp'

        response = requests.get(url)
        response.encoding = 'utf-8'

        soup = BeautifulSoup(response.text, 'xml')

        usd = soup.find('CharCode', string='USD').find_parent('Valute')

        if usd:
            rate = usd.Value.text.replace(',', '.')
            nominal = usd.Nominal.text

            usd_rate = float(rate) / float(nominal)

            result = {
                'currency': 'USD/RUB',
                'rate': round(usd_rate, 2),
                'source': 'ЦБ РФ',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            return result
        else:
            return None

    except Exception as e:
        print(f"Ошибка: {e}")
        return None


def save_to_csv(data, filename="usd_rate.csv"):
    try:
        file_exists = os.path.isfile(filename)

        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            if not file_exists:
                writer.writerow(['Дата', 'Время', 'Курс USD/RUB'])

            date_part = data['timestamp'].split()[0]
            time_part = data['timestamp'].split()[1]

            writer.writerow([date_part, time_part, data['rate']])

        print(f"Курс {data['rate']} сохранен в {filename}")
        return True
    except Exception as e:
        print(f"Ошибка: {e}")
        return False


if __name__ == "__main__":
    rate_data = get_usd_rate_cbr()

    if rate_data:
        print(f"Курс USD/RUB: {rate_data['rate']}")
        print(f"Время: {rate_data['timestamp']}")

        save_to_csv(rate_data)
    else:
        print("Не удалось получить курс")