from veta.scoring_modules.scoring_module import *
from veta.item import Item

class highestN_unique(ScoringModule):
    """
    A class implementing the highestN-unique scoring technique. Child of the ScoringModule class.
    The highestN-unique scoring protocol sums the highest N scores of the unique Wordlist words 
    in the LEAS item. That is to say, if an item has 10 unique matching words and N is set to 4, the
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
    # id = "highestN-unique"

    def __init__(self, N: int) -> None:
        '''
        Initialized the highestN-unique scoring module

                Parameters:
                        N (int): the number of Wordlist words to include in the score
                Returns:

                        
        '''
        super().__init__()
        self.N = N
        self.id = "highest{}-unique".format(N)
        return

    def execute(self, item: Item, wordlist: Wordlist) -> int:
        '''
        Scores a single LEAS item using the highestN-unique Scoring protocol.

                Parameters:
                        item (Item): The LEAS item to be scored
                        wordlist (Wordlist): The wordlist to be searched
                Returns:
                        score (int): The score for the item 
                        
        '''
        sentence = item.self_sentence + ' ' + item.other_sentence
        frequency, matching_words, scores = self.match_words(sentence, wordlist)

        p = scores.argsort()
        scores = scores[p]
        print('give me highest N unique', self.N)

        if self.N > len(scores):
            return sum(scores)
        
        print('give me highest N unique 222222', sum(scores[-1*self.N:]))
        return sum(scores[-1*self.N:])