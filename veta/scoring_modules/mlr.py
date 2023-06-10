from veta.item import Item
from veta.wordlist import Wordlist
from veta.scoring_modules.scoring_module import *

class mlr(ScoringModule):
    """
    A class implementing the mlr scoring technique. Child of the ScoringModule class.
    The mlr scoring protocol returns a binary response (either 1 or 0) indicating whether
    the LEAS item contains a mix of low (either 1 or 2) and high (3) scoring words from 
    the wordlist. A value of 1 is returned if the item does contain a mix, and a value of
    0 is returned if there is not a mix (matching words are either all low, all high,
    or no words match at all).

    ...

    Attributes
    ----------
    type : str
        A string indicating whether the score applies to single item or an entire respondent. Equals either 'per item' or 'per respondent'
    id : str
        A unique string indentifying the scoring module

    Methods
    -------
    execute(item: Item, wordlist: Wordlist) -> int
        Scores a single LEAS item using a given wordlist.
    """
    type = "per item"
    id = "mlr"

    def __init__(self) -> None:
        super().__init__()
        return

    def execute(self, item: Item, wordlist: Wordlist) -> int:
        '''
        Scores a single LEAS item using the mlr Scoring protocol.

                Parameters:
                        item (Item): The LEAS item to be scored
                        wordlist (Wordlist): The wordlist to be searched
                Returns:
                        score (int): The score for the item    
        '''
        sentence = item.self_sentence + ' ' + item.other_sentence
        frequency, matching_words, scores = self.match_words(sentence, wordlist)
        contains_low = 1 in scores or 2 in scores
        contains_high = 3 in scores

        if contains_high and contains_low:
            return 1
        return 0