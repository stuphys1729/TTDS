import pickle
import sys
import re
sys.path.append("..") # Adds higher directory to python modules path.

from Lab1 import preprocess
from Lab2 import indexer

def load_index(filename):
    with open(filename, 'rb') as f:
        index_dict, N = pickle.load(f)
    return indexer.InvertedIndex(index_dict, N)


def main(filename='sample.xml.pickle'):

    index = load_index(filename)

    terms = index.get_terms()

    while(True):
        phrase = input("> ")

        if phrase.lower() == 'stop' or phrase.lower() == 'quit':
            break

        if 'AND' in phrase:
            qterms = re.split(r" AND ", phrase)
            index.conjunction(qterms[0], qterms[1])

        elif 'OR' in phrase:
            qterms = re.split(r' OR ', phrase)
            index.disjunction(qterms[0], qterms[1])

        elif phrase[0] == '"': # Start of a phrase that's not part of conditional
            index.phrase_search(phrase.strip('"'))

        else:
            phrase = preprocess.prep_text(phrase)[0] # 1 word for now

            for term in terms:
                if phrase == term:
                    print(index.str_term(term))

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
