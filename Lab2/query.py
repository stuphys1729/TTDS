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


def main(filename='sample.xml.pickle', queryfile=None):

    index = load_index(filename)

    terms = index.get_terms()

    if queryfile:
        with open(queryfile, 'r') as f:
            for line in f:
                #print(line.rstrip('\n'))
                m = re.search(r'(\d+) (.*)', line)
                process_query( index, terms, m.group(1), m.group(2) )

    else:
        qno = 1
        while(True):
            phrase = input("> ")

            if phrase.lower() == 'stop' or phrase.lower() == 'quit':
                break

            process_query(index, terms, qno, phrase)


def process_query(index, terms, num, phrase):

        if ' AND ' in phrase:
            qterms = re.split(r" AND ", phrase)
            if qterms[0][:4] == 'NOT ':
                index.conjunction(num, qterms[0][4:], qterms[1], 1)
            elif qterms[1][:4] == 'NOT ':
                index.conjunction(num, qterms[0], qterms[1][4:], 2)
            else:
                index.conjunction(num, qterms[0], qterms[1])

        elif ' OR ' in phrase:
            qterms = re.split(r' OR ', phrase)
            if qterms[0][:4] == 'NOT ':
                index.disjunction(num, qterms[0][4:], qterms[1], 1)
            elif qterms[1][:4] == 'NOT ':
                index.disjunction(num, qterms[0], qterms[1][4:], 2)
            else:
                index.disjunction(num, qterms[0], qterms[1])

        elif phrase[0] == '"': # Start of a phrase that's not part of conditional
            index.phrase_search(num, phrase.strip('"'))

        elif phrase[0] == '#':
            first_split = phrase.split('(')
            dist = int( first_split[0][1:] )
            prox_terms = first_split[1].split(',')

            index.proximity_search(num, prox_terms[0], prox_terms[1], dist)

        else: # Assume single term query
            if phrase[:4] == 'NOT ':
                index.single_search(num, phrase[4:], True)
            else:
                index.single_search(num, phrase)


if __name__ == '__main__':

    if len(sys.argv) == 2:
        main(sys.argv[1])

    elif len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])

    else:
        main()
