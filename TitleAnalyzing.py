#!/usr/bin/python

print "Hacker practical python code - Lilly !!!"

### Library imports ###

import sys, getopt, os
import time
import numpy as np
import urllib
import re
import difflib
import csv
import matplotlib.pyplot as plt

### FUNCTIONS ####

def log(msg):
	print msg

def readURL(url):
	log("-> read from "+ url)
	f = urllib.urlopen(url)
	fContent = f.read()
	return fContent

def readURLTitle(url):
	log("-> read from "+ url)
	f = urllib.urlopen(url)
	fContent = ""
	for i in range(1000):	#Read up to 1000 lines or until </title> have been found
		fLine = f.readline()
		fContent = fContent + fLine
		if(fLine.find("</title>") >= 0):
			break
	return fContent

def compareSTR(str1, str2): #Returns ratio
	s1w = re.findall('\w+', str1.lower())
	s2w = re.findall('\w+', str2.lower())
	common_ratio = difflib.SequenceMatcher(None, s1w, s2w).ratio()
	#print '%.1f%% of words common.' % (100*common_ratio)
	return common_ratio

def findTitle(s):
	idx1 = s.find("<title>")
	idx2 = s.find("</title>")
	return s[idx1+7:idx2]



## CONFIGURATION ##
URL_File = "URLs.csv"
Class_Folder = "classifier"

## MAIN ##
listTitle = list()
listUrl = list()

## Read URL CSV file and get
#	- Title (column 3)
#	- URL (column 4)
f = open(URL_File, 'rb')
reader = csv.reader(f)
try:
   for row in reader:
	if len(row) > 4:
	  if len(row[3])>0:
		listTitle.append(row[3])
		listUrl.append(row[4])
except csv.Error, e:
   sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))

listTitle = listTitle[1:]
#get unique list elements
listTitle = list(set(listTitle))
## temporary limit length to 1000
if len(listTitle) > 1000:
	listTitle = listTitle[1:1001]

length = len(listTitle)
print "Length: ", length

#Create Heatmap of Ratio between words of Title
if False:# Temporarily disabled
	plt.figure(1)

	compArr = np.zeros((length, length))

	for i, title1 in enumerate(listTitle):
		for j, title2 in enumerate(listTitle[i:]):
			compArr[i,j+i] = compareSTR(title1, title2)

	plt.imshow(compArr, cmap='hot', interpolation='nearest')
	plt.ion()
	plt.show()

##Clustering
Words = re.findall('\w+', ' '.join(listTitle).lower())

if True: #Apply ignore list
	print "Apply ignore list"
	ignoreWords = np.genfromtxt("ignore.csv", delimiter=',', dtype="str")
	Words = [w for w in Words if w not in ignoreWords]

UniqueWords = list(set(Words))
CounterArr = np.zeros((length, len(Words)))
log("Counter array shape (titles, unique words) = "+str(CounterArr.shape))
for i, title in enumerate(listTitle):
	titleWords = re.findall('\w+', title.lower())
	#log("TitleWords: "+str(titleWords))
	for word in titleWords:	
		if word in UniqueWords:
			idx = UniqueWords.index(word)
			CounterArr[i, idx] += 1


WordCounter = np.sum(CounterArr, axis=0, dtype=int)
#Sort
SortIdx = np.argsort(WordCounter)[::-1]
log("Most (#10) used UniqueWords: "+str( [UniqueWords[i] for i in SortIdx[0:10]] ))
CounterArr = np.asarray([CounterArr[:,i] for i in SortIdx], dtype=int).T
#limit words to words that come more than n times
QualityWordLimit = 3
Indexes_QWords = np.array(np.where(WordCounter > QualityWordLimit), dtype=int)[0,:]
QualityWords = [UniqueWords[i] for i in Indexes_QWords]
QualityWordCounter = [WordCounter[i] for i in Indexes_QWords]
QCounterArr = np.asarray([CounterArr[:,i] for i in Indexes_QWords], dtype=int).T

if False:
	plt.figure(2)
	plt.imshow(QCounterArr, cmap='hot_r', interpolation='nearest')
	plt.title("Show amount of word count where words > "+str(QualityWordLimit))
	plt.xlabel("Quality words index")
	plt.ylabel("Title index")
	plt.ion()
	plt.show()

## classification part ###
print "\nClassification:"
ClassFiles = os.listdir(Class_Folder)
for ClassF in ClassFiles:
	if ClassF.endswith(".csv"):
		counter = 0
		#print "Read:",Class_Folder+"/"+ClassF
		className = ClassF[:-4]
		classWords = np.genfromtxt(Class_Folder+"/"+ClassF, delimiter=',', dtype="str")
		print "Class("+className+"):", len(classWords), "words"
		for word in Words:
			if word in classWords:
				counter = counter+1
		print "--> Counter:",counter
		print "---"
		

