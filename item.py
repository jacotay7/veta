from wordlist import Wordlist

class Item:

    def __init__(self, self_sentence, other_sentence) -> None:
        
        self.self_sentence = self.clean_sentence(self_sentence)
        self.other_sentence = self.clean_sentence(other_sentence)
        self.scores = {}

        self.wordlist = None

        return

    def __str__(self):
        ret = "Self: {}\nOther: {}\n".format(self.self_sentence,self.other_sentence)
        for key in self.scores:
            ret += "{}: {}\n".format(key, self.scores[key])
        return ret

    def add_additional_info(self, id, info):
        self.scores[id] = info
        return

    def clean_sentence(self, sentence):

        sentence = sentence.lower()
        for c in sentence:
            if c in "-,.?!;:/\n":
                sentence = sentence.replace(c,' ')
        return sentence

    def score(self, scoring_module):

        if isinstance(self.wordlist, Wordlist):

            scres = scoring_module.execute(self, self.wordlist)
            if isinstance(scres,tuple):
                for i in range(len(scres)):
                    self.scores[scoring_module.id+str(i+1)] = scres[i]
            else:
                self.scores[scoring_module.id] = scres
        
        else:
            raise Exception("Scoring Error: Item does not have a wordlist")

    def add_wordlist(self, wordlist):
        self.wordlist = wordlist
