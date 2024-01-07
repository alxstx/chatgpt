from configfunctions import *

driver = create_driver()
quellen_list = []
count = 1
quellen_text = {}
no_list = []


def find_quellen(suchwort):
    # Finden von allen Quellen auf Google Startseite durch Eingabe des Suchworts in Google
    driver.get('https://www.google.com')
    anotherbut = driver.find_element_by_xpath('//*[@id="L2AGLb"]/div') # Umgehen der Cookies
    anotherbut.click()
    but = driver.find_element_by_xpath('/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]')
    time.sleep(1)
    but.click()
    but.send_keys(suchwort) # Eingabe des Suchworts
    but.send_keys(Keys.ENTER)
    time.sleep(3)
    qu = driver.find_elements_by_class_name('yuRUbf')

    for q in qu:
        quellen_list.append(q.find_element_by_tag_name('a').get_attribute('href')) # Finden von Seiten
        quellen_text[q.find_element_by_tag_name('a').get_attribute('href')] = []
    return quellen_list, quellen_text


def parsequellen(url, suchwort, quellen_text):
    # Geht die einzelnen Quellen durch und sucht die relevanten Infos zu dem Suchwort aus
    driver.get(url)
    time.sleep(3)
    texte = driver.find_elements_by_tag_name('p')
    for t in texte:
        if first_filter(t.text, suchwort):
            quellen_text[url].append(t.text)
    return quellen_text


def save_in_database(url):
    # Speichert die gute Quelle in der Datenbank
    curs, db = connect_with_database()
    count = get_count(curs)
    curs.execute("""INSERT INTO websites(id, url) 
                   VALUES (?,?);""", (count + 1, url))
    db.commit()
    db.close()


def get_data_fromdatabase(url):
    # Gibt die Quelle aus der Datenbank aus
    curs, db = connect_with_database()
    curs.execute('SELECT url FROM websites')
    result = curs.fetchall()
    db.close()
    return result


def get_count(curs):
    # Erstelle eine ID die sich immer um eins erhöht bei neuen Werten
    curs.execute('SELECT id FROM websites')
    ls = curs.fetchall()
    return ls[-1][-1]


@bot.message_handler(commands=['start'])
def start_text(message):
    # Bei der Command /start gibt er den Start Text aus
    bot.send_message(message.chat.id, welcometext)


@bot.message_handler(commands=['new'])
def start_text(message):
    # Bei der command /new fordert der Bot den User dazu auf ein Suchwort einzugeben
    bot.send_message(message.chat.id, newtext)


@bot.message_handler(content_types=['text'])
def answer(message):
    # Empfängt das Suchwort und gibt dem User Informationen zu dem Suchwort und der Phase des Prozesses aus
    time.sleep(2)
    bot.send_message(message.chat.id, 'Die Suche fängt an')
    time.sleep(3)
    quellen_list, quellen_text = find_quellen(message.text)
    for quelle in quellen_list:
        already = False
        urls = get_data_fromdatabase(quelle)
        endqul = parsequellen(quelle, message.text, quellen_text)
        if endqul[quelle] != []:
            for url in urls:
                if url[0] == shortener(quelle): # Überprüfen ob die Quelle schon gespeichert ist
                    bot.send_message(message.chat.id,
                                     'Wir haben folgende schon gespeicherte Quelle: ' + url[0] + ' mit folgender Information vorliegen: ')
                    quelle = url[0]
                    already = True
                    break
            if not already:
                if quelle not in no_list:
                    bot.send_message(message.chat.id,
                                     'Wir haben folgende Quelle: ' + quelle + ' mit folgender Information vorliegen: ')
                else:
                    bot.send_message(message.chat.id,
                                     'Wir haben folgende Quelle: ' + quelle + ',jedoch ist sie mit Vorsicht zu nutzen weil Nutzer sie als nicht nützlich eingestuft wurden')
            for qq in endqul[quelle]: # Ausgabe der Informationen
                try:
                    time.sleep(0.6)
                    bot.send_message(message.chat.id, qq)
                except:
                    listov = divide_string(qq, 5)
                    for l in listov:
                        time.sleep(0.6)
                        try:
                            bot.send_message(message.chat.id, l)
                        except:
                            pass
            if not already: # Erstellen des Buttons, der den User fragt ob die Infos nützlich waren
                quelle = shortener(quelle)
                keyboard = types.InlineKeyboardMarkup()
                button_ja = types.InlineKeyboardButton('Ja', callback_data=quelle)
                button_nein = types.InlineKeyboardButton('Nein', callback_data='%' + quelle)
                keyboard.add(button_ja)
                keyboard.add(button_nein)
                time.sleep(2)
                bot.send_message(message.chat.id, text='War die Information für sie nützlich?', reply_markup=keyboard)
                time.sleep(20)



@bot.callback_query_handler(func=lambda call: True)
# Umgang mit den Buttons und speicherung der Quelle in der Datenbank
def handle_query(call):
    if '%' in call.data:
        bot.send_message(call.message.chat.id, 'Alles klar, wir werden diese Information nicht speichern')
        no_list.append(call.data[1:])

    else:
        bot.send_message(call.message.chat.id, 'Alles klar, wir werden diese Information speichern')
        save_in_database(call.data)


bot.polling(none_stop=True)
