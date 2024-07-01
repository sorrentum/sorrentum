#!/usr/bin/python3
from collections import defaultdict
import sys

# Initialize a dictionary to store word counts
word_counts = defaultdict(int)

# Initialize variables
current_word = None
current_count = 0
word = None

# Input comes from STDIN (standard input)
# Starting reducer.py
sys.stderr.write("\n-------------------------------------------- STARTING REDUCER.PY -------------------------------------------\n")
for line in sys.stdin:
    # Remove leading and trailing whitespace
    line = line.strip()

    # Parse the input we got from mapper.py
    word, count = line.split('\t', 1)

    # Convert count to an integer
    try:
        count = int(count)
    except ValueError:
        # Count was not a number, so ignore this line
        continue

    # This if-else block transitions to a new word and outputs the previous word's count
    if current_word == word:
        current_count += count
    else:
        if current_word:
            # Write result to STDOUT
            word_counts[current_word] = current_count
        current_count = count
        current_word = word
# Output the last word if needed
if current_word == word:
    word_counts[current_word] = current_count

# Sort the dictionary by value in descending order
sorted_word_counts = sorted(word_counts.items(), key=lambda item: item[1], reverse=True)

sys.stderr.write("\n------------------------------------------- TOP 10 MOST COMMON WORDS --------------------------------------------\n")

# Print the top 100 results
for word, count in sorted_word_counts[:10]:
    print(f"{word}\t{count}")
    sys.stderr.write(f"{count}\t{word}\n")