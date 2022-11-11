from scoring_modules.scoring_module import *
from item import Item

class allsum(ScoringModule):
    """
    A class implementing the allsum scoring technique. Child of the ScoringModule class.
    The allsum scoring protocol sums all of the scores for the Wordlist words that
    are found in the LEAS item. If a word is repeated, the score is multiplied by the number 
    of times the word occurs in the LEAS item.

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
    id = "allsum"

    def __init__(self) -> None:
        super().__init__()
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
        sentence = item.self_sentence + ' ' + item.other_sentence
        frequency, matching_words, scores = self.match_words(sentence, wordlist)

        return sum(scores*frequency)