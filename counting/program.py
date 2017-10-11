# -*- coding: utf8 -*-
import re
import os
import filesort
import pymorphy2
import sqlite3
import json
import TF_IDF
from collections import OrderedDict
from decimal import *

morph = pymorphy2.MorphAnalyzer()


def chapters():  # находит названия глав и записывает в файл, делит текст на главы и раскладывает по файлам
    f = open('counting/m&m.txt', 'r', encoding='utf-8')
    all = f.read()
    f.close()
    m = re.findall('(Глава [0-9]*)( )(.*)(\n)|Эпилог',all)
    chapt_names = []
    for el in m:
        chapt_names.append(el[2])
    a = open('counting/chapt_names.txt', 'a', encoding='utf-8')
    for name in chapt_names:
        a.write(name + '\n')
    n = re.findall('((Глава [0-9]*)( )(.*)(\n))(((.|\s))+?)(?=((Глава [0-9])|Конец))', all)
    chapts = []
    for el in n:
        chapts.append(el[5])
    dir = '/counting/chapters/'
    i = 1
    for chapt in chapts:
        filename = dir + 'chapt' + str(i) + '.txt'
        with open(filename, 'w', encoding='utf-8') as file:
            try:
                file.write(chapt)
                i += 1
            except:
                print('Печалька с файлом %s' % filename)


def loop_open():  # разбивает текст глав на слова, раскладывает по файлам
    directory = 'counting/chapters'
    files = filesort.sortfiles(os.listdir(directory))
    dir = 'counting/chapters_clean/'
    i = 1
    for file in files:
        f = open(directory + '/' + file, 'r', encoding='utf-8')
        string = f.read()
        f.close()
        a = string.split()
        a1 = []
        for word in a:
            word = word.strip('.,!?():;–«»…[]“„…—№').lower()
            a1.append(word)
        for word in a1:
            if word == '':
                a1.remove(word)
            else:
                continue
        filename = dir + 'chapt' + str(i) + '.txt'
        with open(filename, 'w', encoding='utf-8') as file:
            try:
                for word in a1:
                    file.write(word + '\n')
                i += 1
            except:
                print('Печалька с файлом %s' % filename)


def load_stopwords():  # создает список стоп-слов из местоимений и служебных слов
    f = open('counting/stopwords/stopprons.txt', 'r', encoding='utf-8')
    tablep = f.read()
    f.close()
    stopprons1 = tablep.split()
    n = open('counting/stopwords/stopintjs.txt', 'r', encoding='utf-8')
    tablei = n.read()
    n.close()
    stopintjs = tablei.split()
    a = open('counting/stopwords/stopadvs.txt', 'r', encoding='utf-8')
    tablea = a.read()
    n.close()
    stopadvs = tablea.split()
    stopprons2 = []
    stops = []
    for stop in stopintjs:
        if re.match('(([а-я]+)-*)+', stop) is not None:
            stops.append(stop)
        else:
            continue
    for stop in stopadvs:
        if re.match('(([а-я]+)-*)+', stop) is not None:
            stops.append(stop)
    for stop in stopprons1:
        if re.match('(([а-я]+)-*)+', stop) is not None:
            stopprons2.append(stop)
        else:
            continue
    allprons = []
    for stop in stopprons2:
        allprons.append(morph.parse(stop)[0])
    dicti = dict(zip(allprons, stopprons2))
    for i in dicti:
        if 'NOUN' in i.tag or 'NPRO' in i.tag or 'ADJF' in i.tag or 'ADJS' in i.tag:
            continue
        else:
            stops.append(dicti[i])
    prons_lex = []
    for pron in allprons:
        prons_lex.append(pron.lexeme)
    for el in prons_lex:
        for wrd in el:
            stops.append(wrd.word)
    stops = sorted(list(set(stops)))
    for el in stops:
        print(el)
    return stops


