import csv
import time
import random
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# Укажите путь к драйверу Chrome
driver = webdriver.Firefox(executable_path='D:\Documents\GitHub\Psychic-Parser\firefoxdriver\geckodriver.exe')

userAgent = UserAgent()
options = webdriver.FirefoxOptions()
options.add_argument(f"user-agent={userAgent.random}") #Тут у нас вопрос с User Agent
