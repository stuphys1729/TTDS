from nltk.stem import PorterStemmer

#from nltk.tokenize import RegexpTokenizer
from .manualTokeniser import RegexpTokenizer
import sys

def main(filename="bible.txt"):

    with open(filename, 'r') as f:
        text = f.read() # Assumes it can all fit in memory

    tokens = prep_text(text)

    new_file = filename + '.preproc'
    with open(new_file, 'w') as f:
        for tok in tokens:
            f.write(tok + '\n')

def prep_text(text):

    # Initialise stemmer
    ps = PorterStemmer()

    # Get stop words
    with open('stops.txt', 'r') as f:
        stops = f.readlines()

    # stem the stop words
    for i in range(len(stops)):
        stops[i] = ps.stem( stops[i].rstrip('\r\n') )

    ## Tokenisation ##
    #pattern = r"[@\#]?\w+(?:[-']\w+)*"
    pattern =   r'''(?x)(
                ([A-Z]\.)+
                |\d+:\d+
                |(https?://)?(\w+\.)(\w{2,})+([\w/]+)?
                |[@\#]?\w+(?:[-']\w+)*
                |[\$\£]\d+(\.\d+)?%?
                )
                '''
    # Adapted from:
    # http://jeffreyfossett.com/2014/04/25/tokenizing-raw-text-in-python.html

    tokenizer = RegexpTokenizer(pattern)
    tokens = []

    for line in text.split('\n'):

        toks = tokenizer.tokenize(line)
        toks = [ x for x in list(sum(toks, ())) if x ]

        for tok in toks:

            try:
                stemmed = ps.stem(tok.lower())
            except UnicodeDecodeError:
                continue

            if stemmed not in stops:
                tokens.append( stemmed )

    return tokens



if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
