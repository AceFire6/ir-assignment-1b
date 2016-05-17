# Simple extended boolean search engine: query module
# Hussein Suleman
# 14 April 2016

import re
import math
import sys
import os

import porter

import parameters


def do_query(query_words):
    # create accumulators and other data structures
    accum = {}
    filenames = []
    p = porter.PorterStemmer()

    # get N
    f = open(collection + "_index_N", "r")
    N = eval(f.read())
    f.close()

    # get document lengths/titles
    titles = {}
    f = open(collection + "_index_len", "r")
    lengths = f.readlines()
    f.close()

    # get index for each term and calculate similarities using accumulators
    for term in query_words:
        if term != '':
            if parameters.stemming:
                term = p.stem(term, 0, len(term) - 1)
            if not os.path.isfile(collection + "_index/" + term):
                continue
            f = open(collection + "_index/" + term, "r")
            lines = f.readlines()
            idf = 1
            if parameters.use_idf:
                df = len(lines)
                idf = 1 / df
                if parameters.log_idf:
                    idf = math.log(1 + N / df)
            for line in lines:
                mo = re.match(r'([0-9]+)\:([0-9\.]+)', line)
                if mo:
                    file_id = mo.group(1)
                    tf = float(mo.group(2))
                    if not file_id in accum:
                        accum[file_id] = 0
                    if parameters.log_tf:
                        tf = (1 + math.log(tf))
                    accum[file_id] += (tf * idf)
            f.close()
    top_words = {}

    # parse lengths data and divide by |N| and get titles
    for l in lengths:
        mo = re.match(r'([0-9]+)\:([0-9\.]+)\:(.+)\:(.+)', l)
        if mo:
            document_id = mo.group(1)
            length = eval(mo.group(2))
            title = mo.group(3)
            top_words[title] = mo.group(4).split(',')
            if document_id in accum:
                if parameters.normalization:
                    accum[document_id] = accum[document_id] / length
                titles[document_id] = title

    return accum, titles, top_words


# check parameter for collection name
if len(sys.argv)<3:
   print ("Syntax: index.py <collection> <query>")
   exit(0)
 
# construct collection and query
collection = sys.argv[1]
query = ''
arg_index = 2
while arg_index < len(sys.argv):
   query += sys.argv[arg_index] + ' '
   arg_index += 1

# clean query
if parameters.case_folding:
   query = query.lower ()
query = re.sub (r'[^ a-zA-Z0-9]', ' ', query)
query = re.sub (r'\s+', ' ', query)
query_words = query.split (' ')

accum, titles, top_words = do_query(query_words)

results = sorted(accum, key=accum.__getitem__, reverse=True)

# Does the blind relevance feedback
# Takes the top N results and gets the top N highest rated terms from each
# Expands the query to include these new terms and searches again
if parameters.blind_relevance_feedback:
    num_docs = min(len(results), parameters.top_doc_count)
    results = results[:num_docs]

    documents = [titles[results[i]] for i in range(num_docs)]

    word_set = set(query_words)
    # Get top terms from each document and add them to a new query
    for document in documents:
        word_set.update(top_words.get(document, []))

    accum, titles, top_words = do_query(list(word_set))

    results = sorted(accum, key=accum.__getitem__, reverse=True)

# print top results
for i in range (min (len (results), parameters.num_results)):
   print ("{0:10.8f} {1:5} {2}".format (accum[results[i]], results[i], titles[results[i]]))