def make_bags(stops):  # для каждой главы создает bag of words и таблицу с кол.-вом вхождений в базе данных
    directory = 'counting/chapters_clean/'
    files = filesort.sortfiles(os.listdir(directory))
    i = 1
    n = 1
    print(files)
    allwords = []
    for file in files:
        f = open(directory + file, 'r', encoding='utf-8')
        i += 1
        string = f.read()
        f.close()
        a = string.split('\n')
        conn = sqlite3.connect('counting/database.db')
        c = conn.cursor()
        command = 'CREATE TABLE IF NOT EXISTS chapt' + str(n) + ' (word TEXT, frequency INTEGER)'
        c.execute(command)
        a1 = []
        for word in a:
            if word not in stops:
                a1.append(word)
        done = []
        a2 = []
        for word in a1:
            a2.append(morph.parse(word)[0].normal_form)
            allwords.append(morph.parse(word)[0].normal_form)
        for word in a2:
            if word not in done:
                comm = 'INSERT INTO chapt' + str(n) + ' (word, frequency) VALUES (?, ?)'
                c.execute(comm, (word, a2.count(word)))
                conn.commit()
                done.append(word)
            else:
                continue
        n += 1
    c.close()
    conn.close()


def count_char_names():  # для героев подсчитывает кол.-во их упоминаний в каждой главе, создает для них по словарю
    chars = json.loads((open('counting/names.json', 'r', encoding='utf-8')).read())
    charstransl = ['Берлиоз', 'Маргарита', 'Мастер', 'Воланд', 'поэт Иван Бездомный', 'Иешуа Га-Ноцри',
                   'прокуратор Иудеи Понтий Пилат', 'Коровьев-Фагот', 'Азазелло', 'Абадонна', 'поэт Александр Рюхин',
                   'председатель акустической комиссии московских театров Аркадий Аполлонович Семплеяров',
                   'буфетчик Варьете Соков',
                   'председатель жилищного товарищества дома 302-бис по Садовой Никанор Иванович Босой',
                   'кот Бегемот', 'профессор Стравинский', 'финдиректор Варьете Римский',
                   'начальник тайной стражи прокуратора Афраний',
                   'директор ресторана Дома Грибоедова Арчибальд Арчибальдович', 'барон Майгель', 'Гелла',
                   'конферансье Варьете Жорж Бенгальский', 'иудейский первосвященник Иосиф Каифа',
                   'Иуда из Кириафа', 'Левий Матвей', 'директор Варьете Лиxодеев', 'Фрида',
                   'бухгалтер Варьете Ласточкин', 'администратор Варьете Варенуха', 'Аннушка, которая разлила масло',
                   'дядя Берлиоза, Максимилиан Андреевич Поплавский', 'профессор Кузьмин', 'домработница Маргариты Наташа',
                   'критик Латунский']
    directory = 'counting/chapters'
    files = filesort.sortfiles(os.listdir(directory))
    files.append('epilogue.txt')
    print(files)
    n = 1
    for file in files:
        charqs = []
        for person in chars:
            charq = len(re.findall(person, open(directory + '/' + file, 'r', encoding='utf-8').read()))
            if charq in range(1, 2):
                charq = 0
            charqs.append(str(charq))
        dicti = dict(zip(charstransl, charqs))
        conn = sqlite3.connect('counting/database.db')
        c = conn.cursor()
        command = 'CREATE TABLE IF NOT EXISTS chapt' + str(n) + '_freq (nom TEXT, frequency INTEGER)'
        c.execute(command)
        for key, value in dicti.items():
            comm = 'INSERT INTO chapt' + str(n) + '_freq (nom, frequency) VALUES (?, ?)'
            c.execute(comm, (key, value))
            conn.commit()
        n += 1
    c.close()
    conn.close()


def count_foreigner_plus(): # в базу данных добавляются данные о специфических упоминаниях героев
    directory = 'counting/chapters/'
    files1 = ['chapt1.txt', 'chapt2.txt', 'chapt3.txt', 'chapt4.txt', 'chapt5.txt', 'chapt6.txt', 'chapt7.txt',
              'chapt8.txt', 'chapt9.txt', 'chapt10.txt', 'chapt11.txt', 'chapt12.txt', 'chapt13.txt', 'chapt14.txt',
              'chapt15.txt', 'chapt16.txt', 'chapt17.txt', 'chapt18.txt', 'chapt19.txt', 'chapt20.txt']
    foreigner_q = []
    for file in files1:
        q = len(re.findall('иностран(ец|ца|цем|це)', open(directory + file, 'r', encoding='utf-8').read()))
        foreigner_q.append(str(q))
    conn = sqlite3.connect('counting/database.db')
    c = conn.cursor()
    n = 1
    for el in foreigner_q:
        c.execute('SELECT frequency FROM chapt' + str(n) + '_freq WHERE nom="Воланд"')
        q1 = c.fetchall()[0][0]
        comm = "UPDATE chapt" + str(n) + "_freq SET frequency=? WHERE nom='Воланд'"
        k = str(q1 + int(el))
        c.execute(comm, (k,))
        conn.commit()
        n += 1
    c.close()
    conn.close()

