import os
import config
from nlu.ner import DBPediaSpotlightNER as ner
from dblayer import SPARQLWorker as sparql
from nlg import TemplateGenerator

class DialogueManager:
    def __init__(self, classifier, ner=None, sparql=None):
        self.classifier = classifier
        self.ner = ner
        self.sparql = sparql

    def validate_question(self, q_class, annotation):
        #TODO validate all parameters
        return True

    def get_sparql(self, q_class, params):

        with open(os.path.join(config.INTENTS_PATH, q_class, "query.sparql")) as f:
            query = f.read()

        #TODO: make more precise formatting
        param_arr = [p for p in list(params.keys())]

        return query.format(*param_arr)


    def get_answer(self, question_text):
        q_class = self.classifier.get_class(question_text)

        annotation = ner.annotate_text({"text": question_text, "confidence": 0.3})

        if self.validate_question(q_class, annotation):
            query = self.get_sparql(q_class, annotation)
            result = sparql.execute_query({"query": query})
            text_response = TemplateGenerator.generate_answer(q_class, result)
            return text_response

        return "Sorry, not enough information please ask again in different way"
