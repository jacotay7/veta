from scoring_modules.scoring_module import *
from item import Item

class length(ScoringModule):
    """
    A class implementing the length scoring technique. Child of the ScoringModule class.
    The length scoring protocol computes the total number of words in the LEAS item.
    
    ...

    Attributes
    ----------
    type : str
        A string indicating how wether the score applies to single item or an entire respondent. Equals either 'per item' or 'per respondent'
    id : str
        A unique string indentifying the scoring module

    Methods
    -------
    execute(item: Item, wordlist: Wordlist) -> int
        Scores a single LEAS item using a given wordlist.
    """
    type = "per item"
    id = "length"

    def __init__(self) -> None:
        super().__init__()
        return

    def execute(self, item: Item, wordlist: Wordlist) -> int:
        '''
        Scores a single LEAS item using the length Scoring protocol.

                Parameters:
                        item (Item): The LEAS item to be scored
                        wordlist (Wordlist): The wordlist to be searched
                Returns:
                        score (int): The score for the item 
                        
        '''
        sentence = item.self_sentence + ' ' + item.other_sentence
        words = sentence.split(' ')
        words = [word for word in words if word != '']
        return len(words)