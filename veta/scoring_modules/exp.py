from veta.scoring_modules.scoring_module import *
from veta.scoring_modules._3345 import _3345
from veta.item import Item

class exp(ScoringModule):
    """
    A class implementing the exponential scoring technique. Child of the ScoringModule class.
    The exponential scoring protocol returns the exp(b*3345(x)) where exp is the exponential 
    function, b is a free parameter, and 3345(x) is the 3345 scoring module applied to an item x.
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
    id = "exp"

    def __init__(self, b, language='en') -> None:
        '''
        Initialized the exp scoring module

                Parameters:
                        b (float): the exponential scaling parameter to use for scoring.
                Returns:

                        
        '''
        super().__init__(language=language)
        self.b = b
        return

    def execute(self, item: Item, wordlist: Wordlist) -> int:
        '''
        Scores a single LEAS item using the allsum Scoring protocol.

                Parameters:
                        item (Item): The LEAS item to be scored
                        wordlist (Wordlist): The wordlist to be searched
                Returns:
                        score (int): The score for the item 
                        
        '''
        return np.exp(self.b*_3345().execute(item, wordlist))-1
