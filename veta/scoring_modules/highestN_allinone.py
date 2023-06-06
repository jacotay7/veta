from veta.scoring_modules.scoring_module import *
from veta.scoring_modules.highestN import highestN
from veta.item import Item

class highestN_allinone(ScoringModule):
    """
    A class implementing the highestN-allinone scoring technique. Child of the ScoringModule class.
    The highestN-allinone scoring protocol is a per respondent scoring module that combines and scores
    several LEAS items according to the HighestN protocol.
    ...

    Attributes
    ----------
    type : str
        A string indicating how wether the score applies to single item or an entire respondent. Equals either 'per item' or 'per respondent'
    id : str
        A unique string indentifying the scoring module

    Methods
    -------
    execute(self, items: list, wordlist: Wordlist) -> int:
        Scores a list of LEAS items using a given wordlist.
    """
    type = "per respondent"
    

    def __init__(self, N) -> None:
        super().__init__()
        self.N = N
        self.id = "highest{}-allinone".format(N)
        return

    def execute(self, items: list, wordlist: Wordlist) -> int:
        '''
        Scores a list of LEAS items using the highestN-allinone scoring technique.

                Parameters:
                        items (list): The LEAS item to be scored
                        wordlist (Wordlist): The wordlist to be searched
                Returns:
                        score (int): The score for the item 
                        
        '''
        total_sentence = ""
        for item in items:
            total_sentence += " " + item.self_sentence + ' ' + item.other_sentence + ' '
        
        new_item = Item(total_sentence, "")
        return highestN(self.N).execute(new_item, wordlist)