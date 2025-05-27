import random
import requests
from bs4 import BeautifulSoup
import csv
import time

CSV = 'links_to_Anxiety_info.csv'
HOST = 'https://www.mentalhealthforum.net'
BASE_URL = 'https://www.mentalhealthforum.net/forum/forums/anxiety-forum.365/'
HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}

def get_html(url, params=None, retries=3, delay=2):
    """
    Получает HTML страницу с повторными попытками в случае ошибок.
    """
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, params=params)
            if response.status_code == 200:
                return response
            else:
                print(f"Ошибка {response.status_code} при запросе {url}")
        except requests.RequestException as e:
            print(f"RequestException: {e}")
        print(f"Повторная попытка через {delay} секунд...")
        time.sleep(delay)
    return None

def parse_links(html_content):
    """
    Парсит ссылки на страницы баров из HTML контента.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    # В зависимости от страницы может понадобиться менять класс
    items = soup.find_all('div', class_='structItemContainer-group js-threadList')
    links = []

    for item in items:
        name_div = item.find('div', class_='structItem-title')
        if name_div and name_div.find('a'):
            href = name_div.find('a').get('data-href')
            full_link = HOST + href
            links.append({'Anxiety': full_link})
        else:
            print("Не удалось найти ссылку в элементе:", item)
    return links

def save_to_csv(data, filename):
    """
    Сохраняет список словарей в CSV файл.
    """
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Ссылка на страницу со всей инфой'])
        for row in data:
            writer.writerow([row['link_Anxiety']])

def main():
    while True:
        try:
            total_pages = int(input('Укажите количество страниц для парсинга: ').strip())
            if total_pages <= 0:
                print("Пожалуйста, введите положительное число.")
                continue
            break
        except ValueError:
            print("Некорректный ввод. Пожалуйста, введите число.")

    all_links = []

    for page in range(2, total_pages + 1):
        print(f'Парсинг страницы {page}...')
        params = {'page-': page}  # если сайт использует параметры GET для пагинации
        # Если пагинация реализована через URL (например /page/2), используйте URL с добавлением номера страницы
        url = BASE_URL
        response = get_html(url, params=params)
        if response and response.status_code == 200:
            links = parse_links(response.text)
            all_links.extend(links)
            print(f'Найдено {len(links)} ссылок на странице {page}.')
        else:
            print(f'Не удалось получить страницу {page}. Продолжаем...')
        time.sleep(random.uniform(1, 3))  # чтобы не нагружать сервер

    save_to_csv(all_links, CSV)
    print(f'Парсинг завершен! Всего собранных ссылок: {len(all_links)}')

if __name__ == "__main__":
    main()