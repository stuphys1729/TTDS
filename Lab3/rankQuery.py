import sys
sys.path.append("..") # Lets me use other labs as modules

import pickle
import numpy as np

from Lab1 import preprocess
from Lab2 import query

def main(filename='sample.xml.pickle'):

    index = query.load_index(filename)
    all_terms = index.get_terms()

    qno = 1

    while(True):
        phrase = input("> ")

        if phrase.lower() == 'stop' or phrase.lower() == 'quit':
            break

        phrase = preprocess.prep_text(phrase)

        if len(phrase) == 0 or all( [t not in all_terms for t in phrase] ):
            continue

        else:

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
                print( "{0:>2} 0 {1:>5} 0 {2:.4f} 0".format(qno, *doc))

            qno += 1



if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
