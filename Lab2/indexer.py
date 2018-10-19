import xml.etree.ElementTree as ET
import sys
sys.path.append("..") # Lets me use other labs as modules

import pickle

from Lab1 import preprocess

class InvertedIndex(object):

    def __init__(self, index=None, N=0, doc_lengths=None):
        self.index = index if index else {}
        self.N = N
        self.doc_lengths = doc_lengths if doc_lengths else {}
        """
        Each entry in the index will be hashed by the term, resulting in a list.
        That list will itself contain:
            0: The document frequency of that term
            1: A dictionary of doc_num -> position list
        """

    def add_doc_length(self, doc_num, length):
        self.doc_lengths[doc_num] = length

    def add_occurance(self, term, doc_num, location):

        if term in self.index:
            entry = self.index[term]
            if doc_num not in entry[1]:
                entry[0] += 1
                entry[1][doc_num] = [location]
            else:
                entry[1][doc_num].append(location)

        else:
            entry = [1, { doc_num: [location] }]
            self.index[term] = entry


    def get_terms(self):
        return sorted([ k for k in self.index ])


    def str_term(self, term):
        string = ''
        string += "{}:({})\n".format(term, self.index[term][0])

        for doc in self.index[term][1]:
            num_times = len(self.index[term][1][doc])
            string += '\t{0:>4}:({1:>2}) '.format(doc, num_times)
            for i in range(num_times - 1):
                string += str(self.index[term][1][doc][i]) + ', '
            string += str(self.index[term][1][doc][-1]) + '\n'


        return string


    def __str__(self):
        string = ""
        for term in sorted(self.index):
            string += self.str_term(term)

            #string += ('-' * 60) + '\n'

        return string

    def prep_term(self, term_pre):

        term = preprocess.prep_text(term_pre)
        if term:
            return term[0]
        else:
            return # This was a stop word

    def conjunction(self, term1_pre, term2_pre):

        term1 = self.prep_term(term1_pre)
        term2 = self.prep_term(term2_pre)
        if not term1 or not term2:
            return # One or both were stop words

        docs1 = self.index[term1][1]
        docs2 = self.index[term2][1]

        common_docs = docs1.keys() & docs2.keys()

        for doc in common_docs:
            print("document {}:".format(doc))
            # Print 1st term occurances
            print("\t" + term1 + ": ", end='')
            for i in range(len(docs1[doc]) - 1):
                print("{}, ".format(docs1[doc][i]), end='')
            print( docs1[doc][-1] )
            # Print 2nd term occurances
            print("\t" + term2 + ": ", end='')
            for i in range(len(docs2[doc]) - 1):
                print("{}, ".format(docs2[doc][i]), end='')
            print( docs2[doc][-1] )


    def disjunction(self, term1_pre, term2_pre):

        term1 = self.prep_term(term1_pre)
        term2 = self.prep_term(term2_pre)
        if not term1 or not term2:
            return # One or both were stop words

        docs1 = self.index[term1][1]
        docs2 = self.index[term2][1]

        all_docs = docs1.keys() | docs2.keys()

        for doc in all_docs:
            print("document {}:".format(doc))
            if doc in docs1:
                print("\t" + term1 + ": ", end='')
                for i in range(len(docs1[doc]) - 1):
                    print("{}, ".format(docs1[doc][i]), end='')
                print( docs1[doc][-1] )
            if doc in docs2:
                print("\t" + term2 + ": ", end='')
                for i in range(len(docs2[doc]) - 1):
                    print("{}, ".format(docs2[doc][i]), end='')
                print( docs2[doc][-1] )


    def phrase_search(self, phrase):

        terms = preprocess.prep_text(phrase)
        common_docs = {}
        first = True
        for term in terms:
            if term in self.index:
                if first:
                    common_docs = set(self.index[term][1].keys())
                    first = False
                else:
                    common_docs &= self.index[term][1].keys()
            else:
                return # One term was not found at all

        if len(common_docs) == 0:
            return # all terms did not exist in any one document
        else:
            # If we get this far, we need to check the order of terms
            pot_docs = {}
            for doc in common_docs:
                order = []
                for term in terms:
                    order.append(self.index[term][1][doc])
                pot_docs[doc] = order

            return_docs = {}
            for doc in pot_docs:
                for i in pot_docs[doc][0]:
                    if (i+1) in pot_docs[doc][1]:
                        # We have found the phrase
                        if doc in return_docs:
                            return_docs[doc].append(i)
                        else:
                            return_docs[doc] = [i]

            for doc in return_docs:
                print("{0}: ".format(doc), end='')
                for i in return_docs[doc]:
                    print("{0}-{1} ".format(i, i+1), end='')
                print('')


    def proximity_search(self, term1_pre, term2_pre, dist):

        term1 = self.prep_term(term1_pre)
        term2 = self.prep_term(term2_pre)

        common_docs = {}
        first = True
        for term in [term1, term2]:
            if term in self.index:
                if first:
                    common_docs = set(self.index[term][1].keys())
                    first = False
                else:
                    common_docs &= self.index[term][1].keys()
            else:
                return # One term was not found at all

        if len(common_docs) == 0:
            return # both terms did not exist in any one document
        else:
            # If we get this far, we need to check the position of terms
            pot_docs = {}
            for doc in common_docs:
                order = []
                for term in [term1, term2]:
                    order.append(self.index[term][1][doc])
                pot_docs[doc] = order
                
        return_docs = {doc: [] for doc in pot_docs}
        for doc in pot_docs:
            i = 0
            j = 0 # Linear Merge
            while (i < len(pot_docs[doc][0])) and (j < len(pot_docs[doc][1])):

                ti = pot_docs[doc][0][i]
                tj = pot_docs[doc][1][j]
                d = ti - tj
                if d > 0: # t1 ahead of t2
                    if d <= dist:
                        return_docs[doc].append((ti,tj))
                    j += 1
                else: # t2 ahead of t1
                    if d >= -dist:
                        return_docs[doc].append((ti,tj))
                    i += 1

        for doc in return_docs:
            if return_docs[doc] != []:
                print("\t{0:>4}:({1:>2}) ".format(doc, len(return_docs[doc])), end='')
                for i in return_docs[doc][:-1]:
                    print("({0},{1}), ".format(*i), end='')

                print("({0},{1})".format(*return_docs[doc][-1]))


