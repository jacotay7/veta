from veta.scoring_modules.scoring_module import *
from veta.item import Item

class vocab(ScoringModule):
    """
    A class implementing the vocab scoring technique. Child of the ScoringModule class.
    The vocab scoring protocol counts the total number of unique words in the LEAS item.
    
    ...

    Attributes
    ----------
    type : str
        A string indicating how wether the score applies to single item or an entire respondent. Equals either 'per item' or 'per respondent'
    id : str
        A unique string indentifying the scoring module

    Methods
    -------
    execute(items: list, wordlist: Wordlist) -> int:
        Scores all of a respondent's LEAS item using a given wordlist.
    """
    type = "per respondent"
    id = "vocab"

    def __init__(self, language='en') -> None:
        super().__init__(language=language)
        return

    def execute(self, items: list, wordlist: Wordlist) -> int:
        '''
        Scores a list of LEAS items using the vocab scoring technique.

                Parameters:
                        items (list): The LEAS item to be scored
                        wordlist (Wordlist): The wordlist to be searched
                Returns:
                        score (int): The score for the item 
                        
        '''
        total_sentence = ""
        for item in items:
            total_sentence += " " + item.self_sentence + ' ' + item.other_sentence + ' '
        
        words = total_sentence.split(' ')
        words = [word for word in words if word != '']
        return len(set(words))