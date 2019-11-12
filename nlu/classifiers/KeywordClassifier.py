import config
import operator
import os
from resources import constants


def read_keywords(class_name):
    lines = []

    with open(os.path.join(config.INTENTS_PATH, class_name, "keywords.txt")) as f:
        lines = f.read().splitlines()

    return lines


class KeywordClassifier:
    def __init__(self, classes):
        self.classes = classes

    def get_class(self, user_text):
        scores_dict = dict()

        for cls in self.classes:
            keywords = read_keywords(cls)
            score = 0
            for kw in keywords:
                for word in user_text.split():
                    if word == kw:
                        score += 1
            scores_dict[cls] = score

        res_class = max(scores_dict.items(), key=operator.itemgetter(1))[0]
        max_score = max(scores_dict.items(), key=operator.itemgetter(1))[1]

        if max_score == 0:
            res_class = constants.FALLBACK_CLASS

        return res_class
