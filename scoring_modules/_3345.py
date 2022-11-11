from item import Item
from scoring_modules.scoring_module import *
from scoring_modules._334 import _334

class _3345(ScoringModule):
    """
    A class implementing the 3345 scoring technique. Child of the ScoringModule class.
    The 3345 scoring protocol requires the item be separated into sections corresponding to 
    the self and the other. It scores each component using the 334 scoring protocol. The assigned
    score is the the maximum of both 334 scores, unless both 334 scores have a value of 4, in
    which case, the assigned score is 5.

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
    id = "3345"

    def __init__(self) -> None:
        super().__init__()
        return

    def execute(self, item: Item, wordlist: Wordlist) -> int:
        '''
        Scores a single LEAS item using the 3345 Scoring protocol.

                Parameters:
                        item (Item): The LEAS item to be scored
                        wordlist (Wordlist): The wordlist to be searched
                Returns:
                        score (int): The score for the item 
                        

        '''
        self_frequency, self_matching_words, self_scores = self.match_words(item.self_sentence, wordlist)

        if len(self_scores) == 0:
            self_334 =  0
        elif np.count_nonzero(self_scores == 3) > 1:
            self_334 =  4
        else:
            self_334 =  max(self_scores)

        other_frequency, other_matching_words, other_scores = self.match_words(item.other_sentence, wordlist)

        if len(other_scores) == 0:
            other_334 =  0
        elif np.count_nonzero(other_scores == 3) > 1:
            other_334 =  4
        else:
            other_334 =  max(other_scores)
            
        if other_334 == 4 and other_334 == 4:
            return 5
    
        return max(other_334, self_334)
