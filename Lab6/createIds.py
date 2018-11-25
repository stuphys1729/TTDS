import re
from nltk import RegexpTokenizer
from nltk.stem import PorterStemmer
from nltk.tokenize import TweetTokenizer
import sys
import requests
from lxml.html import fromstring
import lxml
from threading import Thread, Lock
from queue import Queue
import time

class Features(object):

    def __init__(self, _terms=None):
        self.terms = _terms if _terms else {}
        self.currId = 1

        # Initialise stemmer
        self.ps = PorterStemmer()

        # Get stop words
        with open('stops.txt', 'r') as f:
            self.stops = f.readlines()

        # stem the stop words
        for i in range(len(self.stops)):
            self.stops[i] = self.ps.stem( self.stops[i].rstrip('\r\n') )

        pattern =   r'''(?x)(
                    ([A-Z]\.)+
                    |\d+:\d+
                    |[@\#]?\w+(?:[-']\w+)*
                    |[\$\£]\d+(\.\d+)?%?
                    )
                    '''
        # Adapted from:
        # http://jeffreyfossett.com/2014/04/25/tokenizing-raw-text-in-python.html

        #self.tokenizer = RegexpTokenizer(pattern)
        self.tokenizer = TweetTokenizer(strip_handles=True, preserve_case=True)

    def get_tokens(self, sentence):
        #return [ x for x in list(sum(self.tokenizer.tokenize(sentence), ())) if x ]
        tokens = []
        toks = self.tokenizer.tokenize(sentence)
        extra = ''
        for tok in toks:
            if tok.startswith('http'):
                try:
                    r = requests.get(tok, timeout=1)
                except:
                    continue
                try:
                    tree = fromstring(r.content)
                except lxml.etree.ParserError as e:
                    continue

                try:
                    extra += tree.findtext('.//title')
                except TypeError as e:
                    continue

        if extra != '':
            toks += self.tokenizer.tokenize(extra)

        for tok in toks:

            try:
                stemmed = self.ps.stem(tok.lower())
            except UnicodeDecodeError:
                continue

            if stemmed not in self.stops:
                tokens.append( stemmed )
                if stemmed.startswith('#'):
                    tokens.append(stemmed[1:])


        return tokens

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

        with open(filename, 'wb') as f:
            f.write(dump.encode(encoding='utf_8'))

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


def old_main(filename="Tweets.14cat.train"):

    p_bar_width = 60

    # setup progress bar
    sys.stdout.write("[%s]" % (" " * p_bar_width))
    sys.stdout.flush()
    sys.stdout.write("\b" * (p_bar_width+1))

    features = Features()
    num_lines = sum(1 for line in open(filename))
    p_freq = int(num_lines/p_bar_width)
    i = 0
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
            i += 1
            if i % p_freq == 0:
                sys.stdout.write("#")
                sys.stdout.flush()

    sys.stdout.write('\n')
    features.dump_terms()

def doWork():
    global q
    global features
    global resDic
    global jLock
    global j
    global start
    while not start:
        time.sleep(0.1)

    while True:

        if q.empty():
            if not start:
                break
            else:
                continue

        num, line = q.get()
        try:
            id, tweet, cat = *line.split('\t'),
        except ValueError as e:
            if line == '\n':
                continue
            else:
                q.task_done()
                resDic[num] = []
                raise ValueError(line)

        toks = features.get_tokens(tweet)

        resDic[num] = toks

        q.task_done()
    jLock.acquire()
    try:
        j += 1
    finally:
        jLock.release()

def main(filename="Tweets.14cat.train"):

    p_bar_width = 60

    # setup progress bar
    sys.stdout.write("[%s]" % (" " * (p_bar_width+1)))
    sys.stdout.flush()
    sys.stdout.write("\b" * (p_bar_width+2))

    global features
    features = Features()

    with open(filename) as f:
        lines = f.readlines()

    num_lines = len(lines)
    p_freq = int(num_lines/p_bar_width)

    concurrent = 200
    global q
    q = Queue(4 * concurrent)

    global resDic
    resDic = {}

    global j
    j = 0
    global jLock
    jLock = Lock()

    global start
    start = False

    for i in range(concurrent):
        t = Thread(target=doWork)
        t.daemon = True
        t.start()

    try:
        for i, line in enumerate(lines):
            if i == (4 * concurrent) - 1:
                start = True
            q.put( (i, line) )
            if i % p_freq == 0:
                sys.stdout.write("#")
                sys.stdout.flush()
        start = False
        while j != concurrent:
            time.sleep(0.1)
    except KeyboardInterrupt:
        sys.exit(1)

    print("Main ready")

    sys.stdout.write('\n')

    for i in range(num_lines):
        for tok in resDic[i]:
            features.add_term(tok)

    features.dump_terms()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
