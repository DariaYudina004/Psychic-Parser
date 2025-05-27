import asyncio
import aiohttp
import time
import re
import random

from bs4 import BeautifulSoup
import csv

CSV = 'all_main_info.csv'
BAD_CSV = 'all_bad_link.csv'
HOST = 'https://www.psychforums.com/forum.html'
HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'cache-control': 'no-cache',
    'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

cookies = {
    'phpbb3_qazi1_u': '1',
    'phpbb3_qazi1_k': '',
    '_ga': 'GA1.1.1645495216.1748295818',
    'phpbb3_qazi1_sid': '35a8027a79b1f67be3dd2e7d241254c4',
    'style_cookie': 'null',
    '_ga_Q5QXM942NE': 'GS2.1.s1748338984$o3$g1$t1748340067$j0$l0$h0',
}

URLS = []


# Асинхронная функция для получения HTML
async def get_html(session, url):
    try:
        async with session.get(url, headers=HEADERS, cookies=cookies) as response:
            return response.status, await response.text()
    except Exception as e:
        print(f"Ошибка при запросе {url}: {e}")
        return None, None


# Асинхронная функция для парсинга одной страницы
async def parse_page(session, url):
    status, html_text = await get_html(session, url)
    if status != 200 or html_text is None:
        return None, url  # Возвращаем ошибку и ссылку
    return get_content(html_text, url), None


def get_content(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find('div', id='page-body').find('h1')
    items = soup.find_all('div', class_=re.compile(r"^post bg"))
    all_main_info = []
    forum_themes = soup.find('div', id="page-footer").find('li', class_="icon-home").find_all('a')

    for item in items:
        try:
            main_theme = forum_themes[2]
            second_theme = forum_themes[3]
            last_theme = forum_themes[4] if len(forum_themes) >= 5 else None
            text_div = item.find('div', class_='content')
            date_p = item.find('p', class_='author')
            if date_p:
                full_text = date_p.get_text(separator=' ', strip=True)
                parts = full_text.split('»')
                date_str = parts[1].strip() if len(parts) > 1 else "NULL"
            else:
                date_str = "NULL"

            id_user_tag = item.find('dl', class_='postprofile')
            messages_tags = id_user_tag.find_all('dd') if id_user_tag else []
            count_messages = messages_tags[2].get_text().replace('Posts: ', '') if len(messages_tags) >= 3 else "NULL"

            all_main_info.append({
                'main_theme': main_theme.get_text(strip=True) if main_theme else 'NULL',
                'second_theme': second_theme.get_text(strip=True).replace(' Forum', '') if second_theme else 'NULL',
                'last_theme': last_theme.get_text(strip=True) if last_theme else 'NULL',
                'title': title.get_text(strip=True) if title else 'NULL',
                'text': text_div.get_text(strip=True) if text_div else 'NULL',
                'date': date_str,
                'id_user': id_user_tag.get('id') if id_user_tag else 'NULL',
                'count_messages': count_messages
            })
        except Exception as e:
            continue
    return all_main_info


def save_document(items, path):
    with open(path, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        for item in items:
            writer.writerow(
                [item['main_theme'], item['second_theme'], item['last_theme'], item['title'], item['text'], item['date'],
                item['id_user'], item['count_messages']])


def save_bad_document(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Ломанные ссылки'])
        for link in items:
            writer.writerow([link])


def read_from_document():
    global URLS
    with open(r'D:\Documents\GitHub\Psychic-Parser\parsers\info_about_separation_anxiety.csv', 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader)
        URLS.extend([row for row in reader])


async def main():
    read_from_document()

    error_links = []
    all_main_info = []

    async with aiohttp.ClientSession() as session:
        tasks = []
        for idx, row in enumerate(URLS):
            url_link = row[0]
            task = asyncio.create_task(parse_page(session, url_link))
            tasks.append((task, url_link))

        for idx, (task, link) in enumerate(tasks):
            try:
                result_content, error_url = await task
                percent_done = ((idx + 1) / len(tasks)) * 100
                print(f"Обработано {idx + 1} из {len(tasks)} ({percent_done:.2f}%)")

                if result_content is not None:
                    all_main_info.extend(result_content)
                    save_document(all_main_info, CSV)
                else:
                    print(f'Ошибка при обработке: {link}')
                    error_links.append(link)

            except Exception as e:
                print(f'Исключение при обработке {link}: {e}')
                error_links.append(link)

            # Можно оставить задержку или убрать для максимальной скорости
            await asyncio.sleep(random.uniform(1, 1.5))

    print('Парсинг завершен')
    save_bad_document(error_links, BAD_CSV)


if __name__ == '__main__':
    asyncio.run(main())