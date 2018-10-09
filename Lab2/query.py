from indexer import InvertedIndex
import pickle
import sys
sys.path.append("..") # Adds higher directory to python modules path.

from Lab1 import preprocess


def main(filename='sample.xml.pickle'):

    with open(filename, 'rb') as f:
        index_dict = pickle.load(f)
    index = InvertedIndex(index_dict)

    terms = index.get_terms()

    while(True):
        phrase = input("> ")

        if phrase.lower() == 'stop' or phrase.lower() == 'quit':
            break

        phrase = preprocess.prep_text(phrase)[0] # 1 word for now

        for term in terms:
            if phrase in term:
                print(index.str_term(term))

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
