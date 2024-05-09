# Read the word list from a file
with open('en.txt', 'r') as file:
    lines = file.readlines()

# Initialize a dictionary to store sentences and scores
formatted_data = {}

# Process each line in the word list
for line in lines:
    parts = line.strip().split()

    # Check if the line has the expected format (word and score)
    if len(parts) != 2:
        print(f"Ignoring line: {line.strip()}")
        continue

    word, score = parts
    try:
        score = int(score)
    except ValueError:
        print(f"Ignoring line due to invalid score: {line.strip()}")
        continue

    if score not in formatted_data:
        formatted_data[score] = []

    formatted_data[score].append(word)

# Write the formatted data to a new file
with open('formatted_wordlist.txt', 'w') as file:
    for score, words in formatted_data.items():
        for word in words:
            file.write(f"{word}\t{score}\n")

