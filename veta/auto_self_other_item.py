import spacy

# Initialize spacy models with defaults
nlp_en = None
nlp_de = None

try:
    nlp_en = spacy.load("en_core_web_sm")
except:
    print("English SpaCy not detected: https://spacy.io/usage/models/")
    
try:
    nlp_de = spacy.load("de_core_news_sm")
except:
    print("German SpaCy not detected: https://spacy.io/usage/models/")

def attempt_auto_self_other(item, lang = "en") -> None:

    self_sentence = ''
    other_sentence = ''
    other_flag = False

    #Decompose the sentence
    if lang.lower() == "de" or lang.lower() == "german" or lang.lower() == "deutsch":
        if nlp_de is None:
            raise RuntimeError("German SpaCy model not available. Please install with: python -m spacy download de_core_news_sm")
        doc = nlp_de(item.raw_input)
        selfidentifiers = ['ich']
        verblist = ["würde", "wäre", "fühlt"]
        subject_identifier = 'sb'
    else:
        if nlp_en is None:
            raise RuntimeError("English SpaCy model not available. Please install with: python -m spacy download en_core_web_sm")
        doc = nlp_en(item.raw_input)
        selfidentifiers = ["i"]
        verblist = ["feel","be","feels","feeling"]
        subject_identifier = 'nsubj'

    #Loop through the sentence components
    for token in doc:
        #When we hit a sentence subject
        if token.dep_ == subject_identifier and not other_flag:
            #If it is a subject not equal to i and relates to the word feel
            #Then we flip the sentence to be about the other
            #Otherwise we assume we are discussing the self
            other_flag = (token.text.lower() not in  selfidentifiers) and (token.head.text in  verblist)
        if other_flag:
            other_sentence += token.text + ' '
        else:
            self_sentence += token.text + ' '

    item.self_sentence = item.clean_sentence(self_sentence)
    item.other_sentence = item.clean_sentence(other_sentence)
    return