from item import Item
from wordlist import Wordlist
from scoring_modules.scoring_module import *

class _334(ScoringModule):
    """
    A class implementing the 334 scoring technique. Child of the ScoringModule class.
    The 334 scoring protocol gives each item a score between 0 and 4. The score corresponds to
    the highest scored word from the LEAS wordlist that is present in the sentence. Additionally, 
    if there are more than one word with an LEAS score of 3 in the sentence, then the sentence is 
    awarded a score of 4.

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
    id = "334"

    def __init__(self) -> None:
        super().__init__()
        return

    def execute(self, item: Item, wordlist: Wordlist) -> int:
        '''
        Scores a single LEAS item using the 334 Scoring protocol.

                Parameters:
                        item (Item): The LEAS item to be scored
                        wordlist (Wordlist): The wordlist to be searched
                Returns:
                        score (int): The score for the item 
                        

        '''
        sentence = item.self_sentence + ' ' + item.other_sentence
        frequency, matching_words, scores = self.match_words(sentence, wordlist)

        if len(scores) == 0:
            return 0
        elif np.count_nonzero(scores == 3) > 1:
            return 4
        else:
            return max(scores)