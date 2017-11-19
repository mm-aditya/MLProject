#Calculate various parameters of the HMM
from parse import parseFile
from parse import parseFileInput
from pprint import pprint
from collections import Counter



def count(tokens, tags, tag, token):
	ctr = 0
	for i in range (len(tokens)):
		if (tokens[i] == token) and (tags[i] == tag):
			ctr=ctr+1
	return ctr


def calculateEmission(tokens, tags, k=0):
	emissionParams = {}

	for i in range (len(tokens)):
		if (tokens.count(tokens[i])) < k:
			tokens[i] = '#UNK#'
			tags[i] = None

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
	 	print percent , "%"				#Print percentage of emission parameters calculated

	return emissionParams



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
				inputTags.append(None)
	



def main():
	simpleSentiment("EN/EN/train","EN/EN/dev.in","EN/EN/dev.out")



main()

