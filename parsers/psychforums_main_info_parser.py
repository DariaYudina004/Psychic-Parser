import time
import re
import random

import requests  #для работы с запросами через реквест происходит обращение на сайт и уже от туда вытягиваются все даннве
from bs4 import BeautifulSoup #библиотека разбивает html страницу, делает из нее объекты с которыми мы дальше и будем работать
import csv # создает csv файл

CSV = 'all_main_info_about_separation_anxiety.csv'
BAD_CSV = 'bad_link_separation_anxiety.csv'
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
    # 'Cookie': 'phpbb3_qazi1_u=1; phpbb3_qazi1_k=; _ga=GA1.1.1645495216.1748295818; phpbb3_qazi1_sid=35a8027a79b1f67be3dd2e7d241254c4; style_cookie=null; _ga_Q5QXM942NE=GS2.1.s1748338984$o3$g1$t1748340067$j0$l0$h0',

    # Можно добавить cookies или другие заголовки, если нужно
} #обновляем заголовки, чтобы сайт не понял, что мы скрипт

cookies = {
    'phpbb3_qazi1_u': '1',
    'phpbb3_qazi1_k': '',
    '_ga': 'GA1.1.1645495216.1748295818',
    'phpbb3_qazi1_sid': '35a8027a79b1f67be3dd2e7d241254c4',
    'style_cookie': 'null',
    '_ga_Q5QXM942NE': 'GS2.1.s1748338984$o3$g1$t1748340067$j0$l0$h0',
}
 #обновляем заголовки, чтобы сайт не понял, что мы скрипт
URLS = []

def get_html(url, params= ''): #создаем функцию которая возвращает значения из хтмл вводится туда в первую очередь url, параметры это то, как функция будет искать нужные данные
    response = requests.get(url, headers = HEADERS, cookies=cookies, params = params)
    return response

def get_content(html,url): #полусение конкретной информации в зависимости от того, какие параметры мы ввели в предыдущую функцию и что нам вернули
    soup = BeautifulSoup(html, 'html.parser') #создаем объект c входными данными
    items = soup.find_all('div', class_=re.compile(r"^post bg")) # Еще два часа моей жизни
    information_about_separation_anxiety = []
    forum_themes = soup.find('div', id="page-footer").find('li', class_="icon-home").find_all('a')
    #print(items)
    #print(information_about_separation_anxiety)
    #print(forum_themes)
    # выносим все эдементы из аппента ибо я замаялась исправлять ошибки
    for item in items:
        #print(item)
        try:
            main_theme = forum_themes[2]
            second_theme = forum_themes[3]
            last_theme = forum_themes[4] if len(forum_themes) >= 4 else 'NULL'
            title = item.find('h1')
            text = item.find('div', class_='content')
            date =  item.find('div', class_='author')
            id_user = item.find('dl', class_='postprofile')
            count_messages = item.find_all('dd')
            count_messages_value = 0
            for dd in count_messages:
                count_text = dd.get_text(strip=True)
                if 'Сообщений' in count_text:
                    match = re.search(r'\d+', count_text)
                    if match:
                        count_messages_value = int(match.group())
                        break

            information_about_separation_anxiety.append(
                {
                    'main_theme' : main_theme.get_text(strip=True) if main_theme else 'NULL',
                    'second_theme': second_theme.get_text(strip=True) if second_theme else 'NULL',
                    'last_theme': last_theme.get_text(strip=True) if last_theme else 'NULL',
                    'title': title.get_text(strip=True) if title else 'NULL',
                    'text': text.get_text(strip=True) if text else 'NULL',
                    'date': date.find('span').get_text(strip=True) if date else 'NULL',
                    'id_user': id_user.get('id') if id_user else 'NULL',
                    'count_messages_value': count_messages_value
                }
            )
            #print(information_about_separation_anxiety)
        except Exception as e:
            print(f"Ошибка при обработке элемента на странице {url}: {e}")
            continue

    return information_about_separation_anxiety

def save_document(items, path):
    with open(path, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter= ';')
        for item in items:
            writer.writerow([item['main_theme'],item['second_theme'],item['last_theme'], item['title'], item['text'], item['date'], item['id_user'], item['count_messages_value']])

def save_bad_document(items, path):
   with open(path, 'w', newline='') as file:
       writer = csv.writer(file, delimiter= ';')
       writer.writerow(['Ломанные ссылки'])
       for item in items:
           writer.writerow([item['bad_link_separation_anxiety']])


def read_from_document():
    with open(r'D:\Documents\GitHub\Psychic-Parser\links_to_separation_anxiety_info.csv', 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader) # 'Это чтоб заголовок пропускать, а то получается у первого ошибка из-за того, что ему передают текст, а не ссылку
        for row in reader:
            URLS.append(row)

def parser():
    read_from_document()
    #print(f"Всего ссылок для обработки: {len(URLS)}")
    information_about_separation_anxiety = []
    error_links = []
    for url in range(len(URLS)):
        try:
            html = get_html(URLS[url][0])
            if html.status_code == 200:
                #print(url)
                print(f'Пошла жара. Сысыслка номер: {URLS[url][0]}')
                information_about_separation_anxiety.extend(get_content(html.text,url ))
                print(information_about_separation_anxiety)
            else:
                print('Ерроре')
                error_links.append(URLS[url][0])
                print(error_links)

        except Exception as e:
            print(f'У меня нет времени на ошибки. Я должен работать {URLS[url]}: {e}')
            continue
        time.sleep(random.uniform(1, 3))
    print(information_about_separation_anxiety)
    print('Парсинг закончен')
    save_document(information_about_separation_anxiety, CSV)
    save_bad_document(error_links, BAD_CSV)
parser()