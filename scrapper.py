import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import os
import time
from pathlib import Path


def get_usd_rate_cbr():
    try:
        url = 'https://www.cbr.ru/scripts/XML_daily.asp'

        response = requests.get(url, timeout=10)
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
            print(f"{datetime.now()}: USD не найден в ответе ЦБ")
            return None

    except requests.exceptions.RequestException as e:
        print(f"{datetime.now()}: Ошибка сети: {e}")
        return None
    except Exception as e:
        print(f"{datetime.now()}: Ошибка: {e}")
        return None


def save_to_csv(data, filename="usd_rate.csv"):
    try:
        Path("logs").mkdir(exist_ok=True)
        filepath = os.path.join("logs", filename)

        file_exists = os.path.isfile(filepath)

        with open(filepath, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=',')

            if not file_exists:
                writer.writerow(['Дата', 'Время', 'Курс USD/RUB', 'Timestamp'])

            date_part = data['timestamp'].split()[0]
            time_part = data['timestamp'].split()[1]

            rate_value = data['rate'] if data['rate'] != 'ERROR' else 'Ошибка'

            writer.writerow([date_part, time_part, rate_value, data['timestamp']])

        print(f"{datetime.now()}: Курс {data['rate']} сохранен в {filepath}")

        return True
    except Exception as e:
        print(f"{datetime.now()}: Ошибка сохранения: {e}")
        return False


def collect_rate():
    print(f"\n{datetime.now()}: Запуск сбора данных...")
    rate_data = get_usd_rate_cbr()

    if rate_data:
        print(f"Курс USD/RUB: {rate_data['rate']}")
        print(f"Время: {rate_data['timestamp']}")
        save_to_csv(rate_data)
    else:
        print("Не удалось получить курс")
        failed_data = {
            'rate': 'ERROR',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        save_to_csv(failed_data)


def collection(duration_hours=48, interval_hours=1):

    print(f"=== НАЧАЛО СБОРА ДАННЫХ (простой метод) ===")
    print(f"Дата старта: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Длительность: {duration_hours} часов")
    print(f"Интервал: {interval_hours} час(а/ов)")
    print("=" * 50)

    start_time = time.time()
    end_time = start_time + (duration_hours * 3600)
    iteration = 0

    while time.time() < end_time:
        iteration += 1
        print(f"\n--- Итерация #{iteration} ---")

        collect_rate()

        next_run_time = time.time() + (interval_hours * 3600)

        if next_run_time > end_time:
            print("Достигнут лимит времени сбора")
            break

        wait_seconds = interval_hours * 3600
        print(f"Ожидание {interval_hours} час(а/ов) до следующего сбора...")

        for i in range(wait_seconds):
            if time.time() + (wait_seconds - i) > end_time:
                print("Прерывание ожидания: достигнут лимит времени")
                break
            if i % 3600 == 0 and i > 0:
                hours_left = (wait_seconds - i) // 3600
                print(f"Осталось ждать: {hours_left} часов")
            time.sleep(1)

        print("Продолжаем сбор...")

    print(f"\n=== СБОР ДАННЫХ ЗАВЕРШЕН ===")
    print(f"Дата окончания: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Всего выполнено итераций: {iteration}")

if __name__ == "__main__":
    DURATION_HOURS = 48
    INTERVAL_HOURS = 1

    collection(DURATION_HOURS, INTERVAL_HOURS)
