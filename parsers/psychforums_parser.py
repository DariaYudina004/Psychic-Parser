import re
import requests  #для работы с запросами через реквест происходит обращение на сайт и уже от туда вытягиваются все даннве
from bs4 import BeautifulSoup #библиотека разбивает html страницу, делает из нее объекты с которыми мы дальше и будем работать
import csv # создает csv файл

import random
import time

CSV = 'ALL_LINKS.csv'
BAD_CSV = 'BAD_OF_ALL_LINKS.csv'
HOST = 'https://www.psychforums.com/forum.html' # домен, который мы парсим
URLS = [] #точный адрес страницы
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
   ALL_LINKS = []


   for item in items:
       dt_element = item.find('dl', class_='icon')
       if dt_element:
           a_tag = dt_element.find('a')
           if a_tag:
               data_href = a_tag.get('href')
               print(data_href)
               ALL_LINKS.append({'ALL_LINKS_of_psihi': data_href})
           else:
               # Обработка случая, когда <a> не найден
               ALL_LINKS.append({'ALL_LINKS_of_psihi': None})
       else:
           # Обработка случая, когда <dt> не найден
           ALL_LINKS.append({'ALL_LINKS_of_psihi': None})

   return ALL_LINKS

def save_document(items, path):
   with open(path, 'w', newline='') as file:
       writer = csv.writer(file, delimiter= ';')
       writer.writerow(['Ссылка на страницу со всей инфой'])
       for item in items:
           writer.writerow([item['ALL_LINKS_of_psihi']])

def save_bad_document(items, path):
   with open(path, 'w', newline='') as file:
       writer = csv.writer(file, delimiter= ';')
       writer.writerow(['Ломанные ссылки'])
       for item in items:
           writer.writerow([item])


def read_from_document():
    with open(r'D:\Documents\GitHub\Psychic-Parser\main_links.csv', 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader) # 'Это чтоб заголовок пропускать, а то получается у первого ошибка из-за того, что ему передают текст, а не ссылку
        for row in reader:
            URLS.append(row)


def parser():
   read_from_document()
   all_links_info = []
   error_links = []
   base_url = None
   for url in range(len(URLS)):
       try:
           base_url = URLS[url][0]
           html = get_html(base_url)
           soup = BeautifulSoup(html.text, 'html.parser')
           counts = soup.find('div', class_='pagination').find('a').find_all('strong')
           PAGENATION = int(counts[1].get_text())
           for page in range(PAGENATION):
               if page == 0:
                   current_url = base_url
               else:
                   current_url = f"{base_url}/page{page * 40}.html"
               print(f'Парсим страницу: {current_url}')
               html_page = get_html(current_url)
               if html_page.status_code != 200:
                   print(f'Ошибка при загрузке {current_url}')
                   error_links.append(base_url)
                   print(error_links)
                   break  # выходим, если страница не загрузилась
               # Обрабатываем текущую страницу
               all_links_info.extend(get_content(html_page.text, current_url))
               save_document(all_links_info, CSV)
               time.sleep(random.uniform(1, 3))
       except Exception as e:
           print(f'У меня нет времени на ошибки. Я должен работать {base_url}: {e}')
           continue

   print(all_links_info)
   print('Парсинг закончен')

   save_bad_document(error_links, BAD_CSV)

parser()
