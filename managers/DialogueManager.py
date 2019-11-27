from nlu.ner import DBPediaSpotlightNER as ner
from dblayer import SPARQLWorker as sparql
from nlg import TemplateGenerator
from SPARQL.sparql_builder import SPARQLBuilder, generate_label_query
from resources.constants import PARAMETER_NUM, QUERY_TYPE, QUERY, PREDICATES, FALLBACK_CLASS
from resources.utils import preprocess_text


class DialogueManager:
    def __init__(self, classifier, sparql_templates, intents):
        """

        :param classifier:
        :param sparql_templates:
        :param intents:
        """

        self.classifier = classifier
        self.intents = intents
        self.sparql_templates = sparql_templates
        self.builder = SPARQLBuilder(self.sparql_templates)

    def validate_question(self, q_class: str, annotation_dict):
        """
        Checks if the number of parameters in query equals retrieved parameters
        :param q_class:
        :param annotation_dict:
        :return:
        """

        query_type = self.intents[q_class][QUERY_TYPE]

        # TODO remove debug tmp variables
        tmp = self.sparql_templates[query_type][PARAMETER_NUM]
        tmp1 = len(list(annotation_dict.keys()))
        if len(list(annotation_dict.keys())) == int(self.sparql_templates[query_type][PARAMETER_NUM]):
            return True
        else:
            return False

    def get_sparql(self, question_intent, entities):
        # TODO add optional statement loop and modify intents.

        query_type = self.intents[question_intent][QUERY_TYPE]
        predicates: list
        # Not every question_intent has predicates assigned to it, so we need to move on even if none are found
        try:
            predicates = list(self.intents[question_intent][PREDICATES])
        except KeyError:
            predicates = list()

        query = self.builder.generate_sparql(query_type, entities, predicates)

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
            query = self.get_sparql(intent, list(annotation_dict.keys()))
            print("[SPARQL Query]: {0}".format(query))
            result = sparql.execute_query({"query": query})
            text_response = TemplateGenerator.generate_answer(self.intents, intent, result, annotation_dict)
            return text_response

        return "Sorry, please ask again in different way"
