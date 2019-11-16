from nlu.ner import DBPediaSpotlightNER as ner
from dblayer import SPARQLWorker as sparql
from nlg import TemplateGenerator
from resources.constants import PARAMETER_NUM, QUERY_TYPE, QUERY, PREDICATE, FALLBACK_CLASS
from resources.utils import preprocess_text


class DialogueManager:
    def __init__(self, classifier, sparql, intents):
        """

        :param classifier:
        :param sparql:
        :param intents:
        """

        self.classifier = classifier
        self.sparql = sparql
        self.intents = intents

    def validate_question(self, q_class: str, annotation_dict):
        """
        Checks if the number of parameters in query equals retrieved parameters
        :param q_class:
        :param annotation_dict:
        :return:
        """

        query_type = self.intents[q_class][QUERY_TYPE]

        tmp = self.sparql[query_type][PARAMETER_NUM]
        tmp1 = len(list(annotation_dict.keys()))
        if len(list(annotation_dict.keys())) == int(self.sparql[query_type][PARAMETER_NUM]):
            return True
        else:
            return False

    def get_sparql(self, question_intent, params):
        # TODO add optional statement loop and modify intents.

        query_type = self.intents[question_intent][QUERY_TYPE]
        query = self.sparql[query_type][QUERY]

        if query_type == "forward" or query_type == "backward":
            predicate = self.intents[question_intent][PREDICATE]
            query = query.format(entity=list(params.keys())[0], predicate=predicate)
        elif query_type == "distance":
            query = query.format(point_1=list(params.keys())[0], point_2=list(params.keys())[1])
        elif query_type == "boolean":
            # TODO Add relation classifier
            #predicate = self.intents[question_intent][PREDICATE]
            query = query.format(entity_1=list(params.keys())[0], entity_2=list(params.keys())[1])

        return query


    def get_answer(self, question_text):
        """

        :param question_text:
        :return:
        """
        preprocessed_text = preprocess_text(question_text, remove_stopwords=False)
        intent = self.classifier.get_class(preprocessed_text)

        if intent == FALLBACK_CLASS:
            return "Sorry, not enough information please ask again in different way"

        preprocessed_text = preprocess_text(question_text)
        annotation_dict = ner.annotate_text({"text": preprocessed_text, "confidence": 0.3})

        if self.validate_question(intent, annotation_dict):
            query = self.get_sparql(intent, annotation_dict)
            result = sparql.execute_query({"query": query})
            text_response = TemplateGenerator.generate_answer(self.intents, intent, result)
            return text_response

        return "Sorry, not enough information please ask again in different way"
