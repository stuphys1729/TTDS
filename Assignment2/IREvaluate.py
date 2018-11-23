import sys
import numpy as np
import re
from ast import literal_eval


def main(filename="S1.results"):

    def put_val(val):
        print("{0:.3f}\t".format(val), end='')

    relList = RelevenceList()
    results = ResultList(filename)
    queryNums = relList.getQueries()

    meanPat10 = meanRat50 = meanrP = MAP = meannDCG10 = meannDCG20 = 0

    print("\tP@10\tR@50\tr-Precision\tAP\tnDCG@10\tnDCG@20")
    for qNum in queryNums:
        print(qNum, '\t', sep='', end='')
        relDocsScores = relList.get_rel_docs(qNum) # tuples of (docNo, relScore)
        relDocsDict = { x[0]: x[1] for x in relDocsScores } # map of docNo to relScore
        relDocs = [ x[0] for x in relDocsScores ] # list of docNo

        assert(len(relDocs) > 0) # There must be at least 1 relevent document

        returnedDocsScores = results.get_returned_docs(qNum) # (docNo, rank, score)
        returnedDocs = [ x[0] for x in returnedDocsScores ] # list of docNo

        # P@10
        first10 = set(returnedDocs[:10])
        Pat10 = len(set(relDocs) & first10) / 10
        put_val(Pat10)
        meanPat10 += Pat10

        # R@50
        first50 = set(returnedDocs[:50])
        Rat50 = len(set(relDocs) & first50) / len(relDocs)
        put_val(Rat50)
        meanRat50 += Rat50

        # r-Precision
        firstR = set(returnedDocs[:len(relDocs)])
        rP = len(set(relDocs) & firstR) / len(relDocs)
        put_val(rP)
        meanrP += rP

        # AP
        relLocs = [] # Locations of relevent documents in returned list
        for doc in relDocs:
            if doc in returnedDocs:
                relLocs.append(returnedDocs.index(doc))

        foundDocs = 0
        AP = 0
        for i in range(len(relDocs)):
            if i in relLocs:
                foundDocs += 1
                AP += foundDocs/ (i+1)
        AP /= len(relDocs)
        put_val(AP)
        MAP += AP

        # nDCG@k
        def nDCGatK(k):
            DCGatK = 0
            for i in range(k):
                if i >= len(returnedDocs):
                    break
                rel = relDocsDict[returnedDocs[i]] if returnedDocs[i] in relDocs else 0
                if i == 0:
                    DCGatK += rel
                else:
                    DCGatK += rel / np.log2(i+1)

            iDCGatK = 0
            idealRels = sorted( [ relDocsDict[x] for x in relDocs ], reverse=True)
            for i in range(len(relDocs)):
                if i == 0:
                    iDCGatK += idealRels[0]
                else:
                    iDCGatK += idealRels[i] / np.log2(i+1)

            return DCGatK / iDCGatK

        nDCGat10 = nDCGatK(10)
        put_val(nDCGat10)
        meannDCG10 += nDCGat10

        nDCGat20 = nDCGatK(20)
        print("{0:.3f}\n".format(nDCGat20), end='')
        meannDCG20 += nDCGat20

    # End loop over queries
    meanPat10 /= len(queryNums)
    meanRat50 /= len(queryNums)
    meanrP /= len(queryNums)
    MAP /= len(queryNums)
    meannDCG10 /= len(queryNums)
    meannDCG20 /= len(queryNums)

    print("mean\t{0:.3f}\t{1:.3f}\t{2:.3f}\t{3:.3f}\t{4:.3f}\t{5:.3f}".format(
        meanPat10, meanRat50, meanrP, MAP, meannDCG10, meannDCG20))



class ResultList(object):

    def __init__(self, filename):
        self.parse_results(filename)

    def parse_results(self, filename):
        """
        This function parses the file stating the results produced by an IR
        system in the following format:

        <query_number> 0 <doc_number> <rank_of_doc> <score> 0
        <query_number> 0 <doc_number> <rank_of_doc> <score> 0
        ...

        where each of the <> terms are replaced by the appropriate values and
        the whitespace between values is a single space (' ')
        """
        self.results = {}
        with open(filename, 'r') as f:
            for line in f:
                qNo, _, docNo, rank, score, _ = literal_eval(
                                            '[' + line.replace(' ', ',') + ']')
                if qNo in self.results:
                    self.results[qNo].append( (docNo, rank, score) )
                else:
                    self.results[qNo] = [ (docNo, rank, score) ]

    def get_returned_docs(self, qNum):

        return self.results[qNum]


class RelevenceList(object):

    def __init__(self, filename='qrels.txt'):
        self.parse_rel_docs(filename)

    def parse_rel_docs(self, filename):
        """
        This function parses the file stating which documents are relevent to each
        query. It expects the format to be as follows:

        <qNo>: (<docNo1>, <doc1Rel>) (<docNo2>, <doc2Rel>) ...
        <qNo>: (<docNo1>, <doc1Rel>) (<docNo2>, <doc2Rel>) ...
        ...

        where each of the <> terms are replaced by the appropriate values and the
        whitespace between each tuple is a single space (' ').
        """
        self.queries = {}
        with open(filename, 'r') as f:
            for line in f:
                m = re.search(r'(\d+:) (.*)', line)
                qNo = int(m.group(1)[:-1])
                rel_docs = literal_eval( '[' +  m.group(2).replace(' ', ',') + ']' )
                self.queries[qNo] = rel_docs

    def get_rel_docs(self, qNum):

        return self.queries[qNum]

    def getQueries(self):
        return list(sorted(self.queries.keys()))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
