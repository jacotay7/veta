from veta.item import Item
from veta.wordlist import Wordlist
from veta.logger import get_logger
import numpy as np

# Initialize logger for this module
logger = get_logger('respondent')

total_respondents = 0

class Respondent:
    """
    A class representing a single respondent of an LEAS survey. The class includes all of the LEAS items (question responses) 
    as well as meta data about the respondent (e.g. age, gender, education). 
    ...

    Attributes
    ----------
    items: list
        a list containing all of the LEAS items belonging to the Respondent.
    id: int
        a unique number representing the respondent.
    wordlist: Wordlist
        the wordlist object used to produce the associated scores.
    totals: dict
        a dictionary containing the sums of all of the scoring methods applied to each member of the items list
    Methods
    -------
    __str__()
        handles conversion of the respondent to a string object for display
    to_array()
        returns all of the respondent's data as a numpy array
    add_item(*sentences)
        instanciates a new LEAS item and adds it to the items list
    add_additional_info(id, data)
        adds a new key, value pair to the totals dict (totals[id] = data)
    score(*modules)
        scores all of the respondent's items for all of the modules passed to the function
    add_wordlist(wordlist: Wordlist)
        sets the wordlist for the respondent and all of its items
    """
    def __init__(self, userid=None, wordlist_file=None) -> None:
        
        global total_respondents

        logger.debug(f"Initializing new Respondent with userid={userid}, wordlist_file={wordlist_file}")

        self.items = []
        self.id = total_respondents
        self.userid = None
        if isinstance(userid, str):
            self.userid = userid
            logger.debug(f"Set userid to: {userid}")
        self.wordlist = None
        if isinstance(wordlist_file, str):
            logger.info(f"Loading wordlist from file: {wordlist_file}")
            wordlist = Wordlist(wordlist_file)
            self.add_wordlist(wordlist)

        total_respondents += 1
        #self.modules_ran = set()
        self.totals = {}
        self.col_names = []

        logger.info(f"Created Respondent {self.id} (userid: {self.userid or 'None'})")
        return

    def __str__(self) -> str:
        '''
        Handles conversion of the Respondent class to a str. Mainly used for display purposes.

                Parameters:
                       
                Returns:
                        respondent (str): The respondent information as a string

        '''
        if isinstance(self.userid, str):
            ret = f"Respondent ID {self.userid}:\n\n"
        else:
            ret = f"Respondent ID {self.id}:\n\n"
        # ret += "Scores:\n"

        i = 1
        for item in self.items:
            ret += "Item {}:\n".format(i)
            ret += str(item) + '\n'
            i += 1
        return ret.rstrip()

    def to_array(self) -> np.array:
        '''
        Handles conversion of the Respondent class to a numpy array. 

                Parameters:
                       
                Returns:
                        respondent (np.array): The respondent information as a numpy array
        '''
        if len(self.items) == 0:
            return np.empty((0,0))
        
        # if len(self.items[0].scores.keys()) == 0:
        #     return np.empty((0,0))

        module_names = list(self.items[0].scores.keys())
        total_names = list(self.totals.keys())
        #print(module_names)
        module_names.sort()
        total_names.sort()

        full_data = np.zeros((len(self.items)+1, len(total_names)))
        for i in range(len(self.items)):
            item = self.items[i]
            for j in range(len(total_names)):
                total_name = total_names[j]
                if total_name in module_names:
                    full_data[i,j] = item.scores[total_name]
        
        for i in range(len(total_names)):
            total_name = total_names[i]
            # print(total_name, total_names)
            full_data[-1,i] = self.totals[total_name]
        self.col_names = total_names
        return full_data

    def add_item(self, *sentences) -> Item:
        '''
        Instanciates a new LEAS item and adds it to the items list.

                Parameters:
                        sentences (tuple): the sentences that will be used to instanciate the new Item class.
                Returns:
                        item (Item): The new item that was created.
        '''
        logger.debug(f"Adding item to Respondent {self.id}. Sentences: {len(sentences)} provided")
        
        if len(sentences) == 1 and isinstance(sentences[0], Item):
            item = sentences[0]
            logger.debug("Using existing Item object")
        else:
            item = Item(*sentences)
            item.add_wordlist(self.wordlist)
            logger.debug("Created new Item from sentences")
        
        if 'index' not in item.scores.keys():
            item.add_additional_info("index", len(self.items)+1)
        
        if not (self.wordlist is None):
            item.add_wordlist(self.wordlist)
            
        self.items.append(item)
        logger.info(f"Added item {len(self.items)} to Respondent {self.id}")
        return item

    
    def add_additional_info(self, id, data) -> None:
        '''
        Adds a new key, value pair to the totals dict (totals[id] = data)

                Parameters:
                        id (any): the key that will hold data in the totals dict
                        data (any): the data to be added to the totals dict
                Returns:

        '''
        logger.debug(f"Adding additional info to Respondent {self.id}: {id} = {data}")
        self.totals[id] = data
        return


    def score(self, *modules) -> None:
        '''
        Scores all of the items in the respondent's items list using all of the specified scoring modules.
        The modules are applied per item or per respondent as indicated by the module type. The totals are
        added to the totals dict.

                Parameters:
                        modules (tuple): the scoring modules to be run on the respondent's items.
                Returns:

        '''
        logger.info(f"Scoring Respondent {self.id} with {len(modules)} modules")
        
        for module in modules:
            logger.debug(f"Applying module: {getattr(module, 'id', str(module))} (type: {getattr(module, 'type', 'unknown')})")
            
            if module.type == "per item":
                #total = 0
                for i, item in enumerate(self.items):
                    logger.debug(f"Scoring item {i+1} with module {getattr(module, 'id', str(module))}")
                    item.score(module)
                    #total += item.scores[module.id]
            elif module.type == "per respondent":
                logger.debug(f"Applying per-respondent module: {getattr(module, 'id', str(module))}")
                for item in self.items:
                    item.scores[module.id] = 0
                total = module.execute(self.items, self.wordlist)
            #self.modules_ran.add(module.id)
                self.totals[module.id] = total
                logger.debug(f"Per-respondent module result: {total}")
                
        self.compute_totals()
        logger.info(f"Completed scoring for Respondent {self.id}")
        return

    def compute_totals(self):
        logger.debug(f"Computing totals for Respondent {self.id}")
        if len(self.items) < 1:
            logger.warning(f"No items found for Respondent {self.id}, cannot compute totals")
            return
        for ids in self.items[0].scores.keys():
            total = 0
            for item in self.items:
                total += item.scores[ids]
            if total != 0 or ids not in self.totals.keys():
                self.totals[ids] = total
        logger.debug(f"Computed totals for {len(self.totals)} scoring methods")

    def add_wordlist(self, wordlist: Wordlist) -> None:
        '''
        Sets the wordlist that the respondent's items will be scored with

                Parameters:
                        wordlist (Wordlist): The wordlist object that will be used
                Returns:

        '''
        logger.info(f"Setting wordlist for Respondent {self.id}")
        self.wordlist = wordlist
        for i, item in enumerate(self.items):
            logger.debug(f"Adding wordlist to item {i+1}")
            item.add_wordlist(wordlist)
        logger.debug(f"Wordlist added to {len(self.items)} items")
        return

