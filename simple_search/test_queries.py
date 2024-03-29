import os
import sys

import parameters
from parameters import print_debug
from query import do_query, blind_relevance_feedback, calculate_AP, calculate_ndcg


def analyze_results(results, collection, query, msg=''):
    if parameters.show_NDCG:
        print_debug('\nCalculating %s NDCG values:' % msg)
        calculate_ndcg(results, collection, query)

    if parameters.show_AP:
        print_debug('\nCalculating %s MAP values:' % msg)
        return calculate_AP(results, collection, query)

for testbed_no in range(1, 17):
    if testbed_no == 10:
        # Testbed 10 is missing relevance information and this breaks
        # our code. So we chose to ignore it.
        continue
    collection = os.path.join('testbeds', 'testbed%d' % testbed_no)
    print('Results for Testbed %d' % testbed_no)
    init_map = 0
    final_map = 0
    for query_num in ['1', '2', '3', '4', '5']:
        with open(os.path.join(collection, 'query.%s' % query_num)) as fin:
            query_words = fin.read().strip().lower().split(' ')
            print('Query {0} with query words {1}'.format(query_num, query_words))

            accum, titles, top_words = do_query(collection, query_words)
            results = sorted(accum, key=accum.__getitem__, reverse=True)
            num_results = min(len(results), parameters.num_results)
            results = results[:num_results]

            # print top results
            print('Initial Results:')
            for i in range(num_results):
                print("{0:10.8f} {1:5} {2}".format(accum[results[i]], results[i],
                                                   titles[results[i]]))

            init_map += analyze_results(results, collection, query_num, 'initial')

            results, accum, titles = blind_relevance_feedback(query_words, results, titles, top_words, collection)
            results = results[:num_results]

            print('Final Results:')
            for i in range(num_results):
                print("{0:10.8f} {1:5} {2}".format(accum[results[i]], results[i],
                                                   titles[results[i]]))

            final_map += analyze_results(results, collection, query_num, 'final')

            print('=' * 50, '\n')

    print('Initial MAP:', init_map / 5)
    print('Final MAP:', final_map / 5)
    print('/%/%' * 40)
    print()

