#Calculate various parameters of the HMM
from parse import parseFile
from parse import parseFileInput
from pprint import pprint
from collections import Counter
import os
import itertools


def count(tokens, tags, tag, token):
    ctr = 0
    for i in range (len(tokens)):
        if (tokens[i] == token) and (tags[i] == tag):
            ctr=ctr+1
    return ctr


def countc(tags1, state2, state1):
    tags = tags1[:]
    for i in range (len(tags)):
        if tags[i] == None:
            tags[i] = '#SPACE#'

    if state2 == 'STOP':
        state2 = '#SPACE#'
    if state1 == 'START':
        state1 = '#SPACE'

    if state1 == 'START' and state2 == 'STOP':
        return 0

    ctr = 0
    prev = None
    for i in tags:
        if prev==None:
            prev = i
        else:
            if i==state2:
                if prev==state1:
                    ctr+=1
        prev = i
    return ctr



def calculateEmission(tokens, tags, k=0):
    emissionParams = {}

    for i in range (len(tokens)):
        if (tokens.count(tokens[i])) < k:
            tokens[i] = '#UNK#'

    # print Counter(tokens)
    tokenset = set(tokens)
    tagset = set(tags)

    for i in tokenset:
        temp = {}
        for p in tagset:
            temp.update({p: 0})
        #print temp
        emissionParams.update({i:temp})

    ctr = 0
    lenz = float(len(emissionParams))
    for i in emissionParams:
        ctr+=1
        for p in tagset:
            emissionParams[i][p] = float(count(tokens, tags, p, i)/float(tags.count(p)))
        percent = float(ctr/lenz) * 100
        print(percent , "%" )            #Print percentage of emission parameters calculated

    #pprint(emissionParams)

    return emissionParams



def calculateTransmission(tags):
    transmissionParams = {}

    tagset = set(tags)
    tagset.remove(None)
    tagset.add('STOP')
    # pprint(tagset)    

    tagset2 = set(tags)
    tagset2.remove(None)
    tagset2.add('START')

    for i in tagset:
        temp = {}
        for p in tagset2:
            temp.update({p:None})
        transmissionParams.update({i : temp})

    for i in transmissionParams:
        for p in transmissionParams[i]:
            #print(i)
            ctr = i
            if i == 'START' or i=='STOP':
                ctr = None
            transmissionParams[i][p] = float(countc(tags,i,p)/float(tags.count(ctr)))
            # pprint(tags)

    #pprint(transmissionParams)

    # for i in range (len(tokens)):
    #     if tokens[i] == None:

    return transmissionParams



def viterbi(tags, tokens, observation):
    #emission[i][j]
    emission = calculateEmission(tokens, tags, 3)
    transmission = calculateTransmission(tags)

    tagset = set(tags)
    tagset.remove(None)
    tagset=list(tagset)
    
    viterbiPath = []
    backpointer = []

    for i in range (len(tagset)):
        temp = []
        temp.append(transmission[tagset[i]]['START'] * emission[tokens[0]][tagset[i]])
        viterbiPath.append(temp)
        temp = []
        temp.append(0)
        backpointer.append(temp)

    pprint(viterbiPath)
    pprint(backpointer)
    print("\n")

    # for i in range (1,len(observation)):
    #     for p in range (len(tagset)):
    #         viterbiPath[p].append()


def maximizer(tagset, viterbiO, transmissionO, emissionO, time):
    viterbi = viterbiO[:]
    transmission = transmissionO.copy()
    emission = emissionO.copy()

    values = []

    # for i in range (len(tagset)):
    #     values.append()




def simpleSentiment(trainingset, devin, devout):
    temp = parseFile(trainingset)
    tokens = temp[0]
    tags = temp[1]

    print("Training started.")
    emissionTable = calculateEmission(tokens, tags, 3)
    print("Training Completed.\n")

    inputTokens = parseFileInput(devin)
    inputTags = []
    pprint(inputTokens)

    # max(stats, key=stats.get)

    for i in inputTokens:
        if i == None:
            inputTags.append("#SPACE#")
        else:
            if i in emissionTable:
                inputTags.append(max(emissionTable[i], key=emissionTable[i].get))
            else:
                inputTags.append(max(emissionTable['#UNK#'], key=emissionTable['#UNK#'].get))

    pprint(inputTags)
    writeout(inputTokens,inputTags, '/Users/aditya/Desktop/Machine Learning/Project/MLProject/EN/EN/output')

    
def writeout(tokens, tags, filename):
    fo = open(filename, "w", encoding = 'utf-8')
    for i in range (len(tokens)):
        if tags[i] == "#SPACE#":
            fo.write("\n")
        else:
            towrite = tokens[i] + " " + tags[i] + "\n"
            fo.write(towrite)
    fo.close()



def main():
    # simpleSentiment('/Users/aditya/Desktop/Machine Learning/Project/MLProject/EN/EN/train','/Users/aditya/Desktop/Machine Learning/Project/MLProject/EN/EN/dev.in','/Users/aditya/Desktop/Machine Learning/Project/MLProject/EN/EN/dev.out')

    temp = parseFile('/Users/aditya/Desktop/Machine Learning/Project/MLProject/EN/EN/train')
    tokens = temp[0]
    tags = temp[1]

    # calculateTransmission(tags)
    # calculateEmission(tokens, tags, 3)
    # viterbi(tags, tokens)


    #Run this one for question 2
    simpleSentiment('/Users/aditya/Desktop/Machine Learning/Project/MLProject/EN/EN/train', '/Users/aditya/Desktop/Machine Learning/Project/MLProject/EN/EN/dev.in', '/Users/aditya/Desktop/Machine Learning/Project/MLProject/EN/EN/dev.out')


main()

