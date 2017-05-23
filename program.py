import re
import os
import filesort
import pymorphy2
import sqlite3
import json

morph = pymorphy2.MorphAnalyzer()


def chapters():  # находит названия глав и записывает в файл, делит текст на главы и раскладывает по файлам
    f = open('m&m.txt', 'r', encoding='utf-8')
    all = f.read()
    f.close()
    m = re.findall('(Глава [0-9]*)( )(.*)(\n)',all)
    chapt_names = []
    for el in m:
        chapt_names.append(el[2])
    a = open('chapt_names.txt','a', encoding='utf-8')
    for name in chapt_names:
        a.write(name + '\n')
    n = re.findall('((Глава [0-9]*)( )(.*)(\n))(((.|\s))+?)(?=((Глава [0-9])|Конец))', all)
    chapts = []
    for el in n:
        chapts.append(el[5])
    dir = '/Users/sea_fog/Documents/github/coursework/chapters/'
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
    directory = '/Users/sea_fog/Documents/github/coursework/chapters'
    files = filesort.sortfiles(os.listdir(directory))
    dir = '/Users/sea_fog/Documents/github/coursework/chapters_clean/'
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


def load_stopwords(): # создает список стоп-слов из местоимений и служебных слов
    f = open('/Users/sea_fog/Documents/github/coursework/stopwords/stopprons.txt', 'r', encoding='utf-8')
    tablep = f.read()
    f.close()
    stopprons1 = tablep.split()
    n = open('/Users/sea_fog/Documents/github/coursework/stopwords/stopintjs.txt', 'r', encoding='utf-8')
    tablei = n.read()
    n.close()
    stopintjs = tablei.split()
    stopprons2 = []
    stops = []
    for stop in stopintjs:
        if re.match('(([а-я]+)-*)+', stop) is not None:
            stops.append(stop)
        else:
            continue
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
    directory = '/Users/sea_fog/Documents/github/coursework/chapters_clean/'
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
        conn = sqlite3.connect('/Users/sea_fog/Documents/github/coursework/database.db')
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
    chars = json.loads((open('/Users/sea_fog/Documents/github/coursework/names.json', 'r', encoding='utf-8')).read())
    charstransl = ['Берлиоз', 'Маргарита', 'Мастер', 'Воланд', 'Иван Бездомный', 'Иешуа Га-Ноцри', 'Понтий Пилат',
                   'Коровьев-Фагот', 'Азазелло', 'Абадонна', 'Александр Рюхин', 'Аркалий Аполлонович Семплеяров',
                   'Соков', 'Никанор Иванович Босой', 'Бегемот', 'Стравинский', 'Римский', 'Афраний',
                   'Арчибальд Арчибальдович', 'барон Майгель', 'Гелла', 'Бенгальский', 'Иосиф Каифа', 'Иуда',
                   'Левий Матвей', 'Лиxодеев', 'Фрида', 'Василий Степанович Ласточкин', 'Варенуха']
    directory = '/Users/sea_fog/Documents/github/coursework/chapters'
    files = filesort.sortfiles(os.listdir(directory))
    n = 1
    for file in files:
        charqs = []
        for person in chars:
            charq = len(re.findall(person, open(directory + '/' + file, 'r', encoding='utf-8').read()))
            if charq in range(1, 2):
                charq = 0
            charqs.append(str(charq))
        dicti = dict(zip(charstransl, charqs))
        conn = sqlite3.connect('/Users/sea_fog/Documents/github/coursework/database.db')
        c = conn.cursor()
        command = 'CREATE TABLE IF NOT EXISTS chapt' + str(n) + '_freq (nom TEXT, frequency INTEGER)'
        c.execute(command)
        for key, value in dicti.items():
            comm = 'INSERT INTO chapt' + str(n) + '_freq (nom, frequency) VALUES (?, ?)'
            c.execute(comm, (key, value))
            conn.commit()
        n += 1


def main():
#    chapters()
#    loop_open()
    count_char_names()


if __name__ == "__main__":
   main()

