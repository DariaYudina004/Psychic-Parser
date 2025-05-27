import csv
import time
import random
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# Укажите путь к драйверу Chrome
driver = webdriver.Chrome(executable_path='/drivers/chromedriver/chromedriver.exe')

userAgent = UserAgent()
options = webdriver.ChromeOptions()
options.add_argument(f"user-agent={userAgent.random}") #Тут у нас вопрос с User Agent


# URL страницы (пример)
url = 'ваша_страница_с_сообщениями'
driver.get(url)
time.sleep(3)

# Создаем список для хранения данных сообщений
posts_data = []

# Находим все сообщения на странице
messages = driver.find_elements(By.CSS_SELECTOR, 'article.message.message--post')

for msg in messages:
    try:
        # Имя пользователя
        username_element = msg.find_element(By.CSS_SELECTOR, 'h4.message-name span.username')
        username = username_element.text.strip()
    except NoSuchElementException:
        username = 'NULL'

    try:
        # Дата публикации
        date_element = msg.find_element(By.CSS_SELECTOR, 'time.u-dt')
        date_posted = date_element.get_attribute('datetime')  # ISO формат или можно взять текст
    except NoSuchElementException:
        date_posted = 'NULL'

    try:
        # Расположение пользователя (если есть)
        location_element = msg.find_element(By.CSS_SELECTOR, 'div.message-userExtras dl.pairs--justified dd')
        # Проверяем, что это именно расположение (может потребоваться более точный селектор)
        location_text = location_element.text.strip()
    except NoSuchElementException:
        location_text = 'NULL'

    try:
        # Текст сообщения
        content_element = msg.find_element(By.CSS_SELECTOR, 'div.message-userContent div.bbWrapper')
        message_text = content_element.text.strip()
    except NoSuchElementException:
        message_text = 'NULL'


    # Можно добавить сбор тегов или других данных по необходимости

    # Собираем все в словарь
    post_info = {
        'Имя': username,
        'Дата публикации': date_posted,
        'Расположение': location_text,
        'Сообщение': message_text,
    }

    posts_data.append(post_info)

# Сохраняем в CSV файл
with open('posts.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=posts_data[0].keys())
    writer.writeheader()
    writer.writerows(posts_data)

driver.quit()