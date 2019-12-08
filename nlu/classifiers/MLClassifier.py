import config
import operator
import os
from resources.constants import KEYWORDS, FALLBACK_CLASS
from nlu.classifiers.Classifier import Classifier


class MLClassifier(Classifier):
    def __init__(self, classifier_model, vectorizer_model, label_encoder_model, threshold=0.3):

        self.THRESHOLD = threshold
        self.classifier_model = classifier_model
        self.vectorizer_model = vectorizer_model
        self.label_encoder_model = label_encoder_model

    def predict(self, text):
        vector = self.vectorizer_model.transform([text])
        prediction = self.classifier_model.predict(vector)
        probas = self.classifier_model.predict_proba(vector)

        _class = self.label_encoder_model.inverse_transform(prediction)

        #if the maximum probability bigger than the threshold then classifier is confident
        is_confident_enough = max(probas[0]) > self.THRESHOLD

        return _class, is_confident_enough


