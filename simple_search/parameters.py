# simple extended boolean search engine: configurable parameters
# Hussein Suleman
# 21 April 2016

debug = True


def print_debug(msg):
    if debug:
        print(msg)

normalization = True
stemming = True
case_folding = True
log_tf = True
use_idf = True
log_idf = True
blind_relevance_feedback = True
num_results = 10
top_doc_count = 5
top_term_count = 5
unique_query_elements = False
show_DCG = True
show_IDCG = True
show_NDCG = True

stop_words = ['a', 'about', 'abov', 'after', 'again', 'against', 'all', 'am',
              'an', 'and', 'ani', 'ar', "aren't", 'as', 'at', 'be', 'becaus',
              'been', 'befor', 'be', 'below', 'between', 'both', 'but', 'by',
              "can't", 'cannot', 'could', "couldn't", 'did', "didn't", 'do',
              'doe', "doesn't", 'do', "don't", 'down', 'dure', 'each', 'few',
              'for', 'from', 'further', 'had', "hadn't", 'ha', "hasn't",
              'have', "haven't", 'have', 'he', "he'd", "he'll", "he'", 'her',
              'here', "here'", 'her', 'herself', 'him', 'himself', 'hi', 'how',
              "how'", 'i', "i'd", "i'll", "i'm", "i'v", 'if', 'in', 'into',
              'is', "isn't", 'it', "it'", 'it', 'itself', "let'", 'me', 'more',
              'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of',
              'off', 'on', 'onc', 'onli', 'or', 'other', 'ought', 'our', 'our',
              'ourselv', 'out', 'over', 'own', 'same', "shan't", 'she',
              "she'd", "she'll", "she'", 'should', "shouldn't", 'so', 'some',
              'such', 'than', 'that', "that'", 'the', 'their', 'their', 'them',
              'themselv', 'then', 'there', "there'", 'these', 'thei', "they'd",
              "they'll", "they'r", "they'v", 'thi', 'those', 'through', 'to',
              'too', 'under', 'until', 'up', 'us', 'veri', 'wa', "wasn't", 'we',
              "we'd", "we'll", "we'r", "we'v", 'were', "weren't", 'what',
              "what'", 'when', "when'", 'where', "where'", 'which', 'while',
              'who', "who'", 'whom', 'why', "why'", 'with', "won't", 'would',
              "wouldn't", 'you', "you'd", "you'll", "you'r", "you'v", 'your',
              'your', 'yourself', 'yourselv']
