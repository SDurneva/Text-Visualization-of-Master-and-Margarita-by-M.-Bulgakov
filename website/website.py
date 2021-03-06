from flask import Flask
from flask import render_template, url_for
import json
from collections import OrderedDict

app = Flask(__name__)

@app.route('/')
def index():
    main_url = url_for('index')
    chapters_url = url_for('chapters')
    sents_url = url_for('sentences')
    words_url = url_for('words')
    keywords_url = url_for('keywords')
    map_url = url_for('map')
    contactsreferences_url = url_for('contactsreferences')
    return render_template('index.html', main_url=main_url, chapters_url=chapters_url, sents_url=sents_url,
                           words_url = words_url, keywords_url = keywords_url, map_url = map_url, 
                           contactsreferences_url = contactsreferences_url)

@app.route('/chapters')
def chapters():
    chars = (json.load(open('static/chars.json', encoding='utf-8'), object_pairs_hook=OrderedDict)).items()
    main_url = url_for('index')
    chapters_url = url_for('chapters')
    sents_url = url_for('sentences')
    words_url = url_for('words')
    keywords_url = url_for('keywords')
    map_url = url_for('map')
    contactsreferences_url = url_for('contactsreferences')
    return render_template('chapters.html', main_url=main_url, chapters_url=chapters_url, chars=chars,
                           sents_url=sents_url, words_url = words_url, keywords_url = keywords_url, map_url = map_url, 
                           contactsreferences_url = contactsreferences_url)

@app.route('/sentences')
def sentences():
    main_url = url_for('index')
    chapters_url = url_for('chapters')
    sents_url = url_for('sentences')
    words_url = url_for('words')
    keywords_url = url_for('keywords')
    map_url = url_for('map')
    contactsreferences_url = url_for('contactsreferences')
    return render_template('sents.html', main_url=main_url, chapters_url=chapters_url, sents_url=sents_url,
                           words_url = words_url, keywords_url = keywords_url, map_url = map_url, 
                           contactsreferences_url = contactsreferences_url)

@app.route('/words')
def words():
    main_url = url_for('index')
    chapters_url = url_for('chapters')
    sents_url = url_for('sentences')
    words_url = url_for('words')
    keywords_url = url_for('keywords')
    map_url = url_for('map')
    contactsreferences_url = url_for('contactsreferences')
    return render_template('words.html', main_url=main_url, chapters_url=chapters_url, sents_url=sents_url,
                           words_url = words_url, keywords_url = keywords_url, map_url = map_url, 
                           contactsreferences_url = contactsreferences_url)

@app.route('/keywords')
def keywords():
    main_url = url_for('index')
    chapters_url = url_for('chapters')
    sents_url = url_for('sentences')
    words_url = url_for('words')
    keywords_url = url_for('keywords')
    map_url = url_for('map')
    contactsreferences_url = url_for('contactsreferences')
    return render_template('keywords.html', main_url=main_url, chapters_url=chapters_url, sents_url=sents_url,
                           words_url = words_url, keywords_url = keywords_url, map_url = map_url, 
                           contactsreferences_url = contactsreferences_url)

@app.route('/map')
def map():
    main_url = url_for('index')
    chapters_url = url_for('chapters')
    sents_url = url_for('sentences')
    words_url = url_for('words')
    keywords_url = url_for('keywords')
    map_url = url_for('map')
    contactsreferences_url = url_for('contactsreferences')
    return render_template('map.html', main_url=main_url, chapters_url=chapters_url, sents_url=sents_url,
                           words_url=words_url, keywords_url=keywords_url, map_url = map_url, 
                           contactsreferences_url = contactsreferences_url)

@app.route('/contactsreferences')
def contactsreferences():
    main_url = url_for('index')
    chapters_url = url_for('chapters')
    sents_url = url_for('sentences')
    words_url = url_for('words')
    keywords_url = url_for('keywords')
    map_url = url_for('map')
    contactsreferences_url = url_for('contactsreferences')
    return render_template('contactsreferences.html', main_url=main_url, chapters_url=chapters_url, sents_url=sents_url,
                           words_url=words_url, keywords_url=keywords_url, map_url = map_url, 
                           contactsreferences_url = contactsreferences_url)

if __name__ == '__main__':
    app.run(debug=True)