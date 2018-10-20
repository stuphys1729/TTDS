import pickle
import sys
import re
sys.path.append("..") # Adds higher directory to python modules path.

from Lab1 import preprocess
from Lab2 import indexer

def load_index(filename):
    with open(filename, 'rb') as f:
        index_dict, N, doc_lengths = pickle.load(f)
    return indexer.InvertedIndex(index_dict, N, doc_lengths)


def main(filename='sample.xml.pickle'):

    index = load_index(filename)

    terms = index.get_terms()

    while(True):
        phrase = input("> ")

        if phrase.lower() == 'stop' or phrase.lower() == 'quit':
            break

        if ' AND ' in phrase:
            qterms = re.split(r" AND ", phrase)
            if qterms[0][:4] == 'NOT ':
                index.conjunction(qterms[0][4:], qterms[1], 1)
            elif qterms[1][:4] == 'NOT ':
                print("Got here")
                index.conjunction(qterms[0], qterms[1][4:], 2)
            else:
                index.conjunction(qterms[0], qterms[1])

        elif ' OR ' in phrase:
            qterms = re.split(r' OR ', phrase)
            if qterms[0][:4] == 'NOT ':
                index.disjunction(qterms[0][4:], qterms[1], 1)
            elif qterms[1][:4] == 'NOT ':
                index.disjunction(qterms[0], qterms[1][4:], 2)
            else:
                index.disjunction(qterms[0], qterms[1])

        elif phrase[0] == '"': # Start of a phrase that's not part of conditional
            index.phrase_search(phrase.strip('"'))

        elif phrase[0] == '#':
            first_split = phrase.split('(')
            dist = int( first_split[0][1:] )
            prox_terms = first_split[1].split(',')

            index.proximity_search(prox_terms[0], prox_terms[1], dist)

        else: # Assume single term query
            if phrase[:4] == 'NOT ':
                index.single_search(phrase[4:], True)
            else:
                index.single_search(phrase)
                

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
