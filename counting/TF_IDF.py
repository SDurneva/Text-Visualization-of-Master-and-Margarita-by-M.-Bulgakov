def tf(document):  # считает tf для каждого слова текста (на вход список)
    from collections import Counter
    tf_document = Counter(document)
    for i in tf_document:
        tf_document[i] = tf_document[i]/float(len(tf_document))  # встречаемость слова деленная на общее количество слов
    return tf_document  # объект типа Counter c TF всех слов текста

def idf(word, corpus):  # слово, список списков слов
    import math
    # количество документов, в которых встречается искомый термин
    return math.log10(len(corpus)/sum([1.0 for i in corpus if word in i]))

    documents_list = []
    for document in corpus:
        tf_idf_dictionary = {}
        computed_tf = compute_tf(document)
        for word in computed_tf:
            tf_idf_dictionary[word] = computed_tf[word] * compute_idf(word, corpus)
        documents_list.append(tf_idf_dictionary)
    return documents_list