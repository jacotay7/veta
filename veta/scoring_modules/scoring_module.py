import numpy as np
from veta.wordlist import Wordlist

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

        if sentence_tmp[index-1] == ' ' and sentence_tmp[index+len(word)] == ' ':
            return True

        return False

    def match_words(self, sentence: str, wordlist: Wordlist):
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
        wordlist_words = wordlist.words
        wordlist_scores = wordlist.scores

        scores = []
        matching_words = []
        frequency = []

        for i in range(len(wordlist_words)):
            word_original = wordlist_words[i]
            word_lower = word_original.lower()
            if word_lower in sentence:
                if self.is_full_word(sentence, word_lower):
                    word_score = wordlist_scores[np.where(wordlist_words == word_original)][0]
                    frequency.append(sentence.count(word_lower))
                    matching_words.append(word_original)
                    scores.append(word_score)

        return np.array(frequency), np.array(matching_words), np.array(scores)

    def __init__(self) -> None:

        return

    def execute():
        
        return