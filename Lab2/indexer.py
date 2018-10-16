import xml.etree.ElementTree as ET
import sys
sys.path.append("..") # Lets me use other labs as modules

import pickle

from Lab1 import preprocess

class InvertedIndex(object):

    def __init__(self, index=None, N=0):
        self.index = index if index else {}
        self.N = N
        """
        Each entry in the index will be hashed by the term, resulting in a list.
        That list will itself contain:
            0: The document frequency of that term
            1: A dictionary of doc_num -> position list
        """

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
            string += '\t' + str(doc) + ':({}) '.format(num_times)
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
                    common_docs &= self.index[term]
            else:
                return # One term was not found at all
        if len(common_docs) == 0:
            return # all terms did not exist in any one document
        #else:
            # If we get this far, we need to check the order of terms


def main(filename="sample.xml"):

    tree = ET.parse(filename)
    root = tree.getroot()

    index = InvertedIndex()

    text_loc = -1
    head_loc = -1
    for i in range(len(root[0])):
        if root[0][i].tag.lower() == 'text':
            text_loc = i
        if root[0][i].tag.lower() == 'headline':
            head_loc = i

    for i in range(len(root)):
        if head_loc != -1 and text_loc != -1:
            terms = preprocess.prep_text( root[i][head_loc].text + root[i][text_loc].text )
        elif text_loc != -1:
            terms = preprocess.prep_text( root[i][text_loc].text )
        else:
            raise ValueError("Could not find collection text")
            
        for j in range(len(terms)):
            index.add_occurance(terms[j], i, j)

    with open(filename + '.index', 'w') as f:
        f.write(str(index)) # For visualisation

    with open(filename + '.pickle', 'wb') as f:
        pickle.dump((index.index, len(root)), f) # For quick re-load


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
