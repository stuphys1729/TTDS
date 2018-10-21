import xml.etree.ElementTree as ET
import sys
sys.path.append("..") # Lets me use other labs as modules

import pickle
import time

from Lab1 import preprocess

# Change this to True to enable term position printing where possible
verbose_print = False

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

    def get_docs(self):
        return self.doc_lengths.keys()


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

    def single_search(self, num, term_pre, neg=False):

        term = self.prep_term(term_pre)
        if not term or term not in self.index: return

        docs = self.index[term][1]
        if neg:
            docs = self.get_docs() - docs.keys()

        self.print_results(num, docs)


    def conjunction(self, num, term1_pre, term2_pre, neg=0):

        if term1_pre[0] == '"':
            docs1 = self.phrase_search(term1_pre, True)
        else:
            term1 = self.prep_term(term1_pre)
            if not term1 or term1 not in self.index: return
            docs1 = self.index[term1][1]

        if term2_pre[0] == '"':
            docs2 = self.phrase_search(term2_pre, True)
        else:
            term2 = self.prep_term(term2_pre)
            if not term2 or term2 not in self.index: return
            docs2 = self.index[term2][1]

        if neg == 1:
            # Negate first
            docs1 = self.get_docs() - docs1.keys()
            all_docs = docs1 & docs2.keys()
        elif neg == 2:
            # Negate second
            docs2 = self.get_docs() - docs2.keys()
            all_docs = docs1.keys() & docs2
        else:
            all_docs = docs1.keys() & docs2.keys()

        self.print_results(num, all_docs)


    def disjunction(self, num, term1_pre, term2_pre, neg=0):

        if term1_pre[0] == '"':
            docs1 = self.phrase_search(term1_pre, True)
        else:
            term1 = self.prep_term(term1_pre)
            if not term1 or term1 not in self.index: return
            docs1 = self.index[term1][1]

        if term2_pre[0] == '"':
            docs2 = self.phrase_search(term2_pre, True)
        else:
            term2 = self.prep_term(term2_pre)
            if not term2 or term2 not in self.index: return
            docs2 = self.index[term2][1]

        if neg == 1:
            # Negate first
            docs1 = self.get_docs() - docs1.keys()
            all_docs = docs1 | docs2.keys()
        elif neg == 2:
            # Negate second
            docs2 = self.get_docs() - docs2.keys()
            all_docs = docs1.keys() | docs2
        else:
            all_docs = docs1.keys() | docs2.keys()

        self.print_results(num, all_docs)


    def phrase_search(self, num, phrase, internal=False):

        terms = preprocess.prep_text(phrase)
        if len(terms) == 2:
            return self.proximity_search(num, terms[0], terms[1], 1, True, internal)
        else:
            print("Phrase search for more than 2 term is not yet supported")


    def proximity_search(self, num, term1_pre, term2_pre, dist, order=False, internal=False):

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
                    if d <= dist and not order:
                        return_docs[doc].append((ti,tj))
                    j += 1
                else: # t2 ahead of t1
                    if d >= -dist:
                        return_docs[doc].append((ti,tj))
                    i += 1

        if internal:
            return return_docs

        if verbose_print:
            for doc in return_docs:
                if return_docs[doc] != []:
                    print("\t{0:>4}:({1:>2}) ".format(doc, len(return_docs[doc])), end='')
                    for i in return_docs[doc][:-1]:
                        print("({0},{1}), ".format(*i), end='')

                    print("({0},{1})".format(*return_docs[doc][-1]))
        else:
            self.print_results(num, return_docs)


    def print_results(self, num, return_docs):

        for doc in sorted(return_docs):
            print( "{0:>2} 0 {1:>5} 0 1 0".format(num, doc))


def main(filename="sample.xml"):

    tree = ET.parse(filename)
    root = tree.getroot()
    num_docs = len(root)

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

    # setup toolbar
    width = 50
    sys.stdout.write("Parsing {} documents: [{}]".format(num_docs, " " * width))
    sys.stdout.flush()
    sys.stdout.write("\b" * (width+1))
    prog_points = num_docs // width

    start = time.time()
    for i in range(num_docs):

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

        if i % prog_points == 0:
            sys.stdout.write("#")
            sys.stdout.flush()

    sys.stdout.write('\n')

    print("Writing index file {}...".format(filename + '.index'))
    with open(filename + '.index', 'w') as f:
        f.write(str(index)) # For visualisation

    print("Writing binary file {}...".format(filename + '.pickle'))
    with open(filename + '.pickle', 'wb') as f:
        pickle.dump((index.index, num_docs, index.doc_lengths), f) # For quick re-load

    taken = time.time() - start
    print("Produced index of {} documents in {:.1f} seconds".format(num_docs, taken))

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
