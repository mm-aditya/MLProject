#Calculate various parameters of the HMM
from parse import parseTrainFile
from parse import parseFileInput
from pprint import pprint
from collections import Counter
import os
import itertools

def countTags(tags):
    tagset = set(tags)
    tagset.remove('STOP')
    tagset.remove('END')

    countT = {}
    for t in tagset:
        countT[t] = 0

    for c, t in enumerate(tags):
        if t == 'STOP' or t == 'END':
            pass

        #handle multiple line breaks
        elif t == 'START' and tags[c+1] == 'STOP':
            pass

        else:
            countT[t] +=1

    return countT

def writeout(tokens, tags, filename):
    fo = open(filename, "w", encoding = 'utf-8')
    for i in range (len(tokens)):
        if tokens[i] == None:
            fo.write("\n")
        else:
            towrite = tokens[i] + " " + tags[i] + "\n"
            fo.write(towrite)
    fo.close()

def calculateEmission(tags, tokens, k=0):
    #horizontal label
    tokenset = set(tokens)
    tokenset.remove(None)
    tokenset.add('#UNK#')

    #label words that appear less than k times as #UNK#
    countTokens = {}
    for t in tokenset:
        countTokens[t] = 0

    for t in tokens:
        if t == None:
            pass
        else:
            countTokens[t] +=1

    for c, t in enumerate(tokens):
        if t == None:
            pass
        else:
            if countTokens[t]<k:
                tokens[c] = '#UNK#'

    #vertical label
    tagset = set(tags)
    tagset.remove('START')
    tagset.remove('STOP')
    tagset.remove('END')

    #initialize emission probability table
    emissionParams = {}
    for j in tagset:
        temp = {}
        for o in tokenset:
            temp.update({o: 0})
        #print temp
        emissionParams.update({j:temp})

    countT = countTags(tags)

    #count the emission of o by j
    for c in range(len(tokens)):
        if tokens[c] == None: #or tokens[c] == '#UNK#':
            pass
        else:
            emissionParams[tags[c]][tokens[c]] += 1

    #calculate the actual emission probability   
    for j in emissionParams:
        for o in emissionParams[j]:
            emissionParams[j][o] = float(emissionParams[j][o])/float(countT[j])

    #pprint(emissionParams)

    return emissionParams

def calculateTransition(tags):
    #pprint(tags)

    #vertical label
    tagset = set(tags)
    tagset.remove('STOP')
    tagset.remove('END')

    #horizontal label
    tagset2 = set(tags)
    tagset2.remove('START')
    tagset2.remove('END')

    #initialize transition probability table
    transitionParams = {}
    for i in tagset:
        temp = {}
        for p in tagset2:
            temp.update({p:0})
        transitionParams.update({i : temp})

    #initialize total count 
    countT = countTags(tags)

    #count transition i-j
    for c, t in enumerate(tags):
        if tags[c+1] == 'END':
            break

        if t == 'STOP' or (t == 'START' and tags[c+1] == 'STOP') :
            pass

        else:
            transitionParams[t][tags[c+1]] += 1

    #calculate the actual transition probability
    for i in transitionParams:
        for j in transitionParams[i]:
            transitionParams[i][j] = float(transitionParams[i][j])/float(countT[i])

    #pprint(transitionParams)

    return transitionParams

def simple(inputTokens, emissionParams):
    predictedTags = []

    for i in inputTokens:
        if i == None:
            predictedTags.append("#SPACE#")
        else:
            tempMaxProb = 0
            tempTag = '#UNK#'

            for j in emissionParams:
                if i in emissionParams[j]:
                    if emissionParams[j][i] > tempMaxProb:
                        tempMaxProb = emissionParams[j][i]
                        tempTag = j

            predictedTags.append(tempTag)

    return predictedTags

