import sys
from createIds import Features
from threading import Thread, Lock
from queue import Queue
import time

def get_class_ids(filename):
    ids = {}
    with open(filename, 'r') as f:
        for line in f:
            className, id = *line.split('\t'),
            ids[className] = int(id)
    return ids


def old_main(rawFile='Tweets.14cat.train', featuresFile='feats.dic', classIdsFile='classIDs.txt'):

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

def doWork():
    global q
    global features
    global classIds
    global resDic
    global jLock
    global j
    global start
    while not start:
        time.sleep(0.1)

    while True:

        if q.empty():
            if not start:
                break
            else:
                continue

        returnString = ''
        num, line = q.get()
        try:
            id, tweet, cat = *line.split('\t'),
        except ValueError as e:
            if line == '\n':
                continue
            else:
                q.task_done()
                resDic[num] = ''
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
        resDic[num] = returnString

        q.task_done()
    jLock.acquire()
    try:
        j += 1
    finally:
        jLock.release()

def main(rawFile='Tweets.14cat.train', featuresFile='feats.dic', classIdsFile='classIDs.txt'):

    p_bar_width = 60

    # setup progress bar
    sys.stdout.write("[%s]" % (" " * (p_bar_width+1)))
    sys.stdout.flush()
    sys.stdout.write("\b" * (p_bar_width+2))

    global features
    features = Features.load_from_file(featuresFile)
    global classIds
    classIds = get_class_ids(classIdsFile)

    with open(rawFile, 'r') as f:
        lines = f.readlines()

    num_lines = len(lines)
    p_freq = int(num_lines/p_bar_width)

    concurrent = 100
    global q
    q = Queue(4 * concurrent)

    global resDic
    resDic = {}

    global j
    j = 0
    global jLock
    jLock = Lock()

    global start
    start = False

    for i in range(concurrent):
        t = Thread(target=doWork)
        t.daemon = True
        t.start()

    try:
        for i, line in enumerate(lines):
            if i == (2 * concurrent) - 1:
                start = True
            q.put( (i, line) )
            if i % p_freq == 0:
                sys.stdout.write("#")
                sys.stdout.flush()
        start = False
        while j != concurrent:
            time.sleep(0.1)
    except KeyboardInterrupt:
        sys.exit(1)

    sys.stdout.write('\n')

    print("Main ready")

    if rawFile.endswith('.train'):
        dumpFile = 'feats.train'
    elif rawFile.endswith('.test'):
        dumpFile = 'feats.test'

    returnString = ''
    for i in range(num_lines):
        returnString += resDic[i]

    with open(dumpFile, 'w') as f:
        f.write(returnString)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(*sys.argv[1:])
    else:
        main()
