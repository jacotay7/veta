from scoring_modules.scoring_module import *
from scoring_modules._3345 import _3345
from item import Item

class powerlaw(ScoringModule):
    """
    A class implementing the powerlaw scoring technique. Child of the ScoringModule class.
    The powerlaw scoring protocol returns the 3345(x)^gamma where, gamma is a free parameter, 
    and 3345(x) is the 3345 scoring module applied to an item x.
    
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
    id = "powerlaw"

    def __init__(self, gamma) -> None:
        '''
        Initialized the exp scoring module

                Parameters:
                        gamma (float): the powerlaw scaling parameter to use for scoring.
                Returns:

                        
        '''
        super().__init__()
        self.gamma = gamma
        return

    def execute(self, item: Item, wordlist: Wordlist) -> int:
        '''
        Scores a single LEAS item using the powerlaw Scoring protocol.

                Parameters:
                        item (Item): The LEAS item to be scored
                        wordlist (Wordlist): The wordlist to be searched
                Returns:
                        score (int): The score for the item 
                        
        '''
        return _3345().execute(item, wordlist)**self.gamma
