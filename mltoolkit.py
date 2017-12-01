#Calculate various parameters of the HMM
from parse import parseTrainFile
from parse import parseFileInput
from pprint import pprint
from collections import Counter
import os
import itertools

######################
# Model Trainer     
######################

def countTags(tags):
    tagset = set(tags)

    countT = {}
    for t in tagset:
        countT[t] = 0

    for t in tags:
        countT[t] +=1

    return countT

def calculateEmission(tags, tokens, k=0):
    """
    Train the emission parameter of the model from a given sequence of tags (training data)
    
    Parameters
    ----------
    tags,token      : list
        Sequence of corresponding tags and tokens from training data

    k               : integer
        Learning threshold for the token (if the token appear less than k times, it is considered unknown token)

    Returns
    -------
    emissionParams  : list
        Emission parameter of the trained model

    """
    #Horizontal label
    tokenset = set(tokens)
    tokenset.remove(None)
    tokenset.add('#UNK#')

    #Label words that appear less than k times as #UNK#
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
            if countTokens[t] < k:
                tokens[c] = '#UNK#'

    #Updated Horizontal label
    tokenset = set(tokens)
    tokenset.remove(None)

    #Vertical label
    tagset = set(tags)
    tagset.remove(None)

    #Initialize emission probability table
    emissionParams = {}
    for j in tagset:
        temp = {}
        for o in tokenset:
            temp.update({o: 0})
        emissionParams.update({j:temp})

    countT = countTags(tags)

    #Count the emission of o by j
    for c in range(len(tokens)):
        if tokens[c] == None:
            pass
        else:
            emissionParams[tags[c]][tokens[c]] += 1

    #Calculate the emission probability   
    for j in emissionParams:
        for o in emissionParams[j]:
            emissionParams[j][o] = float(emissionParams[j][o])/float(countT[j])

    return emissionParams

def calculateTransition(tags):
    """
    Train the transition parameter of the model from a given sequence of tags (training data)
    
    Parameters
    ----------
    tags            : list
        Sequence of tags from training data

    Returns
    -------
    transitionParams: list
        Transition parameter of the trained model

    """

    #Vertical label
    tagset = set(tags)
    tagset.remove(None)
    tagset.add('START')

    #Horizontal label
    tagset2 = set(tags)
    tagset2.remove(None)
    tagset2.add('STOP')

    #Initialize transition probability table
    transitionParams = {}
    for i in tagset:
        temp = {}
        for p in tagset2:
            temp.update({p:0})
        transitionParams.update({i : temp})

    #Count the number of times the tags appear
    countT = countTags(tags)

    #Count the number of transition
    for c, t in enumerate(tags):
        #Start of first sentence
        if c == 0:
            transitionParams['START'][t] +=1

        #End of sentence
        elif t == None:
            transitionParams[tags[c-1]]['STOP'] += 1

        else:
            #Start of new sentence
            if tags[c-1] == None:
                transitionParams['START'][t] +=1
            #Recursion
            else:
                transitionParams[tags[c-1]][t] += 1

    #Calculate the transition probability
    for i in transitionParams:
        for j in transitionParams[i]:
            if i != 'START' and j != 'STOP':
                transitionParams[i][j] = float(transitionParams[i][j])/float(countT[i])

    return transitionParams

######################
# Algorithm          
######################

def simple(inputTokens, emissionParams):
    """
    Simple sentiment analysis to decode the most likely tag for a given token by choosing the highest emission probability by a tag for each token
    If the trained model doesn't recognise the word, use the #UNK# emission probability
    
    Parameters
    ----------
    inputTokens     : list
        List of input tokens

    emissionParams  : list
        Emission probability - emissionParams(j)(o) <==> probability of word o being generated by tag j

    Returns
    -------
    predictedTags   : list
        List of predicted tags for input tokens

    """
    predictedTags = []

    for i in inputTokens:
        if i == None:
            predictedTags.append(None)

        else:
            tempMaxProb = 0
            tempTag = ''


            for j in emissionParams:
                if i in emissionParams[j]:
                    if emissionParams[j][i] > tempMaxProb:
                        tempMaxProb = emissionParams[j][i]
                        tempTag = j
                else:
                    if emissionParams[j]['#UNK#'] > tempMaxProb:
                        tempMaxProb = emissionParams[j]['#UNK#']
                        tempTag = j

            predictedTags.append(tempTag)

    return predictedTags