def count_professor1_plus(): # в базу данных добавляются данные о специфических упоминаниях героев
    directory = 'counting/chapters/'
    files1 = ['chapt3.txt', 'chapt4.txt']
    foreigner_q = []
    for file in files1:
        q = len(re.findall('профессор(а|у|ом|е)*', open(directory + file, 'r', encoding='utf-8').read()))
        foreigner_q.append(str(q))
    conn = sqlite3.connect('counting/database.db')
    c = conn.cursor()
    n = 3
    for el in foreigner_q:
        c.execute('SELECT frequency FROM chapt' + str(n) + '_freq WHERE nom="Воланд"')
        q1 = c.fetchall()[0][0]
        comm = "UPDATE chapt" + str(n) + "_freq SET frequency=? WHERE nom='Воланд'"
        k = str(q1 + int(el))
        c.execute(comm, (k,))
        conn.commit()
        n += 1
    c.close()
    conn.close()


def count_gost_plus():  # в базу данных добавляются данные о специфических упоминаниях героев
    directory = 'counting/chapters/'
    q = len(re.findall('гост(ь|я|ю|ем|е)', open(directory + 'chapt13.txt', 'r', encoding='utf-8').read()))
    print(q)
    conn = sqlite3.connect('counting/database.db')
    c = conn.cursor()
    c.execute('SELECT frequency FROM chapt13_freq WHERE nom="Мастер"')
    q1 = c.fetchall()[0][0]
    print(q1)
    c.execute("UPDATE chapt13_freq SET frequency=? WHERE nom='Мастер'", (str(q1 + q),))
    conn.commit()
    c.close()
    conn.close()

    #

    # master-gost = ['chapt13.txt']
    # bosoy_predsedatel = ['chapt9.txt']
    # afrany-gost = ['chapt25.txt']
    # professor bezdomn = ['epilogue.txt']
    # (профессор(а|у|ом|е)*)( Кузьмин(а|у|ым|е)*)*|Кузьмин(а|у|ым|е)* 'chapt18.txt'


def make_lists(stops):   # создание списков слов по главам для дальнейшего подсчета индекса tf-idf
    directory = 'counting/chapters_clean'
    allchapts1 = []
    for i in range(1, 34):
        chapt = ((open(directory + 'chapt' + str(i) + '.txt')).read()).split('\n')
        allchapts1.append(chapt)
    allchapts2 = []
    for chapt1 in allchapts1:
        chapt = []
        for word in chapt1:
            if word not in stops and word != '':
                chapt.append(morph.parse(word)[0].normal_form)
        allchapts2.append(chapt)
    allchapts = []
    for chapt1 in allchapts2:
        chapt = []
        for word in chapt1:
            if word not in stops:
                chapt.append(word)
        allchapts.append(chapt)
    return allchapts


def calc_tf_idf(allchapts):  # подсчет tf-idf при использовании функций модуля TF_DF, подсчитывающих tf и idf по отдельности
    documents_list = []
    for document in allchapts:
        tf_idf_dictionary = {}
        computed_tf = TF_IDF.tf(document)
        for word in computed_tf:
            tf_idf_dictionary[word] = computed_tf[word] * TF_IDF.idf(word, allchapts)
        documents_list.append(tf_idf_dictionary)
    conn = sqlite3.connect('counting/database2.db')
    c = conn.cursor()
    n = 1
    for list in documents_list:
        command = 'CREATE TABLE IF NOT EXISTS chapt' + str(n) + '_tfidf (nom TEXT, tf_idf FLOAT)'
        c.execute(command)
        for key, value in list.items():
            comm = 'INSERT INTO chapt' + str(n) + '_tfidf (nom, tf_idf) VALUES (?, ?)'
            c.execute(comm, (key, value))
            conn.commit()
        n += 1
    c.close()
    conn.close()



