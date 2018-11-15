import re
from nltk import RegexpTokenizer
import sys


class Features(object):

    def __init__(self, _terms=None):
        self.terms = _terms if _terms else {}
        self.currId = 1
        pattern =   r'''(?x)(
                    ([A-Z]\.)+
                    |\d+:\d+
                    |[@\#]?\w+(?:[-']\w+)*
                    |[\$\£]\d+(\.\d+)?%?
                    )
                    '''
        # Adapted from:
        # http://jeffreyfossett.com/2014/04/25/tokenizing-raw-text-in-python.html

        self.tokenizer = RegexpTokenizer(pattern)

    def get_tokens(self, sentence):
        return [ x for x in list(sum(self.tokenizer.tokenize(sentence), ())) if x ]

    def add_terms(self, sentence):

        for tok in self.get_tokens(sentence):
            self.add_term(tok)

    def add_term(self, term):
        if term not in self.terms:
            self.terms[term] = self.currId
            self.currId += 1

    def dump_terms(self, filename="feats.dic"):
        dump = ""
        for term in self.terms:
            dump += term + '\t' + str(self.terms[term]) + '\n'

        with open(filename, 'w') as f:
            f.write(dump)

    def load_from_file(filename='feats.dic'):
        terms = {}
        with open(filename, 'r') as f:
            for line in f:
                term, id = *line.split('\t'),
                terms[term] = int(id)
        return Features(terms)

    def get_id(self, term):
        if term not in self.terms:
            return -1
        else:
            return self.terms[term]


def main(filename="Tweets.14cat.train"):

    features = Features()
    with open(filename, 'r') as f:
        for line in f:
            try:
                id, tweet, cat = *line.split('\t'),
            except ValueError as e:
                if line == '\n':
                    continue
                else:
                    raise ValueError(line)

            features.add_terms(tweet)

    features.dump_terms()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
