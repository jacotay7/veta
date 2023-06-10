from veta.scoring_modules.scoring_module import *
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class vader(ScoringModule):

    type = "per item"
    return_length = 4
    id = "vader"

    def __init__(self) -> None:
        super().__init__()
        self.analyzer = SentimentIntensityAnalyzer()
        return

    def execute(self, item, wordlist):
        
        sentence = item.self_sentence + ' ' + item.other_sentence

        frequency, matching_words, scores = self.match_words(sentence, wordlist)

        matching_words = [x.lower() for x in list(matching_words)]

        words = [x for x in sentence.split(' ') if x != '' and x not in matching_words]
        sentence = ' '.join(words)

        #if len(words)> 1:
        try:
            res = self.analyzer.polarity_scores(sentence)
            return (res["neg"], res["neu"], res["pos"], res["compound"])
        except:
            print("Something went wrong with Vader. Setence Given: {}".format(sentence)) 
            return (0,0,0,0)
