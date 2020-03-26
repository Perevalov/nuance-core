"""
If two or more of the current question's entities are related in a way not governed by the query template,
the relation_classifier component will resolve the relation and store it to the current question's subgraph as
oa:relation
"""
from flask import Blueprint, Flask, render_template, jsonify, request
import pickle
import os
import sys
import uuid
import json
import numpy as np

sys.path.insert(1, '../../')

from resources.qanary_helpers import *
from resources.constants import *
import config
from nlu.classifiers.MLClassifier import MLClassifier
from resources.constants import *
from resources.utils import preprocess_text, map_template_and_relation_to_intent

relation_classifier_component = Blueprint('relation_classifier_component', __name__, template_folder='templates')

#loading the model
relation_vectorizer = pickle.load(open(os.path.join(config.PROJECT_PATH, "models", "relation_vectorizer.model"), 'rb'))
relation_encoder = pickle.load(open(os.path.join(config.PROJECT_PATH, "models", "relation_encoder.model"), 'rb'))
relation_classifier = pickle.load(open(os.path.join(config.PROJECT_PATH, "models", "relation_classifier.model"), 'rb'))

relation_classifier = MLClassifier(relation_classifier, relation_vectorizer, relation_encoder)

with open(os.path.join(config.INTENTS_PATH, "intents.json")) as json_file:
    intents = json.load(json_file)

@relation_classifier_component.route("/annotatequestion", methods=['POST'])
def qanaryService():
    """the POST endpoint required for a Qanary service"""
    
    triplestore_endpoint = request.json["values"]["urn:qanary#endpoint"]
    triplestore_ingraph  = request.json["values"]["urn:qanary#inGraph"]
    triplestore_outgraph = request.json["values"]["urn:qanary#outGraph"]

    text = get_text_question_in_graph(triplestore_endpoint=triplestore_endpoint, graph=triplestore_ingraph)[0]['text']
    # TODO: this is temporary solution
    text = text.split('$')[0]

    print("Question Text: {0}".format(text))
    preprocessed_text = preprocess_text(text, remove_stopwords=False)
    print("Preprocessed text: {0}".format(preprocessed_text))

    SPARQLquery = """
                    PREFIX oa: <http://www.w3.org/ns/openannotation/core/>

                    SELECT ?p ?o
                    FROM <{graph_guid}>
                    WHERE 
                    {{
                      VALUES ?p {{oa:templateType oa:isTemplateClassifierConfident}}
                      ?s ?p ?o
                    }}
                """.format(graph_guid=triplestore_ingraph)

    template_prediction, is_confident = get_template_prediction(triplestore_endpoint=triplestore_endpoint,
                                                                graph=triplestore_ingraph,
                                                                SPARQLquery=SPARQLquery)

    if template_prediction == TELL_ME_MORE_TEMPLATE:
        relation_prediction = np.array(['http://dbpedia.org/ontology/abstract'])
    else:
        relation_prediction, is_confident = relation_classifier.predict(preprocessed_text)

    guid = str(uuid.uuid4())

    intent = map_template_and_relation_to_intent(template_prediction, relation_prediction, intents)

    SPARQLquery = """
            PREFIX oa: <http://www.w3.org/ns/openannotation/core/>

            INSERT DATA 
            {{ 
                GRAPH <{graph_guid}>
                  {{ 
                    <urn:cqa:annotation:{guid}> oa:relation <{relation}> . 
                    <urn:cqa:annotation:{guid}> oa:intent oa:intent:{intent} 
                  }}
            }}
        """.format(graph_guid=triplestore_ingraph, guid=guid, relation=relation_prediction[0],
                   intent=intent)

    insert_into_triplestore(triplestore_endpoint, triplestore_ingraph, SPARQLquery)

    print(triplestore_ingraph)
    print("endpoint: %s, ingraph: %s, outGraph: %s" % (triplestore_endpoint, triplestore_ingraph, triplestore_outgraph))

	# add your functionality here    

    return jsonify(request.get_json())

@relation_classifier_component.route("/", methods=['GET'])
def index():
    """an examplary GET endpoint returning "hello world2 (String)"""
    print(request.host_url)
    return "Hello, World!"


@relation_classifier_component.route("/", methods=['POST'])
def indexJson():
    """a POST endpoint returning a hello world JSON"""
    data = {'Hello': 'World'}
    return jsonify(data)
