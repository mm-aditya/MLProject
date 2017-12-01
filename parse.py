#parser for the input files
from pprint import pprint


def parseTrainFile(filepath):

	fo = open(filepath, "r", encoding='utf-8')

	token = []
	tag = []

	#First line
	token.append(None)
	tag.append('START')

	for line in fo:
		temp = line.split()

		if(len(temp)!=0):
			token.append(temp[0])
			tag.append(temp[1])
		else:
			token.append(None)
			token.append(None)
			tag.append('STOP')
			tag.append('START')

	#Last line
	token.append(None)
	tag.append('STOP')
	tag.append('END')

	fo.close()

	return [token,tag]

def parseFileInput(filepath):
	fo = open(filepath, "r", encoding = 'utf-8')

	token = []

	for line in fo:
		#print "Line is: ", line
		temp = line.split()
		if(len(temp)!=0):
			token.append(temp[0])
		else:
			token.append(None)

	fo.close()

	return token
# parseFile()