from veta.item import Item
from veta.scoring_modules.scoring_module import *
from veta.scoring_modules._334 import _334

class _3345plus(ScoringModule):
    """
    A class implementing the 3345plus scoring technique. Child of the ScoringModule class.
    The 3345plus scoring protocol is the same as the 3345 protocol with the additional constraint
    that a score of 5 is only given if the `level 3' words in each of the 'self' and 'other' components
    are unique. i.e. unique sentiments are expressed.

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
    id = "3345plus"

    def __init__(self) -> None:
        super().__init__()
        return

    def execute(self, item: Item, wordlist: Wordlist) -> int:
        '''
        Scores a single LEAS item using the 3345plus Scoring protocol.

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


        self_matching_high_words = [self_matching_words[i] for i in range(self_matching_words.size) if self_scores[i] > 2]
        other_matching_high_words = [other_matching_words[i] for i in range(other_matching_words.size) if other_scores[i] > 2]


        if self_334 == 4 and other_334 == 4 and set(other_matching_high_words) != set(self_matching_high_words):
            return 5
    
        return max(other_334, self_334)
