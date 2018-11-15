import sys
from createIds import Features


def get_class_ids(filename):
    ids = {}
    with open(filename, 'r') as f:
        for line in f:
            className, id = *line.split('\t'),
            ids[className] = int(id)
    return ids


def main(rawFile='Tweets.14cat.train', featuresFile='feats.dic', classIdsFile='classIDs.txt'):

    features = Features.load_from_file(featuresFile)
    classIds = get_class_ids(classIdsFile)

    returnString = ""
    with open(rawFile, 'r') as f:
        for line in f:
            try:
                id, tweet, cat = *line.split('\t'),
            except ValueError as e:
                if line == '\n':
                    continue
                else:
                    raise ValueError(line)
            returnString += str(classIds[cat.rstrip('\n')]) + ' '

            tokSet = set()
            for tok in features.get_tokens(tweet):
                tokId = features.get_id(tok)
                if tokId != -1:
                    tokSet.add(tokId)

            for tok in sorted(tokSet):
                returnString += str(tok) + ':1 '

            returnString += '#' + str(id) + '\n'

    if rawFile.endswith('.train'):
        dumpFile = 'feats.train'
    elif rawFile.endswith('.test'):
        dumpFile = 'feats.test'

    with open(dumpFile, 'w') as f:
        f.write(returnString)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(*sys.argv[1:])
    else:
        main()
