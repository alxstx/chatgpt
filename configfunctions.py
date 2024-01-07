import urllib.request
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import telebot
from telebot import types
import sqlite3
from selenium.webdriver.common.by import By
import time
import pyshorteners

verbot_list = ['<', '{', '@id', '"name":', '"headline":', '"description":', '/images/' '"shareUrl":', '"browserTitle":',
               '(R-G-B)', 'env.', '[Bearbeiten | Quelltext bearbeiten]', '中文日本語한국어', '.css("display", "none")']


def create_driver():
    # Selenium Driver erstellen
    driver = webdriver.Safari()
    return driver


def get_html(url, driver):
    # Html code einer seite erhalten
    try:
        driver.get(url)
        html = driver.page_source
    except:
        html = ''
        pass
    return html


def create_bot(token):
    # bot erstellen
    bot = telebot.TeleBot(token)
    return bot


def create_database():
    #datenbank erstellen
    save = sqlite3.connect('Chatgpt.db')
    mycursor = save.cursor()
    mycursor.execute(
        "CREATE TABLE websites (id INT websiteid PRIMARY KEY, url VARCHAR(255))")
    return mycursor, save


def connect_with_database():
    # mit datenbank verbinden
    save2 = sqlite3.connect('Chatgpt.db')
    mycursor = save2.cursor()
    return mycursor, save2


def first_filter(text, suchwort):
    # aussortieren von wörtern und phrasen
    trueorfalse = True
    if suchwort in text:
        for v in verbot_list:
            if v in text:
                trueorfalse = False
    else:
        trueorfalse = False
    if text.count(' ') <= 2:
        trueorfalse = False
    return trueorfalse





def divide_string(long, n):
    # bei zu langem text ihn aufteilen
    dividedlist = []
    length = len(long)
    chars = int(length / n)
    for i in range(0, length, chars):
        part = long[i: i + chars]
        dividedlist.append(part)
    return dividedlist


def shortener(url):
    # bei zu langem url link ihn verkürzen
    type_tiny = pyshorteners.Shortener()
    short_url = type_tiny.tinyurl.short(url)
    return short_url


bot = telebot.TeleBot('6691864205:AAHu7AU6hv1oNHEJwqXXRDMQ6EOvl-pJcts')
welcometext = """ Willkommen zur neuen Version von ChatGpt!
Hier können sie ihr gewünschtes Suchworte oder Suchphrase eingeben
und wir werden für die benötigten Informationen dazu finden und mit einer
Quellenausgabe angeben. Für Start geben sie bitte den Befehl /new ein"""
newtext = """Geben sie das Wort ein zu dem sie gerne Informationen wissen würden und wir
suchen den für sie raus"""