def sent_length():
    names1 = (open('chapt_names.txt', 'r', encoding='utf-8')).read().split('\n')
    g = 1
    names = []
    for name in names1:
        names.append('Глава ' + str(g) + '. ' + name)
        g += 1
    names[-1] = 'Эпилог'
    av_slens = []
    for n in range(1, 34):
        text = (open('chapters/chapt' + str(n) + '.txt', 'r', encoding='utf-8')).read()
        n += 1
        sentences = re.split('(?<!\w\.\w.)(?<![А-Я][а-я]\.)(?<=\.|\?)\s', text)
        wordbags = []
        for s in sentences:
            bag1 = s.split()
            bag = []
            for w in bag1:
                w = w.strip('.,!?():;–«»…[]“„…—№')
                if w != '':
                    bag.append(w)
            if len(bag) > 2:
                wordbags.append(bag)
        lens = []
        for sent in wordbags:
            lens.append(len(sent))
        i = 0
        for slen in lens:
            i += slen
        av_slens.append("%.2f" % (i / len(wordbags)))
    leng = []
    for n in range(1, 34):
        text1 = (open('chapters_clean/chapt' + str(n) + '.txt', 'r', encoding='utf-8')).read().split('\n')
        text = []
        for w in text1:
            if w != '':
                text.append(w)
        leng.append(len(text))
    db_data = [names, av_slens, leng, ' ']
    conn = sqlite3.connect('/Users/sea_fog/Documents/github/coursework/database.db')
    c = conn.cursor()
    command = 'CREATE TABLE IF NOT EXISTS average_sl (chapt_nom TEXT, average_sl INTEGER, color TEXT, c_length INTEGER)'
    c.execute(command)
    for i in range(len(db_data[0])):
        comm = 'INSERT INTO average_sl (chapt_nom, average_sl, color, c_length) VALUES (?, ?, ?, ?)'
        c.execute(comm, (db_data[0][i], db_data[1][i], db_data[3], db_data[2][i]))
        conn.commit()