def main(filename="sample.xml"):

    tree = ET.parse(filename)
    root = tree.getroot()

    index = InvertedIndex()

    text_loc  = -1
    head_loc  = -1
    docno_loc = -1
    for i in range(len(root[0])):
        if root[0][i].tag == 'TEXT':
            text_loc = i # Annoyingly this changes
        if root[0][i].tag == 'HEADLINE':
            head_loc = i
        if root[0][i].tag == 'DOCNO':
            docno_loc = i

    if text_loc == -1:
        raise ValueError("Could not find collection text")

    for i in range(len(root)):

        # Some security against structure change
        if root[i][text_loc].tag != 'TEXT':
            for j in range(len(root[i])):
                if root[i][j].tag == 'TEXT':
                    text_loc = j

        if docno_loc != -1 and root[i][docno_loc].tag != 'DOCNO':
            for j in range(len(root[i])):
                if root[i][j].tag == 'DOCNO':
                    docno_loc = j

        if head_loc != -1:
            terms = preprocess.prep_text( root[i][head_loc].text + root[i][text_loc].text )
        else:
            terms = preprocess.prep_text( root[i][text_loc].text )

        # Default doc numbering
        if docno_loc != -1:
            docno = int(root[i][docno_loc].text)
        else:
            docno = i

        index.add_doc_length(docno, len(terms))

        for j in range(len(terms)):
            index.add_occurance(terms[j], docno, j)

    with open(filename + '.index', 'w') as f:
        f.write(str(index)) # For visualisation

    with open(filename + '.pickle', 'wb') as f:
        pickle.dump((index.index, len(root)), f) # For quick re-load


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
