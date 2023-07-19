from veta.scoring_modules.scoring_module import *
from veta.item import Item

class allsum_unique(ScoringModule):
    """
    A class implementing the allsum-unique scoring technique. Child of the ScoringModule class.
    The allsum-unique scoring protocol sums all of the scores for the unique Wordlist words that
    are found in the LEAS item.

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
    id = "allsum-unique"

    def __init__(self, only_high_scores=False) -> None:
        super().__init__()
        self.only_high_scores = only_high_scores
        return

    def execute(self, item: Item, wordlist: Wordlist) -> int:
        '''
        Scores a single LEAS item using the allsum-unique Scoring protocol.

                Parameters:
                        item (Item): The LEAS item to be scored
                        wordlist (Wordlist): The wordlist to be searched
                Returns:
                        score (int): The score for the item 
                        

        '''
        sentence = item.self_sentence + ' ' + item.other_sentence
        frequency, matching_words, scores = self.match_words(sentence, wordlist)

        if self.only_high_scores:
            return sum(scores[scores>2])
        else:
            return sum(scores)