from pprint import pprint


def parseTrainFile(filepath):

	fo = open(filepath, "r", encoding='utf-8')

	token = []
	tag = []

	# #First line
	# token.append(None)
	# tag.append('START')

	for line in fo:
		temp = line.split()

		if(len(temp)!=0):
			token.append(temp[0])
			tag.append(temp[1])
		else:
			token.append(None)
			tag.append(None)

	fo.close()

	return [token,tag]

def parseFileInput(filepath):
	fo = open(filepath, "r", encoding = 'utf-8')

	token = []

	for line in fo:
		temp = line.split()
		if(len(temp)!=0):
			token.append(temp[0])
		else:
			token.append(None)

	fo.close()

	return token

def parseMMInput(filepath):
	fo = open(filepath, "r", encoding = 'utf-8')

	inputTweets = []
	tweet = []

	for line in fo:
		temp = line.split()
		if(len(temp)!=0):
			tweet.append(temp[0])
		else:
			inputTweets.append(tweet)
			tweet = []

	fo.close()

	return inputTweets	

def parseTrainP5(filepath):

	fo = open(filepath, "r", encoding='utf-8')

	token = []
	tag = []

	# #First line
	# token.append(None)
	# tag.append('START')

	for line in fo:
		temp = line.split()

		if(len(temp)!=0):
			token.append(temp[0].lower())
			tag.append(temp[1])
		else:
			token.append(None)
			tag.append(None)

	fo.close()

	return [token,tag]

def parseInputP5(filepath):
	fo = open(filepath, "r", encoding = 'utf-8')

	inputTweets = []
	tweet = []

	for line in fo:
		temp = line.split()
		if(len(temp)!=0):
			tweet.append(temp[0].lower())
		else:
			inputTweets.append(tweet)
			tweet = []

	fo.close()

	return inputTweets	