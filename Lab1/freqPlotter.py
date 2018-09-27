import sys
import matplotlib.pyplot as plt
import seaborn as sns

def main(filename='bibterms.freq'):

    freqs = []
    with open(filename, 'r') as f:
        for line in f:
            freqs.append( int(line.split()[0]) )

    ranks = list(reversed(range(len(freqs))))

    plt.loglog(ranks, freqs)
    plt.title("Zipf")
    plt.show()

    plt.clf()

    fdigits = [ str(freq)[0] for freq in freqs ]
    sns.countplot(x=fdigits)
    plt.title('Bedford')
    plt.show()

    plt.clf()

    fdigits2 = [ str(freq)[0] for freq in freqs if freq > 9 ]
    sns.countplot(x=fdigits2)
    plt.title('Bedford No Singles')
    plt.show()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
