import sys
import numpy as np

def main(test_file='feats.test', pred_file='pred.out'):

    actual_class = []
    with open(test_file, 'r') as f:
        for line in f:
            actual_class.append(int(line.split(' ')[0]))

    predictions = []
    with open(pred_file, 'r') as f:
        for line in f:
            predictions.append([float(x) if '.' in x else int(x) for x in line.split(' ')])

    assert( len(actual_class) == len(predictions) )
    N = len(actual_class) # == len(predictions)

    num_right = 0
    for i in range(len(actual_class)):
        if actual_class[i] == predictions[i][0]:
            num_right += 1

    print("Accuracy = {0:.3f}".format(num_right / N))

    ind_each_class = {x: set() for x in range(1, 15)}
    for i in range(N):
        ind_each_class[actual_class[i]].add(i)
        # We now have the sets of relevent documents

    ind_pred_class = {x: set() for x in range(1, 15)}
    for i in range(N):
        ind_pred_class[predictions[i][0]].add(i)
        # And the sets of retrieved documents

    #for c in ind_pred_class:
    #    print(c, ind_pred_class[c])

    prec_per_class = []
    rec_per_class  = []
    for i in range(1, 15):
        if (len(ind_pred_class[i]) == 0):
            prec_per_class.append(0)
            rec_per_class.append(0)
        else:
            prec_per_class.append( len(ind_each_class[i] & ind_pred_class[i])
                                    / len(ind_pred_class[i]) )
            rec_per_class.append(  len(ind_each_class[i] & ind_pred_class[i])
                                    / len(ind_each_class[i]) )

    f_measures = []
    for i in range(14):
        P = prec_per_class[i]
        R = rec_per_class[i]
        if (P == 0 or R == 0):
            f_measures.append(0)
        else:
            f_measures.append( 2*P*R / (P + R) )

    macroF = np.mean(f_measures)

    print("Macro-F1 = {0:.3f}".format(macroF))

    for c in range(14):
        print("{0:>2}: P={1:.3f} R={2:.3f} F={3:.3f}".format(c+1, prec_per_class[c],
                                                    rec_per_class[c], f_measures[c]))



if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(*sys.argv[1:])
    else:
        main()
