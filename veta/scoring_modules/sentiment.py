from veta.scoring_modules.scoring_module import *

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
except:
    print("Vader not installed. Try running: pip install vaderSentiment")

try:
    from germansentiment import SentimentModel
except:
    print("German Sentiment not installed. For German sentiment try running: pip install germansentiment")


class sentiment(ScoringModule):

    type = "per item"
    return_length = 4
    id = "sentiment-"

    #language_codes = ["en", "fr", "de", "es", "it", "ru", "ja", "ar", "zh-CN", "zh-TW"]

    def __init__(self, lang = 'en') -> None:
        super().__init__()
        self.lang = lang.lower()

        if self.lang == 'de':
            self.model = SentimentModel()
        else:
            self.analyzer = SentimentIntensityAnalyzer()

        return

    def execute(self, item, wordlist):
        
        sentence = item.self_sentence + ' ' + item.other_sentence

        if self.lang == 'de':
            classes, probabilities = self.model.predict_sentiment([sentence], output_probabilities = True) 
            ratings = [round(i[1],2) for i in probabilities[0]]
            ratings.append(round(ratings[0]-ratings[1],2))
            return tuple(ratings)

        # Translation using MY MEMORY
        # if self.lang != 'en':
        #     # using   MY MEMORY NET   http://mymemory.translated.net
        #     api_url = "http://mymemory.translated.net/api/get?q={}&langpair={}|{}".format(sentence, self.lang,
        #                                                                                     'en')
        #     hdrs = {
        #         'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        #         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        #         'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        #         'Accept-Encoding': 'none',
        #         'Accept-Language': 'en-US,en;q=0.8',
        #         'Connection': 'keep-alive'}
        #     response = requests.get(api_url, headers=hdrs)
        #     response_json = json.loads(response.text)
        #     sentence = response_json["responseData"]["translatedText"]
        else:
            try:
                res = self.analyzer.polarity_scores(sentence)
                return (res["neg"], res["neu"], res["pos"], res["compound"])
            except:
                print("Something went wrong with Vader. Setence Given: {}".format(sentence)) 
                return (0,0,0,0)
