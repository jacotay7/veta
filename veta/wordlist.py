import pandas as pd
import numpy as np
import datetime

class Wordlist:
    """
    A class to store and manipulate an eLEAS wordlist

    ...

    Attributes
    ----------
    words : numpy.array
        a list of all words in the wordlist
    scores : numpy.array
        the eLEAS score assigned to each of the words in the wordlist
    filename : str
        the path to an excel file contatining a list of words and their associated LEAS score

    Methods
    -------
    get_wordlist_from_file(filename):
        extracts the wordlist data from file
    """
    def __init__(self, filename: str, creator="veta", name="wordlist", language="en") -> None:
        '''
        Initializes the Wordlist class

                Parameters:
                        filename (str): the path to an excel file contatining a list of words and their associated LEAS score

                Returns:

        '''
        self.filename = filename
        self.creator = creator
        self.name = name
        self.language = language
        wordlist = self.get_wordlist_from_file(filename)
        self.words = wordlist[:,0]
        self.scores = wordlist[:,1]
        if wordlist.shape[1] > 2:
            self.subclasses = wordlist[:,2]
        else:
            self.subclasses = np.zeros_like(self.scores)

        w, s, sb = [], [], []

        for i in range(len(self.words)):
            if isinstance(self.words[i], str):
                w.append(self.words[i].lower())
                s.append(self.scores[i])
                sb.append(self.subclasses[i])
        self.words = np.array(w)
        self.scores = np.array(s)
        self.subclasses = np.array(sb)

        return

    def get_wordlist_from_file(self, filename: str) -> np.array:
        '''
        Initializes the Wordlist class

                Parameters:
                        filename (str): the path to an excel file contatining a list of words and their associated LEAS score

                Returns:
                        wordlist (numpy.array): the contents of the wordlist file given as as numpy array
        '''
        return np.array(pd.read_excel(filename, engine='openpyxl'))

    def __str__(self):

        ret = ""
        for i in range(self.words.size):
            word, score = self.words[i], self.scores[i]
            space = ''.join([' ']*max(0,20 - len(word) ))
            ret += "{}:{}{}\n".format(word, space, score)

        return ret
    
    def addWord(self, word, score, subclass=0.0):
        assert(isinstance(word, str) and isinstance(score, float), isinstance(subclass, float))
        self.words = np.append(self.words, word)
        self.scores = np.append(self.scores, score)
        self.subclasses = np.append(self.subclasses, subclass)
        return

    def addWords(self, words, scores, subclasses=None):

        #Check data types
        if isinstance(words, list):
            words = np.array(words)
        if isinstance(scores, list):
            scores = np.array(scores)
        if isinstance(subclasses, list):
            subclasses = np.array(subclasses)

        assert(isinstance(words, np.ndarray))
        assert(isinstance(scores, np.ndarray))
        if subclasses is not None:
            assert(isinstance(subclasses, np.ndarray))
        else:
            subclasses = np.zeros_like(scores)
        for i in range(len(words)):
            self.addWord(words[i], scores[i], subclasses[i])
        return

    def sortWordlist(self):
        # Get the indices that would sort the string array
        sorted_indices = np.argsort(self.words)

        # Apply the indices to all arrays
        self.words = self.words[sorted_indices]
        self.scores = self.scores[sorted_indices]
        self.subclasses = self.subclasses[sorted_indices]

        return 

    def removeWord(self, word):
        # Find the indices where arr_strings equals str_to_remove
        indices_to_remove = np.where(self.words == word)[0]
        
        if indices_to_remove.size == 0:
            print(f"'{word}' not found in arr_strings.")
            return
        # Remove the indices from arr_strings
        self.words = np.delete(self.words, indices_to_remove)
        self.scores = np.delete(self.scores, indices_to_remove)
        self.subclasses = np.delete(self.subclasses, indices_to_remove)

        return
    
    def removeWords(self, words):

        #Check data types
        if isinstance(words, list):
            words = np.array(words)

        assert(isinstance(words, np.ndarray))

        for i in range(len(words)):
            self.removeWord(words[i])
        return
    
    def save(self, filename, format='xlsx'):
        self.sortWordlist()
        format = format.lower()
        if format == 'xlsx' or format == 'excel':
            # Convert the arrays to a pandas DataFrame
            df = pd.DataFrame({'Words': self.words, 'Scores': self.scores, 'Sublevel': self.subclasses})
            # Save the DataFrame to an Excel file
            df.to_excel(filename, index=False)
        elif format == 'txt':
            with open(filename, 'w') as file:
                dateStr = datetime.datetime.now().strftime("%B %d, %Y")
                file.write(f"{self.name}, created {dateStr}, by {self.creator}, based on Kim Barchard (2013).\n")
                file.write(f"File to be used with POES to allow scoring of the Levels of Emotional Awareness Scale.\n")
                for i in range(len(self.words)):
                    file.write(f"{self.words[i]}\n")
                    file.write(f"{self.scores[i]}\n")