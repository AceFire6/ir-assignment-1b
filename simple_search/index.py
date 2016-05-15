# Simple extended boolean search engine: indexer based on cranfield format
# Hussein Suleman
# 21 April 2016

import os
import re
import sys

import porter

import parameters

# check parameter for collection name
if len(sys.argv) == 1:
    print("Syntax: index.py <collection>")
    exit(0)
collection = sys.argv[1]

if not os.path.isdir(collection):
    print('<collection> must be a folder')
    exit(0)

documents = list(filter(lambda x: 'document.' in x, os.listdir(collection)))

data = {}
titles = {}

for document in documents:
    path_to_doc = os.path.join(collection, document)
    identifier = document.split('.')[1]
    titles[identifier] = document

    with open(path_to_doc, 'r') as doc_file:
        content = ' '.join(doc_file.readlines())

    data[identifier] = content.lower() if parameters.case_folding else content


if collection.endswith('/'):
    collection = collection[:-1]

# document length/title file
g = open(collection + "_index_len", "w")

# create inverted files in memory and save titles/N to file
index = {}
N = len(data.keys())
p = porter.PorterStemmer()
for key in data:
    content = re.sub(r'[^ a-zA-Z0-9]', ' ', data[key])
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
    print(key, doc_length, titles[key], sep=':', file=g)

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
