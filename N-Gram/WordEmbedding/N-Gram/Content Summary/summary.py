# -*- coding: utf-8 -*-
# import urllib2

import re
import string
import operator

""" Check if a word is an common word
@:param ngram -- the word to be checked
@:return boolean -- check result 
"""
def isCommon(ngram):
    commonWords = ["the", "be", "and", "of", "a", "in", "to", "have",
                   "it", "i", "that", "for", "you", "he", "with", "on", "do", "say",
                   "this", "they", "is", "an", "at", "but","we", "his", "from", "that",
                   "not", "by", "she", "or", "as", "what", "go", "their","can", "who",
                   "get", "if", "would", "her", "all", "my", "make", "about", "know",
                   "will","as", "up", "one", "time", "has", "been", "there", "year", "so",
                   "think", "when", "which", "them", "some", "me", "people", "take", "out",
                   "into", "just", "see", "him", "your", "come", "could", "now", "than",
                   "like", "other", "how", "then", "its", "our", "two", "more", "these",
                   "want", "way", "look", "first", "also", "new", "because", "day", "more",
                   "use", "no", "man", "find", "here", "thing", "give", "many", "well"]

    if ngram in commonWords:
        return True
    else:
        return False

""" Clean up the text 
@:param input -- the file content
@:return input -- the cleaned file content
"""
def cleanText(input):
    # Substitute "\n" change line label with " " space
    input = re.sub('\n+', " ", input).lower()
    # Remove reference labels in form "[1]"
    input = re.sub('\[[0-9]*\]', "", input)
    # Substitute continuous multiple spaces into one space
    input = re.sub(' +', " ", input)
    # Change the characters/bytes into UTF-8 format to ignore conflict
    # Note that when inputing an source of string, an encoding method is required
    input = bytes(input, 'utf-8')
    input = input.decode("ascii", "ignore")
    # Output the cleaned content
    return input

""" Filter the file content 
@:param input -- the file content
@:return -- the cleaned file content
"""
def cleanInput(input):
    # Firstly we clean the text content
    input = cleanText(input)
    # Then we split the file content by spaces
    cleanInput = []
    input = input.split(' ')
    # Clean up reductent space/punctuation/...
    # And add up useful content information
    for item in input:
        # Use string.punctuation to get all the punctuations labels
        item = item.strip(string.punctuation)
        # Filter out letters including "i" and "a"
        if len(item) > 1 or (item.lower() == 'a' or item.lower() == 'i'):
            cleanInput.append(item)
    return cleanInput

""" Get N-gram pair dict with frequency
@:param input -- the file content
@:param n -- the variable "n" for n-gram
@:return -- dictionary which key=NGramPair, value=Frequency
"""
def getNgrams(input, n):
    # Firstly we clean our input
    input = cleanInput(input)

    # Construct Dictionary
    output = {}
    for i in range(len(input)-n+1):
        ngramTemp = " ".join(input[i:i+n])#.encode('utf-8')

        # We only consider the situation when the 2-gram pair does not contain common words
        if isCommon(ngramTemp.split()[0]) or isCommon(ngramTemp.split()[1]):
            pass
        else:
            # Word frequency summary
            if ngramTemp not in output:
                output[ngramTemp] = 0
            output[ngramTemp] += 1
    return output

# Get the sentense the core word stays
def getFirstSentenceContaining(ngram, content):
    # print(ngram)
    sentences = content.split(".")
    for sentence in sentences:
        if ngram in sentence:
            return sentence
    return ""


""" Main 
The main method to run our tasks
"""
if __name__ == "__main__":

    # Define the FileName to be runned
    filename = "AugurationSpeech.txt"

    '''Method 1: Read from the website'''
    # content = urllib2.urlopen(urllib2.Request("http://pythonscraping.com/files/inaugurationSpeech.txt")).read()
    '''Method 2: Read from local files'''
    file = open(filename, "r")
    content = file.read()
    # Get N-Gram pair dicts
    ngrams = getNgrams(content, 2)
    # Sort the words by frequency
    # "reverse=True" means reverse order (Big->Small)
    sortedNGrams = sorted(ngrams.items(), key=operator.itemgetter(1), reverse=True)
    # print(sortedNGrams)
    for top3 in range(3):
        print ("===" + getFirstSentenceContaining(sortedNGrams[top3][0], content.lower()) +" ===")
    # Close the file
    file.close()
