import asyncio
import aiohttp
import re
import csv
from bs4 import BeautifulSoup
import random

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

# Глобальный список URL для парсинга
URLS = []


async def get_html(session, url):
    try:
        async with session.get(url, headers=HEADERS, cookies=cookies) as response:
            if response.status == 200:
                return await response.text()
            else:
                print(f"Ошибка получения {url}: статус {response.status}")
                return None
    except Exception as e:
        print(f"Исключение при запросе {url}: {e}")
        return None


def parse_content(html, url_index):
    soup = BeautifulSoup(html, 'html.parser')
    all_main_info = []

    title = soup.find('div', id='page-body').find('h1')
    items = soup.find_all('div', class_=re.compile(r"^post bg"))
    forum_themes = soup.find('div', id="page-footer").find('li', class_="icon-home").find_all('a')

    for item in items:
        try:
            main_theme = forum_themes[2]
            second_theme = forum_themes[3]
            last_theme = forum_themes[4] if len(forum_themes) >= 5 else None

            text = item.find('div', class_='content')
            date_p = item.find('p', class_='author')
            if date_p:
                full_text = date_p.get_text(separator=' ', strip=True)
                parts = full_text.split('»')
                date_str = parts[1].strip() if len(parts) > 1 else "NULL"
            else:
                date_str = "NULL"

            id_user = item.find('dl', class_='postprofile')
            messages_dds = id_user.find_all('dd') if id_user else []
            count_messages_text = messages_dds[2].get_text() if len(messages_dds) > 2 else ''
            count_messages = count_messages_text.replace('Posts: ', '') if count_messages_text else "NULL"

            all_main_info.append({
                'main_theme': main_theme.get_text(strip=True) if main_theme else 'NULL',
                'second_theme': second_theme.get_text(strip=True).replace(' Forum', '') if second_theme else 'NULL',
                'last_theme': last_theme.get_text(strip=True) if last_theme else 'NULL',
                'title': title.get_text(strip=True) if title else 'NULL',
                'text': text.get_text(strip=True) if text else 'NULL',
                'date': date_str,
                'id_user': id_user.get('id') if id_user else 'NULL',
                'count_messages': count_messages
            })
        except Exception as e:
            # Можно логировать ошибку или пропускать
            continue

    return all_main_info


async def save_document(items, path):
    # Асинхронное сохранение файла не обязательно, можно оставить синхронным
    with open(path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        for item in items:
            writer.writerow([
                item['main_theme'],
                item['second_theme'],
                item['last_theme'],
                item['title'],
                item['text'],
                item['date'],
                item['id_user'],
                item['count_messages'],
            ])


async def save_bad_document(items, path):
    with open(path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Ломанные ссылки'])
        for link in items:
            writer.writerow([link])


def read_from_document():
    global URLS
    with open(r'D:\Documents\GitHub\Psychic-Parser\parsers\info_about_separation_anxiety.csv', newline='',
              encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        URLS.extend([row for row in reader])


async def main():
    read_from_document()
    async with aiohttp.ClientSession() as session:
        tasks = []
        total_links = len(URLS)

        for index, row in enumerate(URLS):
            url_link = row[0]
            task = asyncio.create_task(process_url(session, url_link, index, total_links))
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        # results - список из кортежей (all_main_info_list, error_link)
        all_data = []
        bad_links = []

        for res in results:
            data_part, error_link_part = res
            all_data.extend(data_part)
            bad_links.extend(error_link_part)

        await save_document(all_data, CSV)
        await save_bad_document(bad_links, BAD_CSV)


async def process_url(session, url_link, index, total):
    percent_done = ((index + 1) / total) * 100
    print(f"Обработка {index + 1}/{total} --- {percent_done}%: {url_link}")
    html_content = await get_html(session, url_link)

    error_links_local = []

    if html_content:
        try:
            data_items = parse_content(html_content, index)
            # Можно добавить задержку между запросами для имитации human-like поведения
            await asyncio.sleep(random.uniform(1, 2))
            return data_items, error_links_local
        except Exception as e:
            print(f"Ошибка при парсинге {url_link}: {e}")
            error_links_local.append(url_link)
            return [], error_links_local
    else:
        error_links_local.append(url_link)
        return [], error_links_local


if __name__ == '__main__':
    asyncio.run(main())