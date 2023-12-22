import os
import fitz  # PyMuPDF
import re
import sys
import operator

# Directory containing PDF files
directory = sys.argv[1]

def is_word_in_file(word, file_contents, case_sensitive=False):
    word_pattern = rf'\b{re.escape(word)}\b'
    flags = 0 if case_sensitive else re.IGNORECASE
    return bool(re.search(word_pattern, file_contents, flags))

def are_words_in_order(words, file_contents, case_sensitive=False):
    words_pattern = r'\b' + r'\b.*\b'.join(map(re.escape, words.split())) + r'\b'
    flags = 0 if case_sensitive else re.IGNORECASE
    return bool(re.search(words_pattern, file_contents, flags))

# Keywords to search for
keywords = [
    # List of case-insensitive keywords
    "Black Box", "Interpretability", "Feature Importance",
    # ... other keywords ...
    "AI Explainability Techniques"
]

keywords_case_sensitive = [
    # List of case-sensitive keywords
    "LIME", "SHAP"
]

# Dictionaries to store results
keyword_counts = {}
files_with_keywords = {}

# Traverse through all files in the directory
match_count = 0
total = 0
error = 0
for filename in os.listdir(directory):
    if filename.endswith(".pdf"):
        file_path = os.path.join(directory, filename)
        text = ""
        total += 1
        try:
            # Open the file
            doc = fitz.open(file_path)
            # Extract text from each page
            text = chr(12).join([page.get_text() for page in doc])
            print(f"Read {filename}, Count: {total}")
        except:
            print(f"Error reading {filename}")
            error += 1
            continue

        # Check for each keyword in the text
        for keyword_list, case_sensitive in [(keywords, False), (keywords_case_sensitive, True)]:
            for keyword in keyword_list:
                single_word = len(keyword.split()) == 1
                if single_word and is_word_in_file(keyword, text, case_sensitive):
                    keyword_lower = keyword.lower() if not case_sensitive else keyword
                    keyword_counts.setdefault(keyword_lower, 0)
                    files_with_keywords.setdefault(keyword_lower, []).append(filename)
                    keyword_counts[keyword_lower] += 1
                    match_count += 1
                    break
                elif not single_word and are_words_in_order(keyword, text, case_sensitive):
                    keyword_lower = keyword.lower() if not case_sensitive else keyword
                    keyword_counts.setdefault(keyword_lower, 0)
                    files_with_keywords.setdefault(keyword_lower, []).append(filename)
                    keyword_counts[keyword_lower] += 1
                    match_count += 1
                    break

# Write results to a file
sorted_file_counts = sorted(keyword_counts.items(), key=operator.itemgetter(1), reverse=True)
output_file = "keyword_search_results.txt"
output_file1 = "keyword_search_results_files.txt"
with open(output_file1, "w") as w, open(output_file, "w") as f:
    for keyword, count in sorted_file_counts:
        f.write(f"{keyword}: {count}\n")
        w.write(f"{keyword}: {files_with_keywords[keyword]}\n\n")

print(f"Total files: {total}")
print(f"Match count: {match_count}")
print(f"Files with errors: {error}")
print(f"Results written to {output_file}")