def viterbi(inputTokens, transitionParams, emissionParams):

    #generate tagset from emission table label
    tagset = []
    for t in emissionParams:
        tagset.append(t)

    #get path probability table
    piTable = []

    for count, token in enumerate(inputTokens):
        currentPi = []

        if token not in emissionParams['O'] and token != None:
            token = '#UNK#'
        
        #print(count,token)
        
        #initialization
        if count == 0:
            for v in tagset:
                pikv = []
                pistart = transitionParams['START'][v]*emissionParams[v][token]
                pikv.append(pistart)
                if pistart > 0:
                    pikv.append('START')
                else:
                    pikv.append('X')
                currentPi.append(pikv)

        #termination
        elif token == None:
            maxPi = 0
            tempPointer = 'X'
            for c, p in enumerate(piTable[count-1]):
                pikv = []
                if p[1] == 'X': #path is already terminated
                    pass
                else:
                    pi = p[0]*transitionParams[tagset[c]]['STOP']
                    if maxPi < pi:
                        maxPi = pi
                        tempPointer = c
            pikv.append(maxPi)
            pikv.append(tempPointer)
            currentPi.append(pikv)

        #handle extra blank lines
        #elif token == None and inputTokens[count-1] != None:


        else:
            #re-initialization
            if inputTokens[count-1] == None:
                for v in tagset:
                    pikv = []
                    pistart = transitionParams['START'][v]*emissionParams[v][token]
                    pikv.append(pistart)
                    if pistart > 0:
                        pikv.append('START')
                    else:
                        pikv.append('X')
                    currentPi.append(pikv)

            #recursion
            else:           
                for v in tagset:
                    maxPi = 0
                    tempPointer = 'X'
                    for c, p in enumerate(piTable[count-1]):
                        pikv = []
                        if p[1] == 'X': #path is already terminated
                            pass
                        else:
                            pi = p[0]*transitionParams[tagset[c]][v]*emissionParams[v][token]
                            if maxPi < pi:
                                maxPi = pi
                                tempPointer = c
                    pikv.append(maxPi)
                    pikv.append(tempPointer)
                    currentPi.append(pikv)

        piTable.append(currentPi)

    #backward
    tempPredictedTags = []
    backpointer = 'X'

    tempPredictedTags.append('START')

    #adding last tag
    for i in reversed(piTable):
        if len(i) == 1:
            backpointer = i[0][1]
            #print ('Its a stop')
        elif backpointer == 'X':
            #print ('Non Entity')
            pass
        else:
            #print ('Its NOT a stop')
            backpointer = i[backpointer][1]

        tempPredictedTags.append(backpointer)

    tempPredictedTags = tempPredictedTags[:-1]

    predictedTags = []

    for i in reversed(tempPredictedTags):
        if i == 'X':
            predictedTags.append('#UNK#')
        elif i == 'START':
            predictedTags.append('#SPACE#')
        else:
            predictedTags.append(tagset[i])

    #pprint(predictedTags)
    return predictedTags

def maxMarginal (inputTokens, transitionParams, emissionParams):
    #generate tagset from emission table label
    tagset = []
    for t in emissionParams:
        tagset.append(t)

    #forward scores
    forward = []
    prevAlpha = {}
    for count, token in enumerate(inputTokens):
        currAlpha = {}
        for u in tagset:
            #initialization
            if count == 0:
                currAlpha[u] = transitionParams['START'][u]
            #recursion
            else:
                #check whether transition prob is u-v or v-u
                currAlpha[u] = sum(prevAlpha[v]*transitionParams[u][v]*emissionParams[u][token] for v in tagset)
        #record forward score for the current count/token
        forward.append(currAlpha)
        prevAlpha = currAlpha

    #termination
    forward.append(sum(prevAlpha[v] * transitionParams[v]['STOP'] for v in tagset ))

    #backward scores
    backward = []
    prevBeta = {}
    for count, token in enumerate(reversed(inputTokens[1:])):
        currBeta = {}
        for u in tagset:
            #initialization
            if count == 0:
                currBeta[u] = transitionParams[u]['STOP']
            #recursion
            else:
                currBeta[u]  = sum(prevBeta[v]*transitionParams[u][v]*emissionParams[u][token] for v in tagset)
        #record backward score for the current count/token
        backward.append(currBeta)
        prevBeta = currBeta

    #termination
    backward.append(sum(prevBeta[v] * transitionParams['START'][v] * emissionParams for v in tagset ))

    #combine forward and backward scores to find max-marginal score
    combined = []

    #choose best path

    return   

