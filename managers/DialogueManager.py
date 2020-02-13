import numpy as np
from nlu.ner import DBPediaSpotlightNER as ner
from dblayer import SPARQLWorker as sparql
from nlg import TemplateGenerator
from nlu.classifiers.Classifier import tell_me_more_classifier
from SPARQL.sparql_builder import SPARQLBuilder
from resources.constants import *
from resources.utils import preprocess_text, map_template_and_relation_to_intent, find_best_string_match
from nlu.ner import coreference_resolver as coref
from dblayer.sql_worker import *
import ast


class DialogueManager:
    def __init__(self, keyword_classifier, template_classifier, fwd_bwd_classifier,
                 relation_classifier, sparql_templates, intents):
        """

        :param classifier:
        :param sparql_templates:
        :param intents:
        """

        self.keyword_classifier = keyword_classifier
        self.template_classifier = template_classifier
        self.fwd_bwd_classifier = fwd_bwd_classifier
        self.relation_classifier = relation_classifier

        self.intents = intents
        self.sparql_templates = sparql_templates
        self.builder = SPARQLBuilder(self.sparql_templates)
        self.sql_worker = SQLWorker()

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

    def get_answer(self, question_text, dialogue_id):
        """

        :param question_text:
        :return:
        """

        #FOR TELL ME MORE FEATURE:
        #TODO: check the dialogue state (started, in_process). if in process -- use previous context (if necessary)
        # TODO: manually check "Tell me more about..." intent
        #TODO: check if there is some coreference in question. if not -- do as usual
        #TODO: if in process -- use previous context and cache subject (e.g. dbpedia.org/resource/Donald_Trump)
        #TODO: Tell me more about the PERSON. Compare type label with previous context.

        #FOR ENTITY RESOLUTION FEATURE:
        #TODO: run Hugginface NER over question text if automatic NED (DBpedia Spotlight) doesn't recognize anything
        #TODO: search in Wikidata for pages with label similar to Hugginface entity
        #TODO: filter ones that don't have link to dbpedia
        #TODO: find the most popular in pagerank file

        is_dialogue_exists = self.sql_worker.is_dialogue_exists(dialogue_id)

        if not is_dialogue_exists:
            self.sql_worker.create_dialogue(dialogue_id)


        preprocessed_text = preprocess_text(question_text, remove_stopwords=False)

        # Predict template
        is_tell_me_more = tell_me_more_classifier(preprocessed_text)

        if is_tell_me_more:
            template_prediction = TELL_ME_MORE_TEMPLATE
            is_confident = True
        else:
            template_prediction, is_confident = self.template_classifier.predict(preprocessed_text)

            if template_prediction == 'FWD_BWD':
                template_prediction, is_confident = self.fwd_bwd_classifier.predict(preprocessed_text)

        # Predict relation
        if template_prediction != 'distance' and template_prediction != TELL_ME_MORE_TEMPLATE:
            relation_prediction, is_confident = self.relation_classifier.predict(preprocessed_text)

            intent = map_template_and_relation_to_intent(template_prediction, relation_prediction, self.intents)

            if not is_confident:
                intent = self.keyword_classifier.predict(preprocessed_text)
        elif template_prediction == TELL_ME_MORE_TEMPLATE:
            relation_prediction = np.array(['http://dbpedia.org/ontology/abstract'])

            intent = map_template_and_relation_to_intent(template_prediction, relation_prediction, self.intents)

            if not is_confident:
                intent = self.keyword_classifier.predict(preprocessed_text)
        else:
            intent = 'distance'

        if intent == FALLBACK_CLASS:
            return "Sorry, not enough information please ask again in different way"

        has_coref = coref.has_coref(preprocessed_text)

        preprocessed_text = preprocess_text(question_text)
        annotation_dict = ner.annotate_text({"text": preprocessed_text, "confidence": 0.3})

        message_id = self.sql_worker.create_message(dialogue_id, preprocessed_text, QUESTION_TYPE, str(annotation_dict))

        if has_coref:
            last_question = self.sql_worker.get_last_question(dialogue_id)

            if last_question:
                question_1 = last_question["text"]
                answer = self.sql_worker.get_message(last_question['answer_id'])
                question_2 = question_text

                result = coref.get_coreferent_label(question_1, question_2, answer['text'])

                if result:
                    # TODO: decide which annotation should we retrieve (answer or question)
                    if result['index'] == 0:  # that means we search for question's annotation
                        annotation_dict = ast.literal_eval(last_question['annotation'])
                        label = result['label']
                        # TODO: fuzzy search for entity in annotation dict (if found - put it to annotation)
                        list_of_labels = [annotation_dict[key]['@surfaceForm'] for key in list(annotation_dict.keys())]
                        idx, ratio = find_best_string_match(list_of_labels, label)
                        uri = list(annotation_dict.keys())[idx]

                    else:
                        annotation_dict = answer['uri']

        # TODO: annotation_dict = prev_annot
        if self.validate_question(intent, annotation_dict):
            query = self.get_sparql(intent, list(annotation_dict.keys()))
            print("[SPARQL Query]: {0}".format(query))
            result = sparql.execute_query({"query": query})
            text_response, uri = TemplateGenerator.generate_answer(self.intents, intent, result, annotation_dict)

            # insert answer and update corresponding message
            answer_id = self.sql_worker.create_message(dialogue_id, preprocessed_text, ANSWER_TYPE, str(annotation_dict))
            self.sql_worker.update_answer_for_question(answer_id, message_id)

            return text_response

        return "Sorry, please ask again in different way"
