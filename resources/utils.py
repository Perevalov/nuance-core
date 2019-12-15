import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nlu.classifiers.MLClassifier import MLClassifier
from resources.constants import *
import pickle
import os
import config

#nltk.download('wordnet')
#nltk.download('stopwords')

tokenizer = RegexpTokenizer(r'\w+')
stopwords = stopwords.words('english')

def preprocess_text(text, remove_stopwords=True, lowercase=True):
    # clean_ascii
    tmp = "".join(i for i in text if ord(i) < 128)
    # lowercase
    if lowercase:
        tmp = tmp.lower()
    # normal form
    tokens = tokenizer.tokenize(tmp)
    # stopwords
    if remove_stopwords:
        prep_text = ' '.join(t for t in tokens if t not in stopwords)
    else:
        prep_text = ' '.join(t for t in tokens)

    return prep_text


def init_ml_classifiers():
    template_vectorizer = pickle.load(open(os.path.join(config.PROJECT_PATH, "models", "template_vectorizer.model"), 'rb'))
    template_encoder = pickle.load(open(os.path.join(config.PROJECT_PATH, "models", "template_encoder.model"), 'rb'))
    template_classifier = pickle.load(open(os.path.join(config.PROJECT_PATH, "models", "template_classifier.model"), 'rb'))

    fwd_bwd_vectorizer = pickle.load(open(os.path.join(config.PROJECT_PATH, "models", "fwd_bwd_vectorizer.model"), 'rb'))
    fwd_bwd_encoder = pickle.load(open(os.path.join(config.PROJECT_PATH, "models", "fwd_bwd_encoder.model"), 'rb'))
    fwd_bwd_classifier = pickle.load(open(os.path.join(config.PROJECT_PATH, "models", "fwd_bwd_classifier.model"), 'rb'))

    relation_vectorizer = pickle.load(open(os.path.join(config.PROJECT_PATH, "models", "relation_vectorizer.model"), 'rb'))
    relation_encoder = pickle.load(open(os.path.join(config.PROJECT_PATH, "models", "relation_encoder.model"), 'rb'))
    relation_classifier = pickle.load(open(os.path.join(config.PROJECT_PATH, "models", "relation_classifier.model"), 'rb'))

    template_classifier = MLClassifier(template_classifier, template_vectorizer, template_encoder)
    fwd_bwd_classifier = MLClassifier(fwd_bwd_classifier, fwd_bwd_vectorizer, fwd_bwd_encoder)
    relation_classifier = MLClassifier(relation_classifier, relation_vectorizer, relation_encoder, threshold=0.2)

    return template_classifier, fwd_bwd_classifier, relation_classifier


def map_template_and_relation_to_intent(template_prediction, relation_prediction, intents_dict):
    for intent in list(intents_dict.keys()):
        if intents_dict[intent][QUERY_TYPE] in template_prediction:
            if relation_prediction in intents_dict[intent][PREDICATES]:
                return intent

    return FALLBACK_CLASS


