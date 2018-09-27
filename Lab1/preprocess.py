from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize, RegexpTokenizer
import sys

def main(filename="bible.txt"):

    # Initialise stemmer
    ps = PorterStemmer()

    # Get stop words
    with open('stops.txt', 'r') as f:
        stops = f.readlines()

    # Should we stem the stop words?
    for i in range(len(stops)):
        stops[i] = ps.stem( stops[i].rstrip('\r\n') )

    ## Tokenisation ##
    tokens = []
    tokenizer = RegexpTokenizer(r'\w+') # Only keep alpha-numeric (no periods)
    with open(filename, 'r') as f:
        for line in f:
            """
            toks = line.split() # default call splits on all punctuation
            for i in range(len(toks)): # apart from period (.)
                toks[i] = toks[i].rstrip('.').lower()
            tokens += toks
            """

            toks = tokenizer.tokenize(line)

            for tok in toks:

                try:
                    stemmed = ps.stem(tok.lower())
                except UnicodeDecodeError:
                    continue

                if stemmed not in stops:
                    tokens.append( stemmed )

    print(tokens[:5])

    new_file = filename + '.preproc'
    with open(new_file, 'w') as f:
        for tok in tokens:
            f.write(tok + '\n')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
