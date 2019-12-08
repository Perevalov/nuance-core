import config
import operator
import os
from resources.constants import KEYWORDS, FALLBACK_CLASS


class KeywordClassifier:
    def __init__(self, intents, threshold=0.01):
        """

        :param intents: dict
        :param threshold: float
        """
        self.THRESHOLD = threshold
        self.intents = intents

    def get_class(self, user_text):
        # TODO add weights to keywords

        scores_dict = dict()

        for intent in self.intents.keys():
            keywords = self.intents[intent][KEYWORDS]
            score = 0
            for kw in keywords:
                score += user_text.count(kw)
            scores_dict[intent] = score

        intent = max(scores_dict.items(), key=operator.itemgetter(1))[0]
        max_score = max(scores_dict.items(), key=operator.itemgetter(1))[1]

        if max_score <= self.THRESHOLD:
            intent = FALLBACK_CLASS

        return intent
