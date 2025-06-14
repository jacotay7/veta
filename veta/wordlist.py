import pandas as pd
import numpy as np
import datetime
import re 
import random
import string
from veta.logger import get_logger

# Initialize logger for this module
logger = get_logger('wordlist')

def is_number(s):
    """
    Check if the string s represents a number (integer or float).
    """
    s = s.strip()
    if not s:
        return False
    # Regular expression pattern for matching integers and floats, including negative numbers
    number_pattern = re.compile(r'^-?\d+(?:\.\d+)?$')
    return bool(number_pattern.match(s))

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
    loadFromFile(filename):
        extracts the wordlist data from file
    """
    def __init__(self, filename: str, creator="veta", name="wordlist", language="en") -> None:
        '''
        Initializes the Wordlist class

                Parameters:
                        filename (str): the path to an excel file contatining a list of words and their associated LEAS score

                Returns:

        '''
        logger.info(f"Initializing Wordlist from file: {filename}")
        self.unique_id = ''.join(random.sample(string.ascii_uppercase, 26))
        self.filename = filename
        self.creator = creator
        self.name = name
        self.language = language
        
        logger.debug(f"Loading wordlist data from file")
        self.loadFromFile(filename)
        
        logger.debug("Cleaning wordlist data")
        self.cleanWordlist()
        
        logger.info(f"Wordlist initialized with {len(self.words)} words")
        # w, s, sb = [], [], []

        # #
        # for i in range(len(self.words)):
        #     if isinstance(self.words[i], str):
        #         w.append(self.words[i].lower())
        #         s.append(self.scores[i])
        #         sb.append(self.subclasses[i])
        # self.words = np.array(w)
        # self.scores = np.array(s)
        # self.subclasses = np.array(sb)

        return

    def loadFromFile(self, filename: str) -> np.array:
        '''
        Initializes the Wordlist class

                Parameters:
                        filename (str): the path to an excel file contatining a list of words and their associated LEAS score

                Returns:
                        wordlist (numpy.array): the contents of the wordlist file given as as numpy array
        '''
        logger.debug(f"Loading wordlist from file: {filename}")
        
        try:
            if filename.endswith(".txt"):
                logger.debug("Loading from text file")
                self.words, self.scores = self.loadFromTxt(filename)
                self.subclasses = np.zeros_like(self.scores)
            elif filename.endswith(".xlsx") or filename.endswith(".xls"):
                logger.debug("Loading from Excel file")
                data = np.array(pd.read_excel(filename, engine='openpyxl'))
                self.words = data[:,0]
                self.scores = data[:,1]
                if data.shape[1] > 2:
                    self.subclasses = data[:,2]
                    logger.debug("Loaded subclasses from third column")
                else:
                    self.subclasses = np.zeros_like(self.scores)
                    logger.debug("No subclasses found, using zeros")
                return 
            else:
                logger.error(f"Unsupported file type: {filename}")
                raise Exception("File Type not Supported. Please use .txt or .xlsx")
                
        except Exception as e:
            logger.error(f"Error loading wordlist from {filename}: {str(e)}")
            raise

    def __str__(self):

        ret = ""
        for i in range(self.words.size):
            word, score = self.words[i], self.scores[i]
            space = ''.join([' ']*max(0,20 - len(word) ))
            ret += "{}:{}{}\n".format(word, space, score)

        return ret
    
    def addWord(self, word, score, subclass=0.0):
        assert isinstance(word, str) and isinstance(score, float) and isinstance(subclass, float)
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
        self.cleanWordlist()
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

    def loadFromTxt(self, filename):

        words = []
        numbers = []
        prev_line = None
        last_word = None
        with open(filename, 'r') as file:
            lines = file.readlines()

        # Assume the first two lines are headers
        data_lines = lines[2:]

        for line in data_lines:
            line = line.strip()
            if not line:
                continue  # Skip empty lines

            if prev_line is None:
                # Expecting a word
                if is_number(line):
                    print(f"Warning: Expected a word, but got a number '{line}'. Last word found {last_word}")
                    continue  # Skip this line
                else:
                    prev_line = line
            else:
                # Expecting a number
                if is_number(line):
                    number = float(line)
                    words.append(prev_line)
                    last_word  = prev_line
                    numbers.append(number)
                    prev_line = None
                else:
                    print(f"Warning: Expected a number after word '{prev_line}', but got '{line}'.")
                    prev_line = line  # Treat this line as the new word

        # Convert lists to NumPy arrays
        return np.array(words), np.array(numbers)


    def cleanWordlist(self):
        # Make all words lower case
        self.words = np.array([word.lower() for word in self.words ])
        
        # Remove entries where both score == 0 and subclass == 0
        mask = ~((self.scores == 0) & (self.subclasses == 0))
        self.words = self.words[mask]
        self.scores = self.scores[mask]
        self.subclasses = self.subclasses[mask]
        
        # Remove duplicate words, keeping only the first occurrence
        _, unique_indices = np.unique(self.words, return_index=True)
        unique_indices.sort()  # Sort indices to keep the original order
        self.words = self.words[unique_indices]
        self.scores = self.scores[unique_indices]
        self.subclasses = self.subclasses[unique_indices]

        self.sortWordlist()

        return