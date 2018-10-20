import sys
sys.path.append("..") # Lets me use other labs as modules

import pickle
import numpy as np
import re

from Lab1 import preprocess
from Lab2 import query

def main(filename='sample.xml.pickle', queryfile=None):

    index = query.load_index(filename)
    all_terms = index.get_terms()

    if queryfile:
        with open(queryfile, 'r') as f:
            for line in f:
                print(line.rstrip('\n'))
                m = re.search(r'(\d+) (.*)', line)
                process_query( index, all_terms, int(m.group(1)), m.group(2) )

    else:
        qno = 1
        while(True):
            phrase = input("> ")

            if phrase.lower() == 'stop' or phrase.lower() == 'quit':
                break

            if len(phrase) == 0 or all( [t not in all_terms for t in phrase] ):
                continue

            process_query(index, all_terms, qno, phrase)

            qno += 1


def process_query(index, all_terms, num, phrase):

    phrase = preprocess.prep_text(phrase)

    rel_docs = set()
    indices  = []
    for term in phrase:
        if term in all_terms:
            rel_docs |= index.index[term][1].keys()
            indices.append( index.index[term] )

    results = []
    for doc in rel_docs:
        score = 0
        for i in range(len(phrase)):
            df = indices[i][0]
            if doc in indices[i][1]:
                tf = len(indices[i][1][doc])
                score += (1 + np.log10(tf)) * np.log10(index.N / df)
        results.append( (doc, score) )

    results = np.array(results, dtype=[('doc', int), ('score', float)])
    results.sort(order='score')

    for doc in reversed(results):
        print( "{0:>2} 0 {1:>5} 0 {2:.4f} 0".format(num, *doc))


if __name__ == '__main__':

    if len(sys.argv) == 2:
        main(sys.argv[1])

    elif len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])

    else:
        main()
