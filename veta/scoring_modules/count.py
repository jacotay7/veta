from veta.scoring_modules.scoring_module import *
from veta.item import Item

class count(ScoringModule):
    """
    A class implementing the count scoring technique. Child of the ScoringModule class.
    The count scoring protocol counts how many times a particular level is found in an 
    in an LEAS item. This method ignores repeated mentioning of the same word. 

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
    id = "count"

    def __init__(self, mode = 'both', level = None, sublevel = None, binary=False, language='en') -> None:
        super().__init__(language=language)
        self.level = level
        self.sublevel = sublevel
        self.binary = binary
        self.mode = mode

        if not(self.level is None):
            self.id += '-level-' + str(self.level)

        if not(self.sublevel is None):
            self.id += '-sublevel-' + str(self.sublevel)

        self.id += '-'+str(self.mode)
        if self.binary:
            self.id += "-" + "true_false"
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
        if self.mode == 'self':
            sentence = item.self_sentence
        elif self.mode == 'other':
            sentence = item.other_sentence
        else:
            sentence = item.self_sentence + ' ' + item.other_sentence

        if (self.sublevel is None):
            frequency, matching_words, scores = self.match_words(sentence, wordlist, sublevels=False)
        else:
            frequency, matching_words, scores, subscores = self.match_words(sentence, wordlist, sublevels=True)

        #If the user has not specified the level they are interested in, do them all
        if self.level is None:
            if self.binary:
                return len(matching_words) > 1
            else:
                return len(matching_words)
        #Otherwise
        else:
            #If they have specified a subscore:
            if not(self.sublevel is None):
                #Check if we have any matches at that score and subscore
                any = np.sum((scores == self.level)&(subscores == self.sublevel)) > 0
            else:
                #Check if we have any matches at that score
                any = np.sum(scores == self.level) > 0
            #If they asked for binary output, return yes/no
            if self.binary:
                return any
            #If they want to total number of occurrences of that level
            if any:
                #If they have specified a subscore:
                if not(self.sublevel is None):
                    #Count all of the occurrences which have that level and sub level
                    return len(matching_words[(scores == self.level)&(subscores == self.sublevel)])
                else:
                    return len(matching_words[scores == self.level])
            else:
                return 0
        