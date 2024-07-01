#!/usr/bin/python3
import sys
import string
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

# Initialize the stemmer
stemmer = PorterStemmer()

# Load NLTK stopwords
stop_words = set(stopwords.words('english'))

# Define a translation table to remove punctuation
translator = str.maketrans("", "", string.punctuation)

# Input comes from STDIN (standard input)
# Starting mapper.py
sys.stderr.write("\n-------------------------------------------- STARTING MAPPER.PY -------------------------------------------\n")
# Input comes from STDIN (standard input)
for line in sys.stdin:
    # Remove leading and trailing whitespace
    line = line.strip()
    # Convert to lowercase and remove punctuation
    line = line.lower().translate(translator)
    # Tokenize the line into words
    words = word_tokenize(line)
    # Stem and emit each word with count 1
    for word in words:
        # Remove stopwords and stem
        if word not in stop_words and word.isalpha():
            stemmed_word = stemmer.stem(word)
            print(f"{stemmed_word}\t1")
            
      
