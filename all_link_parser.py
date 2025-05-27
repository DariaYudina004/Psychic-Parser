import re
import requests  #для работы с запросами через реквест происходит обращение на сайт и уже от туда вытягиваются все даннве
from bs4 import BeautifulSoup #библиотека разбивает html страницу, делает из нее объекты с которыми мы дальше и будем работать
import csv # создает csv файл

import random
import time

CSV = 'links_to_separation_anxiety_info.csv'
HOST = 'https://www.psychforums.com/forum.html' # домен, который мы парсим
URL = 'https://www.psychforums.com/separation-anxiety/' #точный адрес страницы
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

#response = requests.get('https://www.psychforums.com/separation-anxiety/', cookies=cookies, headers=HEADERS)

#session = requests.Session()
#session.headers.update(HEADERS)

def get_html(url, params= ''): #создаем функцию которая возвращает значения из хтмл вводится туда в первую очередь url, параметры это то, как функция будет искать нужные данные
    response = requests.get(url, headers = HEADERS, cookies=cookies, params = params)
    return response

def get_content(html, page): #полусение конкретной информации в зависимости от того, какие параметры мы ввели в предыдущую функцию и что нам вернули
   soup = BeautifulSoup(html, 'html.parser') #создаем объект c входными данными
   items = soup.find_all('li', class_=re.compile(r'^row bg')) # минус 3 часа моей жизни
   links_to_separation_anxiety_info = []

   for item in items:
       dt_element = item.find('dl', class_='icon')
       if dt_element:
           a_tag = dt_element.find('a')
           if a_tag:
               data_href = a_tag.get('href')
               links_to_separation_anxiety_info.append({'link_separation_anxiety': data_href})
           else:
               # Обработка случая, когда <a> не найден
               links_to_separation_anxiety_info.append({'link_separation_anxiety': None})
       else:
           # Обработка случая, когда <dt> не найден
           links_to_separation_anxiety_info.append({'link_separation_anxiety': None})

   return links_to_separation_anxiety_info

def save_document(items, path):
   with open(path, 'w', newline='') as file:
       writer = csv.writer(file, delimiter= ';')
       writer.writerow(['Ссылка на страницу со всей инфой'])
       for item in items:
           writer.writerow([item['link_separation_anxiety']])

def parser():
   PAGENATION = input('Укажите количество страниц для парсинга: ')
   PAGENATION = int(PAGENATION.strip())
   html = get_html(URL)
   links_to_separation_anxiety_info = []
   if html.status_code == 200:
       for page in range(1, PAGENATION + 1):
           print(f'пошел парсинг. Страница: {page}' )
           #url = URL + f'/page-{page}'
           html = get_html(URL)
           links_to_separation_anxiety_info.extend(get_content(html.text, page))
           print(links_to_separation_anxiety_info)
           time.sleep(random.uniform(1, 3))
       print(links_to_separation_anxiety_info)
       print('Парсинг закончен')
   else:
       print('Error')
   if links_to_separation_anxiety_info:
       save_document(links_to_separation_anxiety_info, CSV)

parser()
