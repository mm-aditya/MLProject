#parser for the input files
from pprint import pprint


def parseFile(filepath = "EN/EN/train"):

	fo = open(filepath, "r")
	tokenlist = []

	token = []
	tag = []
	ctr = 0

	for line in fo:
		#print "Line is: ", line
		temp = line.split()
		tokenlist.append(temp)
		if(len(temp)!=0):
			token.append(temp[0])
			tag.append(temp[1])
		else:
			token.append(None)
			tag.append(None)

	del tokenlist[len(tokenlist)-1]
	# pprint(tokenlist)
	# pprint(token)
	fo.close()

	return [token,tag]


def parseFileInput(filepath = "EN/EN/train"):

	fo = open(filepath, "r")
	tokenlist = []

	token = []
	ctr = 0

	for line in fo:
		#print "Line is: ", line
		temp = line.split()
		tokenlist.append(temp)
		if(len(temp)!=0):
			token.append(temp[0])
		else:
			token.append(None)

	del tokenlist[len(tokenlist)-1]
	# pprint(tokenlist)
	# pprint(token)
	fo.close()

	return token


# parseFile()