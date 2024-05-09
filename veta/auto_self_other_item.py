import spacy
nlp = spacy.load("en_core_web_sm")

def attempt_auto_self_other(item) -> None:

    self_sentence = ''
    other_sentence = ''
    other_flag = False

    #Decompose the sentence
    doc = nlp(item.raw_input)
    #Loop through the sentence components
    for token in doc:
        #When we hit a sentence subject
        if token.dep_ == 'nsubj' and not other_flag:
            #If it is a subject not equal to i and relates to the word feel
            #Then we flip the sentence to be about the other
            #Otherwise we assume we are discussing the self
            other_flag = (token.text.lower() != 'i') and (token.head.text in ["feel","be","feels","feeling"] )
        if other_flag:
            other_sentence += token.text + ' '
        else:
            self_sentence += token.text + ' '

    item.self_sentence = item.clean_sentence(self_sentence)
    item.other_sentence = item.clean_sentence(other_sentence)
    return