import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords

#nltk.download('wordnet')
#nltk.download('stopwords')

tokenizer = RegexpTokenizer(r'\w+')
stopwords = stopwords.words('english')

def preprocess_text(text, remove_stopwords=True):
    # clean_ascii
    tmp = "".join(i for i in text if ord(i) < 128)
    # lowercase
    tmp = tmp.lower()
    # normal form
    tokens = tokenizer.tokenize(tmp)
    # stopwords
    if remove_stopwords:
        prep_text = ' '.join(t for t in tokens if t not in stopwords)
    else:
        prep_text = ' '.join(t for t in tokens)

    return prep_text