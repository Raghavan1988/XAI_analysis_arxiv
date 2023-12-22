import os
import fitz  # PyMuPDF for reading PDF files
import re

# Directory containing PDF files, passed as a command line argument
directory = sys.argv[1]

# Function to check if a word is in the file contents
def is_word_in_file(word, file_contents):
    word_pattern = rf'\b{re.escape(word)}\b'  # Regular expression pattern for the word
    return bool(re.search(word_pattern, file_contents, re.IGNORECASE))  # Case-insensitive search

# Function to check if a sequence of words is in the file contents in the given order
def are_words_in_order(words, file_contents):
    words_pattern = r'\b' + r'\b.*\b'.join(map(re.escape, words.split())) + r'\b'  # Pattern for the sequence of words
    return bool(re.search(words_pattern, file_contents, re.IGNORECASE))  # Case-insensitive search

# List of keywords to search for in the PDF files
keywords = [
    # A list of keywords and phrases related to AI and machine learning
    # ...
    # Additional relevant terms
    # ...
]

# Dictionaries to store results
keyword_counts = {}  # Counts of each keyword
files_with_keywords = {}  # Files containing each keyword

# Traverse through all files in the directory
match_count = 0  # Total number of matches found
total = 0  # Total number of files processed
error = 0  # Number of files with errors

for filename in os.listdir(directory):
    if filename.endswith(".pdf"):
        file_path = os.path.join(directory, filename)
        text = ""
        total += 1
        try:
            doc = fitz.open(file_path)  # Open the PDF file
            text = chr(12).join([page.get_text() for page in doc])  # Extract text from each page
            print(f"Read {filename}, Count: {total}")
        except:
            print(f"Error reading {filename}")
            error += 1
            continue

        # Check for each keyword in the text
        for keyword in keywords:
            single_word = len(keyword.split()) == 1  # Check if the keyword is a single word
            
            # Check if keyword is in the text and whether it matches the criteria based on its length
            if keyword in text and ((single_word and is_word_in_file(keyword, text)) or (not single_word and are_words_in_order(keyword, text))):
                if keyword not in keyword_counts:
                    keyword_counts[keyword] = 0
                    files_with_keywords[keyword] = []
                keyword_counts[keyword] += 1
                files_with_keywords[keyword].append(filename)
                match_count += 1
                break

# Write results to files
sorted_file_counts = sorted(keyword_counts.items(), key=operator.itemgetter(1), reverse=True)
output_file = "keyword_search_results.txt"
output_file1 = "keyword_search_results_files.txt"
with open(output_file, "w") as f, open(output_file1, "w") as w:
    for keyword, count in sorted_file_counts:
        f.write(f"{keyword}: {count}\n")
        w.write(f"{keyword}: {files_with_keywords[keyword]}\n\n")

print(f"Total files: {total}")
print(f"Match count: {match_count}")
print(f"Files with errors: {error}")
print(f"Results written to {output_file}")
