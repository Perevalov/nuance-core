import config
import operator
import os
from resources.constants import KEYWORDS, FALLBACK_CLASS
from nlu.classifiers.Classifier import Classifier

class KeywordClassifier(Classifier):
    def __init__(self, intents, threshold=0.01):
        """

        :param intents: dict
        :param threshold: float
        """
        self.THRESHOLD = threshold
        self.intents = intents

    def predict(self, user_text):
        #TODO add weights to keywords

        scores_dict = dict()

        for intent in self.intents.keys():
            keywords = self.intents[intent][KEYWORDS]
            score = 0
            for kw in keywords:
                for word in user_text.split():
                    if word == kw:
                        score += 1
            scores_dict[intent] = score

        intent = max(scores_dict.items(), key=operator.itemgetter(1))[0]
        max_score = max(scores_dict.items(), key=operator.itemgetter(1))[1]

        if max_score <= self.THRESHOLD:
            intent = FALLBACK_CLASS

        return intent
