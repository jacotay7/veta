from item import *
from wordlist import Wordlist
import numpy as np

total_respondents = 0

class Respondent:

    def __init__(self, wordlist_file=None) -> None:
        
        global total_respondents

        self.items = []
        self.id = total_respondents
        self.wordlist = None
        if isinstance(wordlist_file, str):
            wordlist = Wordlist(wordlist_file)
            self.add_wordlist(wordlist)

        total_respondents += 1
        #self.modules_ran = set()
        self.totals = {}

        return
    
    def add_item(self, *sentences):

        item = Item(*sentences)
        item.add_wordlist(self.wordlist)
        self.items.append(item)

        return item
    
    
    def add_additional_info(self, id, data):

        self.totals[id] = data


    def score(self, *modules):
        
        for module in modules:
            if module.type == "per item":
                #total = 0
                for item in self.items:
                    item.score(module)
                    #total += item.scores[module.id]
            elif module.type == "per respondent":
                for item in self.items:
                    item.scores[module.id] = 0
                total = module.execute(self.items, self.wordlist)
            #self.modules_ran.add(module.id)
                self.totals[module.id] = total
        for ids in self.items[0].scores.keys():
            total = 0
            for item in self.items:
                total += item.scores[ids]
            if total != 0 or ids not in self.totals.keys():
                self.totals[ids] = total

        return

    def __str__(self):
        ret = ""
        i = 1
        for item in self.items:
            ret += "Item {}:\n".format(i)
            ret += str(item) + '\n'
            i += 1
        return ret.rstrip()

    def add_wordlist(self, wordlist):
        self.wordlist = wordlist
        for item in self.items:
            item.add_wordlist(wordlist)

    def to_array(self):

        if len(self.items) == 0:
            return np.empty((0,0))
        
        if len(self.items[0].scores.keys()) == 0:
            return np.empty((0,0))

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
            full_data[-1,i] = self.totals[total_name]

        return full_data