def make_wjson():
    chars = [[['кот Бегемот', 2], ['Аннушка, которая разлила масло', 2], ['поэт Иван Бездомный', 55], ['Берлиоз', 72], ['Коровьев-Фагот', 2], ['Воланд', 29]], [['прокуратор Иудеи Понтий Пилат', 180], ['Левий Матвей', 5], ['Иешуа Га-Ноцри', 78], ['иудейский первосвященник Иосиф Каифа', 32]], [['прокуратор Иудеи Понтий Пилат', 2], ['поэт Иван Бездомный', 11], ['Берлиоз', 28], ['Коровьев-Фагот', 3], ['Воланд', 19]], [['прокуратор Иудеи Понтий Пилат', 2], ['кот Бегемот', 11], ['Аннушка, которая разлила масло', 8], ['поэт Иван Бездомный', 65], ['Берлиоз', 4], ['Коровьев-Фагот', 15], ['Воланд', 11]], [['поэт Иван Бездомный', 30], ['Берлиоз', 19], ['поэт Александр Рюхин', 3], ['директор ресторана Дома Грибоедова Арчибальд Арчибальдович', 3], ['Воланд', 2]], [['прокуратор Иудеи Понтий Пилат', 4], ['поэт Иван Бездомный', 56], ['Берлиоз', 5], ['поэт Александр Рюхин', 38], ['директор ресторана Дома Грибоедова Арчибальд Арчибальдович', 2], ['Воланд', 5]], [['директор Варьете Лиxодеев', 81], ['финдиректор Варьете Римский', 7], ['кот Бегемот', 8], ['Берлиоз', 13], ['Азазелло', 4], ['Воланд', 14]], [['прокуратор Иудеи Понтий Пилат', 18], ['Аннушка, которая разлила масло', 3], ['поэт Иван Бездомный', 79], ['Берлиоз', 3], ['Воланд', 7], ['профессор Стравинский', 29]], [['директор Варьете Лиxодеев', 8], ['кот Бегемот', 4], ['Берлиоз', 3], ['Коровьев-Фагот', 42], ['председатель жилищного товарищества дома 302-бис по Садовой Никанор Иванович Босой', 97], ['Воланд', 14]], [['директор Варьете Лиxодеев', 28], ['финдиректор Варьете Римский', 53], ['администратор Варьете Варенуха', 87], ['поэт Иван Бездомный', 8], ['Коровьев-Фагот', 2], ['Воланд', 9]], [['прокуратор Иудеи Понтий Пилат', 5], ['кот Бегемот', 4], ['поэт Иван Бездомный', 30], ['Берлиоз', 8], ['Воланд', 4]], [['директор Варьете Лиxодеев', 2], ['финдиректор Варьете Римский', 21], ['кот Бегемот', 27], ['администратор Варьете Варенуха', 3], ['конферансье Варьете Жорж Бенгальский', 18], ['Коровьев-Фагот', 50], ['председатель акустической комиссии московских театров Аркадий Аполлонович Семплеяров', 19], ['Воланд', 7]], [['Мастер', 63], ['прокуратор Иудеи Понтий Пилат', 13], ['кот Бегемот', 2], ['поэт Иван Бездомный', 80], ['критик Латунский', 6], ['Берлиоз', 6], ['профессор Стравинский', 3]], [['директор Варьете Лиxодеев', 13], ['финдиректор Варьете Римский', 63], ['администратор Варьете Варенуха', 39]], [['поэт Иван Бездомный', 4], ['Коровьев-Фагот', 8], ['председатель жилищного товарищества дома 302-бис по Садовой Никанор Иванович Босой', 57], ['Азазелло', 2], ['Воланд', 1], ['профессор Стравинский', 3]], [['прокуратор Иудеи Понтий Пилат', 5], ['Левий Матвей', 31], ['Иешуа Га-Ноцри', 30]], [['бухгалтер Варьете Ласточкин', 49], ['директор Варьете Лиxодеев', 24], ['финдиректор Варьете Римский', 9], ['кот Бегемот', 4], ['администратор Варьете Варенуха', 5], ['Коровьев-Фагот', 5], ['Воланд', 5]], [['профессор Кузьмин', 45], ['кот Бегемот', 14], ['дядя Берлиоза, Максимилиан Андреевич Поплавский', 62], ['Гелла', 5], ['Берлиоз', 12], ['Коровьев-Фагот', 13], ['Азазелло', 13], ['буфетчик Варьете Соков', 86], ['Воланд', 5]], [['Мастер', 9], ['прокуратор Иудеи Понтий Пилат', 3], ['кот Бегемот', 3], ['поэт Иван Бездомный', 3], ['домработница Маргариты Наташа', 7], ['Маргарита', 88], ['критик Латунский', 3], ['Берлиоз', 4], ['Азазелло', 31], ['Воланд', 2]], [['домработница Маргариты Наташа', 8], ['Маргарита', 46], ['Азазелло', 5], ['Воланд', 1]], [['домработница Маргариты Наташа', 19], ['Маргарита', 112], ['критик Латунский', 13], ['Берлиоз', 2]], [['Абадонна', 6], ['кот Бегемот', 31], ['домработница Маргариты Наташа', 2], ['Маргарита', 70], ['Гелла', 7], ['Коровьев-Фагот', 40], ['Азазелло', 19], ['Воланд', 39]], [['Абадонна', 3], ['кот Бегемот', 23], ['домработница Маргариты Наташа', 4], ['Маргарита', 100], ['Гелла', 2], ['Коровьев-Фагот', 43], ['Фрида', 7], ['Азазелло', 11], ['барон Майгель', 9], ['Воланд', 18]], [['Мастер', 39], ['прокуратор Иудеи Понтий Пилат', 5], ['финдиректор Варьете Римский', 2], ['кот Бегемот', 59], ['администратор Варьете Варенуха', 5], ['Аннушка, которая разлила масло', 31], ['поэт Иван Бездомный', 4], ['домработница Маргариты Наташа', 6], ['Маргарита', 119], ['Гелла', 16], ['критик Латунский', 3], ['Коровьев-Фагот', 34], ['Фрида', 11], ['Азазелло', 35], ['барон Майгель', 4], ['Воланд', 83]], [['прокуратор Иудеи Понтий Пилат', 87], ['начальник тайной стражи прокуратора Афраний', 4], ['Иешуа Га-Ноцри', 2], ['иудейский первосвященник Иосиф Каифа', 3], ['Иуда из Кириафа', 3]], [['прокуратор Иудеи Понтий Пилат', 128], ['поэт Иван Бездомный', 2], ['начальник тайной стражи прокуратора Афраний', 53], ['Левий Матвей', 29], ['Иешуа Га-Ноцри', 6], ['иудейский первосвященник Иосиф Каифа', 2], ['Иуда из Кириафа', 57]], [['Мастер', 2], ['прокуратор Иудеи Понтий Пилат', 2], ['директор Варьете Лиxодеев', 12], ['финдиректор Варьете Римский', 13], ['кот Бегемот', 40], ['администратор Варьете Варенуха', 11], ['Аннушка, которая разлила масло', 9], ['поэт Иван Бездомный', 24], ['домработница Маргариты Наташа', 2], ['Маргарита', 6], ['Берлиоз', 6], ['Коровьев-Фагот', 6], ['Азазелло', 6], ['барон Майгель', 4], ['председатель акустической комиссии московских театров Аркадий Аполлонович Семплеяров', 17], ['Воланд', 10], ['профессор Стравинский', 2]], [['кот Бегемот', 38], ['Коровьев-Фагот', 44], ['директор ресторана Дома Грибоедова Арчибальд Арчибальдович', 17]], [['Мастер', 2], ['кот Бегемот', 14], ['Коровьев-Фагот', 11], ['Левий Матвей', 6], ['Азазелло', 6], ['Воланд', 32]], [['Мастер', 62], ['поэт Иван Бездомный', 20], ['Маргарита', 52], ['Азазелло', 37], ['Воланд', 4]], [['Мастер', 10], ['кот Бегемот', 6], ['Маргарита', 9], ['Коровьев-Фагот', 6], ['Воланд', 10]], [['Мастер', 24], ['прокуратор Иудеи Понтий Пилат', 5], ['кот Бегемот', 3], ['Маргарита', 25], ['Коровьев-Фагот', 6], ['Азазелло', 3], ['Иешуа Га-Ноцри', 3], ['Воланд', 21]], [['Воланд', 7], ['конферансье Варьете Жорж Бенгальский', 2], ['Коровьев-Фагот', 9], ['финдиректор Варьете Римский', 9], ['Маргарита', 2], ['поэт Иван Бездомный', 33], ['председатель акустической комиссии московских театров Аркадий Аполлонович Семплеяров', 3], ['председатель жилищного товарищества дома 302-бис по Садовой Никанор Иванович Босой', 7], ['прокуратор Иудеи Понтий Пилат', 2], ['кот Бегемот', 16], ['администратор Варьете Варенуха', 8], ['директор Варьете Лиxодеев', 9], ['Берлиоз', 3]]]
    names1 = (open('chapt_names.txt', 'r', encoding='utf-8')).read().split('\n')
    g = 1
    names = []
    for name in names1:
        names.append('Глава ' + str(g) + '. ' + name)
        g += 1
    names[-1] = 'Эпилог'
    pairs = OrderedDict(zip(names, chars))
    print(pairs)

def get_tfidf():
    conn = sqlite3.connect('/Users/sea_fog/Documents/github/Text-Visualization-of-Master-and-Margarita-by-M.-Bulgakov/counting/database2.db')
    c = conn.cursor()
    chapts = []
    for i in range (1, 34):
        command = 'SELECT * FROM chapt' + str(i) + '_tfidf WHERE tf_idf > 0.003'
        c.execute(command)
        chapt = []
        for el in c.fetchall():
            el = list(el)
            el[1] = "%.3f" % (el[1])
            chapt.append(el)
        chapts.append(chapt)
    f = open('tfidfs.txt', 'a', encoding='utf-8')
    i = 1
    for chapt in chapts:
        f.write('ГЛАВА' + str(i))
        i += 1
        for el in chapt:
            f.write(str(el) + ';' + '\n')
        f.write('\n' + '\n' + '\n')

    # f = open('website/static/chars.json', 'w', encoding='utf-8')
    # f.write(json.dumps(pairs))



def main():
    # chapters()
    # loop_open()
    # count_char_names()
    # count_gost_plus()
    # calc_tf_idf(make_lists(load_stopwords()))
    # sent_length()
    # make_wjson()
    # load_stopwords()
    get_tfidf()




if __name__ == "__main__":
   main()
