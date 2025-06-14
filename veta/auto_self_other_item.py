import spacy
from veta.logger import get_logger

# Initialize logger for this module
logger = get_logger('auto_self_other_item')

# Initialize spacy models with defaults
nlp_en = None
nlp_de = None

try:
    nlp_en = spacy.load("en_core_web_sm")
    logger.info("English SpaCy model loaded successfully")
except:
    logger.warning("English SpaCy not detected: https://spacy.io/usage/models/")
    print("English SpaCy not detected: https://spacy.io/usage/models/")
    
try:
    nlp_de = spacy.load("de_core_news_sm")
    logger.info("German SpaCy model loaded successfully")
except:
    logger.warning("German SpaCy not detected: https://spacy.io/usage/models/")
    print("German SpaCy not detected: https://spacy.io/usage/models/")

def attempt_auto_self_other(item, lang = "en") -> None:
    logger.debug(f"Attempting auto self/other separation for language: {lang}")

    self_sentence = ''
    other_sentence = ''
    other_flag = False

    #Decompose the sentence
    if lang.lower() == "de" or lang.lower() == "german" or lang.lower() == "deutsch":
        logger.debug("Using German language processing")
        if nlp_de is None:
            logger.error("German SpaCy model not available")
            raise RuntimeError("German SpaCy model not available. Please install with: python -m spacy download de_core_news_sm")
        doc = nlp_de(item.raw_input)
        selfidentifiers = ['ich']
        verblist = ["würde", "wäre", "fühlt"]
        subject_identifier = 'sb'
    else:
        logger.debug("Using English language processing")
        if nlp_en is None:
            logger.error("English SpaCy model not available")
            raise RuntimeError("English SpaCy model not available. Please install with: python -m spacy download en_core_web_sm")
        doc = nlp_en(item.raw_input)
        selfidentifiers = ["i"]
        verblist = ["feel","be","feels","feeling"]
        subject_identifier = 'nsubj'

    logger.debug(f"Processing sentence with {len(doc)} tokens")

    #Loop through the sentence components
    for token in doc:
        #When we hit a sentence subject
        if token.dep_ == subject_identifier and not other_flag:
            #If it is a subject not equal to i and relates to the word feel
            #Then we flip the sentence to be about the other
            #Otherwise we assume we are discussing the self
            other_flag = (token.text.lower() not in  selfidentifiers) and (token.head.text in  verblist)
            if other_flag:
                logger.debug(f"Switched to 'other' context at token: {token.text}")
        if other_flag:
            other_sentence += token.text + ' '
        else:
            self_sentence += token.text + ' '

    item.self_sentence = item.clean_sentence(self_sentence)
    item.other_sentence = item.clean_sentence(other_sentence)
    
    logger.info(f"Auto-separated - Self: '{item.self_sentence[:30]}...', Other: '{item.other_sentence[:30]}...'")
    return