import sqlite3
import re


def get_numbers():  # извлекает из БД имена героев и их встречаемость по главам в удобном для google charts формате
    conn = sqlite3.connect('/Users/sea_fog/Documents/github/coursework/database.db')
    c = conn.cursor()
    all = []
    for n in range(1, 34):
        c.execute("SELECT * FROM chapt" + str(n) + "_freq")
        all.append(c.fetchall())
    graphs = []
    for el in all:
        el_new = []
        for pers in el:
            el_new.append(list(pers))
        graphs.append(el_new)
    conn.close()
    for graph in graphs:
        print(graph)


def get_numbers2():  # извлекает из БД названия глав и среднюю длину предложений для каждой главы
    conn = sqlite3.connect('/Users/sea_fog/Documents/github/coursework/database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM average_sl")
    for row in c.fetchall():
        print(row)


def main():
    get_numbers2()


if __name__ == "__main__":
   main()