def viterbi(inputTokens, transitionParams, emissionParams):
    """
    Viterbi decoding algorithm to predict the most likely tag sequence for the given tokens
    If the trained model doesn't recognise the word, use the parameter for #UNK# 
    
    Parameters
    ----------
    inputTokens     : list
        List of input tokens

    emissionParams  : list
        Emission probability - emissionParams(j)(o) <==> probability of word o being generated by tag j

    Returns
    -------
    predictedTags   : list
        List of predicted tags for input tokens

    """
    tagset = []
    for t in emissionParams:
        tagset.append(t)

    #Get path probability table
    piTable = []

    for count, token in enumerate(inputTokens):
        currentPi = []

        if token not in emissionParams['O'] and token != None:
            token = '#UNK#'
        
        #Initialization
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

        #Termination
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

        else:
            #Re-initialization
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

            #Recursion
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

    #Backward step
    tempPredictedTags = []
    backpointer = 'X'

    tempPredictedTags.append('START')

    for i in reversed(piTable):
        if len(i) == 1:
            backpointer = i[0][1]
        elif backpointer == 'X':
            pass
        else:
            backpointer = i[backpointer][1]

        tempPredictedTags.append(backpointer)

    #Trim the first tag
    tempPredictedTags = tempPredictedTags[:-1]

    predictedTags = []

    for i in reversed(tempPredictedTags):
        if i == 'X':
            predictedTags.append('O')
        elif i == 'START':
            predictedTags.append(None)
        else:
            predictedTags.append(tagset[i])

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

######################
# Helper Functions   
######################

def writeout(tokens, tags, filename):
    fo = open(filename, "w", encoding = 'utf-8')
    for i in range (len(tokens)):
        if tokens[i] == None:
            fo.write("\n")
        else:
            towrite = tokens[i] + " " + tags[i] + "\n"
            fo.write(towrite)
    fo.close()

def simpleSentimentAnalysis(train, devin, devout):
    traindata = parseTrainFile(train)
    tokens = traindata[0]
    tags = traindata[1]

    emissionParams = calculateEmission(tags, tokens, 3)

    inputTokens = parseFileInput(devin)

    #writecheck(inputTokens, 'modifiedInput')

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

def main():
    #For debugging

    simpleSentimentAnalysis('C:/Users/Bellabong/MLProject/EN/train', 'C:/Users/Bellabong/MLProject/EN/dev.in', 'C:/Users/Bellabong/MLProject/output/EN/dev.p2.out')
    viterbiSentimentAnalysis('C:/Users/Bellabong/MLProject/EN/train', 'C:/Users/Bellabong/MLProject/EN/dev.in', 'C:/Users/Bellabong/MLProject/output/EN/dev.p3.out')

    simpleSentimentAnalysis('C:/Users/Bellabong/MLProject/FR/train', 'C:/Users/Bellabong/MLProject/FR/dev.in', 'C:/Users/Bellabong/MLProject/output/FR/dev.p2.out')
    viterbiSentimentAnalysis('C:/Users/Bellabong/MLProject/FR/train', 'C:/Users/Bellabong/MLProject/FR/dev.in', 'C:/Users/Bellabong/MLProject/output/FR/dev.p3.out')

    simpleSentimentAnalysis('C:/Users/Bellabong/MLProject/CN/train', 'C:/Users/Bellabong/MLProject/CN/dev.in', 'C:/Users/Bellabong/MLProject/output/CN/dev.p2.out')
    viterbiSentimentAnalysis('C:/Users/Bellabong/MLProject/CN/train', 'C:/Users/Bellabong/MLProject/CN/dev.in', 'C:/Users/Bellabong/MLProject/output/CN/dev.p3.out')

    simpleSentimentAnalysis('C:/Users/Bellabong/MLProject/SG/train', 'C:/Users/Bellabong/MLProject/SG/dev.in', 'C:/Users/Bellabong/MLProject/output/SG/dev.p2.out')
    viterbiSentimentAnalysis('C:/Users/Bellabong/MLProject/SG/train', 'C:/Users/Bellabong/MLProject/SG/dev.in', 'C:/Users/Bellabong/MLProject/output/SG/dev.p3.out')
    #maxMarginalSentimentAnalysis('C:/Users/Bellabong/MLProject/EN/train', 'C:/Users/Bellabong/MLProject/EN/dev.in', 'C:/Users/Bellabong/MLProject/EN/dev.p4.out')    

main()

######################
# How to use the program  
######################

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

