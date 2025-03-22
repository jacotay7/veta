import numpy as np
from veta.wordlist import Wordlist
import re
from collections import defaultdict

class ScoringModule:
    """
    The parent class to all of the LEAS scoring modules

    ...

    Attributes
    ----------
    type : str
        A string indicating how wether the score applies to single item or an entire respondent. Equals either 'per item' or 'per respondent'
    id : str
        A unique string indentifying the scoring module

    Methods
    -------
    is_full_word(self, sentence: str, word: str)
        A helper function that checks if the string 'word' is contained within the string 'sentence' with a space on either side.
    match_words(self, sentence: str, wordlist: Wordlist)
        Finds all of the wordlist words and correspndoing scores that are contained in the sentence.
    execute()
        Empty. To be overwritten by child classes.
    """
    type = None
    id = None

    def is_full_word(self, sentence: str, word: str) -> bool:
        '''
        A helper function that checks if the string 'word' is fully contained within the string 'sentence' as an independent word.
        The purpose is to account for the possibility that the word is in the sentence only as a substring of a full word. 
        E.g. if the word was 'sad' and the sentence contained the word 'sadly', this function would return False.

                Parameters:
                        sentence (str): The string containing the sentence to be searched.
                        word (str): The word to be found in the sentence. 
                Returns:
                        (bool): True if the word is in the sentence with spaces on either side. False otherwise.

        '''

        sentence_tmp = ' ' + sentence + ' '
        
        index = sentence_tmp.index(word)

        previous_char = sentence_tmp[index-1]
        next_char = sentence_tmp[index+len(word)]

        
        condition = previous_char in self.acceptable_prev_chars and  next_char in self.acceptable_next_chars
        return condition

    # def match_words(self, sentence: str, wordlist: Wordlist, sublevels = False):
    #     '''
    #     Finds which words from the wordlist are present in the sentence along with their frequency and corresponding scores.
    #     This function is used by most scoring modules to score LEAS items.

    #             Parameters:
    #                     sentence (str): The string containing the sentence to be characterized.
    #                     wordlist (Wordlist): The wordlist to be searched
    #             Returns:
    #                     frequency (np.array): An array containing the frequency that each word in matching_words appears in the sentence.
    #                     matching_words (np.array): An array containing the words in the wordlist that are contained in the sentence.
    #                     scores (np.array): The corresponding scores of each matching word from the wordlist.
                        

    #     '''
    #     if not sublevels:
    #         return self.match_words_regex(sentence, wordlist)

    #     wordlist_words = wordlist.words
    #     wordlist_scores = wordlist.scores
    #     if sublevels:
    #         wordlist_subscores = wordlist.subclasses
    #         subscores = []

    #     scores = []
    #     matching_words = []
    #     frequency = []

    #     #Loop through the wordlist
    #     for i in range(len(wordlist_words)):
    #         #get the original and lowercase version of the word
    #         word_original = wordlist_words[i]
    #         word_lower = word_original.lower()
    #         #Check if its in the sentence and its not a partial word component
    #         #Here we are checking for things like "love" is not found in "glove"
    #         if word_lower in sentence and self.is_full_word(sentence, word_lower):
    #             index = np.where(wordlist_words == word_original)
    #             word_score = wordlist_scores[index][0]
    #             frequency.append(sentence.count(word_lower))
    #             matching_words.append(word_original)
    #             scores.append(word_score)
    #             if sublevels:
    #                 subscores.append(wordlist_subscores[index][0])
        
    #     matching_words = np.array(matching_words)
    #     word_lengths = np.array([len(word) for word in matching_words])
    #     sort_indices = np.argsort(word_lengths)

    #     matching_words = matching_words[sort_indices]
    #     frequency = np.array(frequency)[sort_indices]
    #     scores = np.array(scores)[sort_indices]
    #     if sublevels:
    #         subscores = np.array(subscores)[sort_indices]
    #     """
    #     Here we need to check to make sure that the words we found from the wordlist
    #     are not nested into expressions that are in the wordlist, i.e. love language 
    #     should not score for love 
    #     """
    #     inds_to_remove = []
    #     sentence_tmp = sentence[:]
    #     #Loop through the sorted matching words
    #     for i, word in enumerate(matching_words):
    #         #Count how many indices we find
    #         frequency[i] = sentence_tmp.count(word)
    #         #If we find none, set to remove
    #         if frequency[i] == 0:
    #             inds_to_remove.append(i)
    #         #remove all instances from the sentence for the future iterations
    #         sentence_tmp = self.remove_full_words(sentence_tmp, word)

    #     matching_words = np.delete(matching_words,inds_to_remove)
    #     frequency = np.delete(frequency,inds_to_remove)
    #     scores = np.delete(scores,inds_to_remove)
    #     if sublevels:
    #         subscores = np.delete(subscores,inds_to_remove)

    #     if sublevels:
    #         return frequency, matching_words, scores, subscores
    #     return frequency, matching_words, scores

    def match_words(self, sentence: str, wordlist: Wordlist, sublevels = False):
        '''
        Finds which words from the wordlist are present in the sentence along with their frequency and corresponding scores.
        This function is used by most scoring modules to score LEAS items.

                Parameters:
                        sentence (str): The string containing the sentence to be characterized.
                        wordlist (Wordlist): The wordlist to be searched
                Returns:
                        frequency (np.array): An array containing the frequency that each word in matching_words appears in the sentence.
                        matching_words (np.array): An array containing the words in the wordlist that are contained in the sentence.
                        scores (np.array): The corresponding scores of each matching word from the wordlist.
                        

        '''
        if self.wordlist is None or self.wordlist.unique_id != wordlist.unique_id:
            self.add_wordlist(wordlist)

        # Find all non-overlapping matches in the sentence
        matches = list(self.regex.finditer(sentence))

        # Keep track of matched ranges to prevent overlapping sub-word matches
        matched_ranges = []
        matched_words = []
        word_counts = defaultdict(int)
        for match in matches:
            start, end = match.span()
            # Check for overlap with existing matched ranges
            overlap = False
            for s, e in matched_ranges:
                if start < e and end > s:
                    overlap = True
                    break
            #If there is not overlap from the words so far
            if not overlap:
                matched_text = match.group()
                matched_words.append(matched_text)
                #Either the word is in the wordlist
                if matched_text in self.word_score:
                    word_counts[matched_text] += 1
                #Or it has an escape character at the front
                elif matched_text[:-1] in self.word_score:
                    word_counts[matched_text[:-1]] += 1
                #Or it has one at the beginning
                elif matched_text[1:] in self.word_score:
                    word_counts[matched_text[1:]] += 1
                else:
                    raise Exception(f"An issue finding the matching word for {matched_text}")
                matched_ranges.append((start, end))

        """
        Allow people to miss spaces between two emotion words
        """
        if self.language == 'he':
            # Loop through what we found
            for i, word in enumerate(matched_words):
                if i == 0:
                    continue
                #If the starting letter comes right after a previous match (i.e, no space)
                if matched_ranges[i][0] == matched_ranges[i-1][1]:
                    #if the the next spot in the sentence exists and is not a space (i.e, its another letter)
                    if len(sentence) > matched_ranges[i][1] and sentence[matched_ranges[i][1]] != ' ':
                        word_counts[word] -= 1

        # Prepare the output list
        frequency, matching_words, scores, subscores = [], [], [], []
        for word, f in word_counts.items():
            #Double check to make sure its actually in the dictionary 
            if word in self.word_score:
                matching_words.append(word)
                frequency.append(f)
                scores.append(self.word_score.get(word, 0))
                subscores.append(self.word_subscore.get(word, 0))
        frequency = np.array(frequency)
        matching_words = np.array(matching_words)
        scores = np.array(scores)
        subscores = np.array(subscores)
        if sublevels:
            return frequency, matching_words, scores, subscores
        return frequency, matching_words, scores

    def __init__(self, language='en') -> None:

        self.language = language
        self.regex = None
        self.wordlist = None
        self.acceptable_prev_chars = ''
        self.acceptable_next_chars = ''
        #Hebrew specific rulings
        if self.language == 'he':
            self.acceptable_prev_chars += "לושבהו"
            # self.acceptable_next_chars += "ושבוה"
            # acceptable_prev_chars += "רןףקםוחצמלץנךסגאכישּ2דעבזפטתה"
            # acceptable_next_chars += "רןףקםוחצמלץנךסגאכישּ2דעבזפטתה"
        elif self.language == 'ar':
            self.acceptable_prev_chars += '،ءأؤإئابةتثجحخدذرزسشصضطظعغفقكلمنهوىي'
        return

    def add_wordlist(self, wordlist: Wordlist):
        self.wordlist = wordlist
        # Create a mapping from word/phrase to score
        self.word_score = dict(zip(wordlist.words, wordlist.scores))
        self.word_subscore = dict(zip(wordlist.words, wordlist.subclasses))

        # Sort the words by length in descending order to match longer phrases first
        words_sorted = sorted(wordlist.words, key=len, reverse=True)

        # Prepare the special characters pattern
        acceptable_prev_chars_pattern = '[' + self.acceptable_prev_chars + ']?'
        acceptable_next_chars_pattern = '[' + self.acceptable_next_chars + ']?'

        # Build individual regex patterns for each word/phrase
        patterns = []
        for word in words_sorted:
            # Allow special characters before the first word of the phrase
            if len(self.acceptable_prev_chars) > 0:
                word_pattern = '\\b' + acceptable_prev_chars_pattern + word + '\\b'
                patterns.append(word_pattern)
            if len(self.acceptable_next_chars) > 0:
                word_pattern = '\\b' + word + acceptable_next_chars_pattern + '\\b'
                patterns.append(word_pattern)
            # if len(self.acceptable_prev_chars) == 0 and len(self.acceptable_next_chars) == 0:
            word_pattern = '\\b' + word + '\\b'
            patterns.append(word_pattern)
        """
        Allow missing spaces between words, is much slower
        """
        if self.language == 'he':
            for word in words_sorted:
                if len(word) > 2:
                    patterns.append(word)
        self.patterns = patterns
        # Combine individual patterns into one regex pattern
        combined_pattern = '|'.join(patterns)

        # Compile the regex pattern
        self.regex = re.compile(combined_pattern)

    def execute():
        
        return
    
    def remove_full_words(self, sentence, word):
        """
        Removes all instances of 'substring' in 'string' if they satisfy the 'condition'.
        The 'condition' is a function that takes the substring instance and returns True if it should be removed.

        Args:
        string (str): The original string.
        substring (str): The substring to search for and potentially remove.
        condition (function): A function that takes a substring and returns a boolean.

        Returns:
        str: The modified string with specified substrings removed if they meet the condition.
        """
        sentence_tmp = ' ' + sentence + ' '
        start = 0  # Start index for search
        while sentence_tmp.find(word, start) != -1:
            # Find the next index of the substring
            start = sentence_tmp.find(word, start)
            # Check if the current occurrence satisfies the condition
            condition = sentence_tmp[start-1] == ' ' and sentence_tmp[start+len(word)] == ' '
            if condition:
                # Remove the substring from the string
                sentence_tmp = sentence_tmp[:start] + sentence_tmp[start+len(word):]
            else:
                # Move start index forward to continue searching
                start += len(word)

        return sentence_tmp