def simpleSentimentAnalysis(train, devin, devout):
    traindata = parseTrainFile(train)
    tokens = traindata[0]
    tags = traindata[1]

    emissionParams = calculateEmission(tags, tokens, 3)

    inputTokens = parseFileInput(devin)

    predictedTags = simple(inputTokens, emissionParams)

    writeout(inputTokens, predictedTags, devout)

def viterbiSentimentAnalysis(train, devin, devout):
    traindata = parseTrainFile(train)
    tokens = traindata[0]
    tags = traindata[1]

    emissionParams = calculateEmission(tags, tokens, 3)
    transitionParams = calculateTransition(tags)

    inputTokens = parseFileInput(devin)

    predictedTags = viterbi(inputTokens, transitionParams, emissionParams)

    writeout(inputTokens, predictedTags, devout)

def maxMarginalSentimentAnalysis(train, devin, devout):
    traindata = parseTrainFile(train)
    tokens = traindata[0]
    tags = traindata[1]

    emissionParams = calculateEmission(tags, tokens, 3)
    transitionParams = calculateTransition(tags)

    inputTokens = parseFileInput(devin)

def kViterbiSentimentAnalysis(train, devin, devout):
    pass

def main():
    #simpleSentimentAnalysis('C:/Users/Bellabong/MLProject/EN/train', 'C:/Users/Bellabong/MLProject/EN/dev.in', 'C:/Users/Bellabong/MLProject/EN/dev.p2.out')
    viterbiSentimentAnalysis('C:/Users/Bellabong/MLProject/EN/train', 'C:/Users/Bellabong/MLProject/EN/dev.in', 'C:/Users/Bellabong/MLProject/EN/dev.p3.out')
    #maxMarginalSentimentAnalysis('C:/Users/Bellabong/MLProject/EN/train', 'C:/Users/Bellabong/MLProject/EN/dev.in', 'C:/Users/Bellabong/MLProject/EN/dev.p4.out')    
main()

'''
How to use the program

'''
# if len(sys.argv) < 4:
#     print ('Supported Algorithm: simple | viterbi | maxmarginal | kviterbi')
#     print ('Supporter Language: EN | FR | CN | SG')
#     print ('How to use: sentimenttool.pyc algorithm language inputFilePath outputFilePath')
#     print ("Example of usage: sentimenttool.pyc simple EN C:/Users/Bellabong/MLProject/EN/dev.in C:/Users/Bellabong/MLProject/EN/dev.p3.out")
#     sys.exit()

# algorithm = sys.argv[1]
# language = sys.argv[2]
# devin = sys.argv[3]
# devout = sys.argv[4]

# #Retrieve path of training set of the selected language

# train = ''

# if language == 'EN':
#     train = 'C:/Users/Bellabong/MLProject/EN/train'

# elif language == 'FR':
#     train = 'C:/Users/Bellabong/MLProject/FR/train'

# elif language == 'CN':
#     train = 'C:/Users/Bellabong/MLProject/CN/train'

# elif language == 'SG':
#     train = 'C:/Users/Bellabong/MLProject/SG/train'

# else:
#     print ('Language is not supported')
#     print ('Supporter Language: EN | FR | CN | SG')
#     sys.exit()

# print ('Training is completed')

# #Run the selected algorithm and perform sentiment analysis

# if algorithm == 'simple':
#     simpleSentimentAnalysis(train, devin, devout)

# elif algorithm == 'viterbi':
#     viterbiSentimentAnalysis(train, devin, devout)

# elif algorithm == 'maxmarginal':
#     maxMarginalSentimentAnalysis(train, devin, devout)

# elif algorithm == 'kviterbi':
#     kViterbiSentimentAnalysis(train, devin, devout)

# else:
#     print ('Algorithm is not supported')
#     print ('Supported Algorithm: simple | viterbi | maxmarginal | kviterbi')
#     sys.exit()

