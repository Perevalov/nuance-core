import os
import nltk

nltk.download('stopwords')
nltk.download('wordnet')

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

INTENTS_PATH = os.path.join(PROJECT_PATH, "intents")