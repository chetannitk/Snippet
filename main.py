from nlp_utils.data_cleaning import *

if __name__ == '__main__':
    sents = [r"my name is     chetan chauhan. I won't work for it" ,  'My name is! chetan chauhan']
    print(normalize_contractions(sents))
