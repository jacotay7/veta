from veta.scoring_modules.scoring_module import *
from veta.scoring_modules._334 import _334
from veta.item import Item

class highestN(ScoringModule):
    """
    A class implementing the highestN scoring technique. Child of the ScoringModule class.
    The highestN scoring protocol sums the highest N scores of the Wordlist words that appear
    in the LEAS item. That is to say, if an item has 10 matching words and N is set to 4, the
    assigned score will correspond to the sum of the largest 4 scores of the 10 matching words.
    
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
    # id = "highestN"

    def __init__(self, N, language='en') -> None:
        '''
        Initialized the highestN-unique scoring module

                Parameters:
                        N (int): the number of Wordlist words to include in the score
                Returns:

                        
        '''
        super().__init__(language=language)
        self.N = N
        self.id = "highest{}".format(N)
        return

    def execute(self, item: Item, wordlist: Wordlist) -> int:
        '''
        Scores a single LEAS item using the highestN Scoring protocol.

                Parameters:
                        item (Item): The LEAS item to be scored
                        wordlist (Wordlist): The wordlist to be searched
                Returns:
                        score (int): The score for the item 
                        
        '''
        sentence = item.self_sentence + ' ' + item.other_sentence
        frequency, matching_words, scores = self.match_words(sentence, wordlist)

        p = (-1*scores).argsort()
        scores = scores[p]
        frequency = frequency[p]

        total = 0
        i = 0
        left = self.N
        while i < frequency.size and left > 0:
            if frequency[i] < left:
                total += frequency[i]*scores[i]
                left -= frequency[i]
            else:
                total += left*scores[i]
                left = 0
            
            i += 1
            
        return total