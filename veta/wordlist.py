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
    
    def save(self, filename, format='xlsx'):
        format = format.lower()
        if format == 'xlsx' or format == 'excel':
            # Convert the arrays to a pandas DataFrame
            df = pd.DataFrame({'Words': self.words, 'Scores': self.scores})
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