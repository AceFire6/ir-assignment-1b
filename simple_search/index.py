# Simple extended boolean search engine: indexer based on cranfield format
# Hussein Suleman
# 21 April 2016

import os
import re
import sys
import math

import porter

import parameters


def index_collection(collection):
    documents = list(filter(lambda x: 'document.' in x, os.listdir(collection)))

    doc_data = {}
    titles = {}

    for document in documents:
        path_to_doc = os.path.join(collection, document)
        identifier = document.split('.')[1]
        titles[identifier] = document

        with open(path_to_doc, 'r', errors='ignore') as doc_file:
            content = ' '.join(doc_file.readlines())

        doc_data[identifier] = (content.lower()
                                if parameters.case_folding else content)


    if collection.endswith('/'):
        collection = collection[:-1]

    # document length/title file
    g = open(collection + "_index_len", "w")

    # create inverted files in memory and save titles/N to file
    index = {}
    N = len(doc_data.keys())
    p = porter.PorterStemmer()
    for key in doc_data:
        content = re.sub(r'[^ a-zA-Z0-9]', ' ', doc_data[key])
        content = re.sub(r'\s+', ' ', content)
        words = content.split(' ')
        doc_length = 0
        for word in words:
            if word != '':
                if parameters.stemming:
                    word = p.stem(word, 0, len(word) - 1)
                doc_length += 1
                if not word in index:
                    index[word] = {key: 1}
                else:
                    if not key in index[word]:
                        index[word][key] = 1
                    else:
                        index[word][key] += 1

        word_tf_idf = {}
        words = list(filter(lambda x: x.lower() not in parameters.stop_words, index))
        for word_key in words:
            if key in index[word_key]:
                word_tf_idf[word_key] = index[word_key][key] * math.log(200 / len(index[word_key]))

        top_word_list = ','.join(sorted(word_tf_idf,
                                        key=word_tf_idf.__getitem__,
                                        reverse=True)[:parameters.top_term_count])

        print(key, doc_length, titles[key], top_word_list, sep=':', file=g)

    # document length/title file
    g.close()

    # write inverted index to files
    try:
        os.mkdir(collection + "_index")
    except:
        pass
    for key in index:
        f = open(os.path.join(collection + "_index", key), "w")
        for entry in index[key]:
            print(entry, index[key][entry], sep=':', file=f)
        f.close()

    # write N
    f = open(collection + "_index_N", "w")
    print(N, file=f)
    f.close()


# check parameter for collection name
if len(sys.argv) == 1:
    print("Syntax: index.py <collection>")
    exit(0)
collection = sys.argv[1]

if not os.path.isdir(collection):
    print('<collection> must be a folder')
    exit(0)

if collection.endswith('testbeds'):
    collections = list(filter(lambda x: re.match(r'^testbed[0-9]+$', x),
                              os.listdir(collection)))
    for c_dir in collections:
        index_collection(os.path.join(collection, c_dir))
else:
    index_collection(collection)
