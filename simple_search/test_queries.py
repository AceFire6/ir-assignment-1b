import os
import sys

import parameters
from parameters import print_debug
from query import do_query, blind_relevance_feedback, calculate_MAP, calculate_ndcg


def analyze_results(results, collection, query, msg=''):
    if parameters.show_NDCG:
        print_debug('\nCalculating %s NDCG values:' % msg)
        calculate_ndcg(results, collection, query)

    if parameters.show_MAP:
        print_debug('\nCalculating %s MAP values:' % msg)
        calculate_MAP(results, collection, query)

# check parameter for collection name
if len(sys.argv) < 2:
    print("Syntax: test_queries.py <collection>")
    exit(0)

# construct collection and query
collection = sys.argv[1]
if collection.endswith(os.path.sep):
    collection = collection[:-1]

for query_num in ['1', '2', '3', '4', '5']:
    with open(os.path.join(collection, 'query.%s' % query_num)) as fin:
        query_words = fin.read().strip().split(' ')
        print('Query {0} with query words {1}'.format(query_num, query_words))

        accum, titles, top_words = do_query(collection, query_words)
        results = sorted(accum, key=accum.__getitem__, reverse=True)

        # print top results
        print('Initial Results:')
        for i in range(min(len(results), parameters.num_results)):
            print("{0:10.8f} {1:5} {2}".format(accum[results[i]], results[i],
                                               titles[results[i]]))

        analyze_results(results, collection, query_num, 'initial')

        results, accum, titles = blind_relevance_feedback(query_words, results, titles, top_words, collection)

        print('Final Results:')
        for i in range(min(len(results), parameters.num_results)):
            print("{0:10.8f} {1:5} {2}".format(accum[results[i]], results[i],
                                               titles[results[i]]))

        analyze_results(results, collection, query_num, 'final')

        print('=' * 50, '\n')


