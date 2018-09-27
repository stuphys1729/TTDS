from nltk.tokenize import word_tokenize, RegexpTokenizer
import matplotlib.pyplot as plt
import sys
from scipy.optimize import minimize
from scipy.stats import chisquare
import numpy as np


def main(filename="bible.txt"):

    tokenizer = RegexpTokenizer(r'\w+') # Only keep alpha-numeric (no periods)

    with open(filename, 'r') as f:
        lines = f.readlines()

    n = 0
    v = 0
    n_list = [0]
    v_list = [0]
    terms = set()

    for line in lines:
        toks = tokenizer.tokenize(line)

        for tok in toks:
            n += 1
            if tok not in terms:
                terms.add(tok)
                v += 1

        if v > v_list[-1] + 200:
            n_list.append(n)
            v_list.append(v)

    fig, ax = plt.subplots()

    plt.scatter(n_list, v_list)

    def heaps(params):
        k = params[0]
        b = params[1]

        pred = [ k*n**b for n in n_list ]
        diff = [ (v_list[i] - pred[i])**2 for i in range(len(pred)) ]
        return sum(diff)
        #return chisquare(pred, f_exp=v_list)

    #print( heaps([2, 0.65]) )
    vals = minimize(heaps, [2, 0.65])
    print(vals.x)

    k = vals.x[0]
    b = vals.x[1]
    pred = [ k*n**b for n in n_list ]

    plt.plot(n_list, pred, color='r')

    plt.title('Heap\'s Law - The bible')
    props = dict(boxstyle='round', facecolor='g', alpha=0.3)
    text = "k = {0:.3f}\nb = {1:.3f}".format(k,b)
    ax.text(0.78, 0.15, text, transform=ax.transAxes, fontsize=14,
            verticalalignment='top', bbox=props)
    plt.savefig('HeapsLaw.png', dpi=300)
    plt.show()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
