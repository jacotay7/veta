from veta.wordlist import Wordlist
from veta.scoring_modules.scoring_module import ScoringModule

class Item:
    """
    A class representing a single LEAS survey item. An item is a single response to an LEAS questions.
    The class is responsible for holding the scores given to the item, cleaning it so that it is machine readable,
    and holding all additional information pertaining to the item.

    ...

    Attributes
    ----------
    self_sentence : str
        a string containing the response to the LEAS question. If the user wants to use LEAS scoring methods which make a 
        distinction between text refering to the 'self' or the 'other', this attribute holds the components of the response referencing the 'self'.
    other_sentence : str
        If the user wants to use LEAS scoring methods which make a distinction between text refering to the 'self' or the 'other', 
        this attribute holds the components of the response referencing the 'other'.
    scores: dict
        A dictionary containing the scores or additional information assigned to the item. 
        The keys are the scoring module ids, the values are the corresponding scores.
    wordlist: Wordlist
        The wordlist objetc used to produce the associated scores.
    Methods
    -------
    add_additional_info(id, info)
        adds a key (id), value (info) pair to the scores dictionary
    clean_sentence(sentence: str)
        preps the sentence to be scored
    score(scoring_module: ScoringModule)
        applies the given scoring module and adds the score to the scores dictionary
    add_wordlist(wordlist: Wordlist)
        sets the wordlist for the item
    """
    def __init__(self, self_sentence: str, other_sentence: str = "") -> None:
        '''
        Initializes the Item class

                Parameters:
                        self_sentence (str): The entire response to an LEAS question or the components of the LEAS question response referencing the 'self'. 
                        other_sentence (str): the components of the LEAS question response referencing the 'other'.

                Returns:

        '''
        self.raw_input = self_sentence +". " + other_sentence
        self.self_sentence = self.clean_sentence(self_sentence)
        self.other_sentence = self.clean_sentence(other_sentence)
        self.scores = {}

        self.wordlist = None

        return

    def __str__(self):
        '''
        Handles conversion of the Item class to a str. Mainly used for display purposes.

                Parameters:
                       
                Returns:

        '''
        ret = "Self: {}\nOther: {}\n".format(self.self_sentence,self.other_sentence)
        for key in self.scores:
            ret += "{}: {}\n".format(key, self.scores[key])
        return ret

    def add_additional_info(self, id, info) -> None:
        '''
        Adds a key (id), value (info) pair to the scores dictionary. Used to add item specific, non-LEAS scoring information.

                Parameters:
                        id (any, usually str, int): The new key to be added to scores dictionary
                        info (any, usually str, int, or float): The variable associated with the id

                Returns:

        '''
        self.scores[id] = info
        return

    def clean_sentence(self, sentence: str) -> str:
        '''
        Cleans a string for further processing by the standard LEAS scoring modules. Removes punctuation and capitalization

                Parameters:
                        sentence (str): The string that will be cleaned. 
                Returns:
                        sentence (str): The cleaned string 

        '''
        sentence = str(sentence).lower()
        for c in sentence:
            if c in "-,.?!;:/\n":
                sentence = sentence.replace(c,' ')
        return sentence

    def score(self, scoring_module: ScoringModule) -> None:
        '''
        Scores the Item using the given scoring module. The score is added to the scores dictionary as follows: scores[scoring_module.id] = value

                Parameters:
                        scoring_module (ScoringModule): The scoring module that will be applied. 
                Returns:

        '''
        if isinstance(self.wordlist, Wordlist):

            scres = scoring_module.execute(self, self.wordlist)
            if isinstance(scres,tuple):
                for i in range(len(scres)):
                    self.scores[scoring_module.id+str(i+1)] = scres[i]
            else:
                self.scores[scoring_module.id] = scres
        
        else:
            raise Exception("Scoring Error: Item does not have a wordlist")
        
        return

    def add_wordlist(self, wordlist: Wordlist) -> None: 
        '''
        Sets the wordlist that the item will be scored with

                Parameters:
                        wordlist (Wordlist): The wordlist object that will be used
                Returns:

        '''
        self.wordlist = wordlist
        return
    

