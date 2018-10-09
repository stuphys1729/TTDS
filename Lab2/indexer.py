import xml.etree.ElementTree as ET
import sys
sys.path.append("..") # Adds higher directory to python modules path.

import pickle

from Lab1 import preprocess

class InvertedIndex(object):

    def __init__(self, index=None):
        self.index = index if index else {}
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
        string += "{}: {}\n".format(term, self.index[term][0])

        for doc in self.index[term][1]:
            string += ('\t' + str(doc) + ': '
                        + str(self.index[term][1][doc]) + '\n')

        return string


    def __str__(self):
        string = ""
        for term in sorted(self.index):
            string += self.str_term(term)

            string += ('-' * 60) + '\n'

        return string


def main(filename="sample.xml"):

    tree = ET.parse(filename)
    root = tree.getroot()

    index = InvertedIndex()

    text_loc = -1
    for i in range(len(root[0])):
        if root[0][i].tag.lower() == 'text':
            text_loc = i
            break

    for i in range(len(root)):
        terms = preprocess.prep_text( root[i][text_loc].text )
        for j in range(len(terms)):
            index.add_occurance(terms[j], i, j)

    with open(filename + '.pickle', 'wb') as f:
        pickle.dump(index.index, f)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
