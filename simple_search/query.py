# Simple extended boolean search engine: query module
# Hussein Suleman
# 14 April 2016

import re
import math
import sys
import os

import porter

import parameters
from parameters import print_debug, stop_words


def do_query(collection_dir, terms):
    # create accumulators and other data structures
    tf_idf_accum = {}
    filenames = []
    p = porter.PorterStemmer()

    # get N
    f = open("%s_index_N" % collection_dir, "r")
    N = eval(f.read())
    f.close()

    # get document lengths/titles
    titles = {}
    f = open("%s_index_len" % collection_dir, "r")
    lengths = f.readlines()
    f.close()

    # get index for each term and calculate similarities using accumulators
    for term in terms:
        if term != '':
            if parameters.stemming:
                term = p.stem(term, 0, len(term) - 1)
            term_path = "%s_index/%s" % (collection_dir, term)
            if not os.path.isfile(term_path):
                continue
            f = open(term_path, "r")
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
                    if not file_id in tf_idf_accum:
                        tf_idf_accum[file_id] = 0
                    if parameters.log_tf:
                        tf = (1 + math.log(tf))
                    tf_idf_accum[file_id] += (tf * idf)
            f.close()
    top_words = {}

    # parse lengths data and divide by |N| and get titles
    for l in lengths:
        mo = re.match(r'([0-9]+)\:([0-9\.]+)\:(.+)\:(.+)', l)
        if mo:
            doc_id = mo.group(1)
            length = eval(mo.group(2))
            title = mo.group(3)
            top_words[title] = mo.group(4).split(',')
            if doc_id in tf_idf_accum:
                if parameters.normalization:
                    tf_idf_accum[doc_id] = tf_idf_accum[doc_id] / length
                titles[doc_id] = title

    return tf_idf_accum, titles, top_words


def blind_relevance_feedback(query_words, results, titles, top_words, collection):
    # Does the blind relevance feedback
    # Takes the top N results and gets the top N highest rated terms from each
    # Expands the query to include these new terms and searches again

    print_debug('\nRunning blind relevance feedback')
    num_docs = min(len(results), parameters.top_doc_count)
    print_debug('Using top %d results' % num_docs)
    results = results[:num_docs]

    documents = [titles[results[i]] for i in range(num_docs)]
    print_debug('Top {0} docs: {1}'.format(num_docs, documents))

    print_debug('Using top %d terms' % parameters.top_term_count)

    if parameters.unique_query_elements:
        print_debug('Unique query terms only')
        word_set = set(query_words)
        # Get top terms from each document and add them to a new query
        for document in documents:
            word_set.update(top_words.get(document, []))
    else:
        word_set = query_words
        for document in documents:
            word_set.extend(top_words.get(document, []))

    print_debug('Expanded query terms: {0}'.format(word_set))
    accum, titles, top_words = do_query(collection, list(word_set))

    results = sorted(accum, key=accum.__getitem__, reverse=True)
    return results, accum, titles


def get_relevance_dict(results, collection):
    results = list(map(int, results))
    relevance = {'1': {}, '2': {}, '3': {}, '4': {}, '5': {}}
    for query_num in relevance:
        with open(os.path.join(collection, 'relevance.%s' % query_num)) as fin:
            relevance_vals = [int(line) for line in fin.readlines()]
            for i in range(len(results)):
                relevance[query_num][results[i]] = (relevance_vals[results[i] - 1])
    return relevance


def calculate_ndcg(results, collection, query):
    num_docs = min(len(results), parameters.num_results)
    results = list(map(int, results[:num_docs]))
    dcg = 0
    idcg = 0
    relevance = get_relevance_dict(results, collection)[query]

    # calculates the dcg for each document
    for i in range(num_docs):
        dcg += relevance[results[i]] / math.log(i + 2, 2)
    print('DCG for query.%s: %f' % (query, dcg))

    # create the idcg list
    ordered_keys = sorted(relevance, key=relevance.get, reverse=True)
    for j in range(num_docs):
        idcg += relevance[ordered_keys[j]] / math.log(j + 2, 2)
    print('IDCG for query.%s: %f' % (query, idcg))

    # Calculating the NDCG
    if idcg != 0:
        print('NDCG for query.%s: %f' % (query, dcg / idcg))


def calculate_AP(results, collection, query):
    relevance = get_relevance_dict(results, collection)[query]
    results = list(map(int, results))
    relevant_docs = 0
    total_docs = 0
    AP = 0
    for result in results:
        total_docs += 1
        if relevance[result] != 0:
            relevant_docs += 1
        AP += relevant_docs / total_docs
    print('AP for query.%s is: %f' % (query, AP / len(results)))
    return AP / len(results)


def main():
    # check parameter for collection name
    if len(sys.argv) < 3:
        print("Syntax: index.py <collection> <query>")
        exit(0)

    # construct collection and query
    collection = sys.argv[1]
    if collection.endswith(os.path.sep):
        collection = collection[:-1]

    query = ''
    arg_index = 2
    while arg_index < len(sys.argv):
        query += sys.argv[arg_index] + ' '
        arg_index += 1

    # clean query
    if parameters.case_folding:
        query = query.lower()
    query = re.sub(r'[^ a-zA-Z0-9]', ' ', query)
    query = re.sub(r'\s+', ' ', query)
    query = query.strip()
    # filter out stop words from the user's query
    query_words = list(filter(lambda x: x not in stop_words, query.split(' ')))

    print_debug('Query terms: {0}'.format(query_words))

    accum, titles, top_words = do_query(collection, query_words)

    results = sorted(accum, key=accum.__getitem__, reverse=True)
    print_debug('Initial Results:')
    # print top results
    for i in range(min(len(results), parameters.num_results)):
        print("{0:10.8f} {1:5} {2}".format(accum[results[i]], results[i],
                                           titles[results[i]]))

    if len(results) == 0:
        print('No results')
        exit()

if __name__ == '__main__':
    main()
