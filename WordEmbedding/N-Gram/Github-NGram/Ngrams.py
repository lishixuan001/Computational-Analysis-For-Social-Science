#Program that generates sentences based on bigrams

import re
import random
mydata = open('movies.txt','r').read().split()


def preprocess(data):
  """function takes in corpus and makes everything lowercase
      and removes punctuation."""
  #convert to lowercase
  lower=[re.sub('A-Z','a-z',x ) for x in data]
  #remove all non alphanumeric chars  and empty strings
  return filter(None, [re.sub(r'\W','',x) for x in lower])



def get_counts(data):
   """function takes a list of strings
   creates a dictionary of bigrams with their counts as values 
   and a dictionary of unigrams and their counts as values"""
       
   bigrams = {}
   unigrams = {}
   #range is len-1 because the bigram uses ith+1 element
   for i in range(0, len(data)-1):
      #ith element and ith+1 element
       bigram=(data[i],data[i+1])
       if(bigram in bigrams):
           count=bigrams[bigram]
           bigrams[bigram]= count+1
       else:
          #if bigram not in dict of bigrams, add with count 1
           bigrams[bigram]=1
           
   for unigram in data:
       if(unigram in unigrams):
           count=unigrams[unigram]
           unigrams[unigram]= count+1
       else:
          #if unigram not present, add with count 1
           unigrams[unigram]=1
                 
   return bigrams,unigrams

def build_bigram_model(data):
   """function takes a list of strings and produces a model
   which is a dictionary with a bigram key and probablility 
   of the bigram as the value."""

   bigrams,unigrams = get_counts(data)
   model = {}
   for bigram in bigrams:
       uni_count=unigrams[bigram[0]]
       bi_count=bigrams[bigram]
       
       #probability is bigram count divided by unigram count
       model[bigram]=(bi_count/float(uni_count))
   return model

def get_sentence_probability(model,sentence):
   """function takes a dictionary model and string sentence (all lowercase
   , no punctuation) and produces the probablity of the sentence (float)"""
   probs = []
   for i in range(0, len(sentence)-1):
       bigram=(sentence[i],sentence[i+1])
       if bigram in model:
          probs.append(model[bigram])
      #case if bigram is not in corpus
       else:
          probs.append(0)
   prob=1
   #loop through all the prob values and multiply
   for num in probs:
       prob=prob*num
    
   return prob

def generate_sentence(model):
   """The function generates a random sentence of a random length. 
   The first word is chosen by picking a random bigram.
   The following words are taken by using the second word in a bigram 
   and making a list of all keys with that word as the first word in a bigram.
   A bigram from the list is picked randonmly.
   This process repeats until the sentence is the appropriate length. """

   sentence=[]
   #sentences between 2 and 15 words
   length= random.randint(2,15)
   keys=model.keys()
   bigram=random.choice(keys)
   #iterate until sentence is correct length
   for i in range(0,length):
      matches=[]
      found=False
      while not found:
         
         #search in keys for key[0] to match the bigram[1]
         for key in keys:
            regex=re.compile(r"\b%s\b"%bigram[1])
            result=regex.match(key[0])
            if result:
               matches.append(key)
               found=True
               
         #if no match, choose another bigram to try
         if not found:
             bigram=random.choice(keys)
             
      #add first member of bigram to sentence list       
      sentence.append(bigram[1])
      #choose next bigram from the list of matches
      bigram=random.choice(matches)
      
   #combine strings from list
   return " ".join(sentence)
   

sentence_to_test ='it storm tough with anger'

def demo(corpus, testsentence):
    
   mymodel = build_bigram_model(preprocess(corpus))
   testsentencelist = testsentence.split()
   print 'The probability for "', sentence_to_test, '" is: ', str(get_sentence_probability(mymodel,testsentencelist))
   print "A randomly generated sentence: ", generate_sentence(mymodel)

if __name__ == "__main__":
   demo(mydata,sentence_to_test)


