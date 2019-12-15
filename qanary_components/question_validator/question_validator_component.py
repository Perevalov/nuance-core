from flask import Blueprint, Flask, render_template, jsonify, request
import pickle
import os
import sys
import uuid
import json

sys.path.insert(1, '../../')

from resources.qanary_helpers import *
import config
from resources.constants import *

question_validator_component = Blueprint('question_validator_component', __name__, template_folder='templates')

with open(os.path.join(config.INTENTS_PATH, "intents.json")) as json_file:
    intents = json.load(json_file)

with open(os.path.join(config.INTENTS_PATH, "sparql_templates.json")) as json_file:
    sparql_templates = json.load(json_file)

def validate_question(intent: str, annotation_dict):
    """
    Checks if the number of parameters in query equals retrieved parameters
    :param q_class:
    :param annotation_dict:
    :return:
    """
    if len(list(annotation_dict.keys())) < 1:
        return False

    query_type = intents[intent][QUERY_TYPE]

    # TODO remove debug tmp variables
    tmp = sparql_templates[query_type][PARAMETER_NUM]
    tmp1 = len(list(annotation_dict.keys()))
    if len(list(annotation_dict.keys())) == int(sparql_templates[query_type][PARAMETER_NUM]):
        return True
    else:
        return False

@question_validator_component.route("/annotatequestion", methods=['POST'])
def qanaryService():
    """the POST endpoint required for a Qanary service"""
    
    triplestore_endpoint = request.json["values"]["urn:qanary#endpoint"]
    triplestore_ingraph  = request.json["values"]["urn:qanary#inGraph"]
    triplestore_outgraph = request.json["values"]["urn:qanary#outGraph"]

    SPARQLquery = """
                    PREFIX oa: <http://www.w3.org/ns/openannotation/core/>

                    SELECT ?p ?o
                    FROM <{graph_guid}>
                    WHERE 
                    {{
                      VALUES ?p {{oa:spotlightAnnotation oa:intent}}
                      ?s ?p ?o
                    }}
                """.format(graph_guid=triplestore_ingraph)

    annotation, intent = get_annotation_and_intent(triplestore_endpoint=triplestore_endpoint,
                                                                graph=triplestore_ingraph,
                                                                SPARQLquery=SPARQLquery)

    validation_result = validate_question(intent, annotation)

    guid = str(uuid.uuid4())

    SPARQLquery = """
                PREFIX oa: <http://www.w3.org/ns/openannotation/core/>

                INSERT DATA 
                {{ 
                    GRAPH <{graph_guid}>
                      {{ 
                        <urn:cqa:annotation:{guid}> oa:isQuestionValidated oa:boolean:{is_valid} .
                      }}
                }}
            """.format(graph_guid=triplestore_ingraph, guid=guid, is_valid=validation_result)

    insert_into_triplestore(triplestore_endpoint, triplestore_ingraph, SPARQLquery)


    print(triplestore_ingraph)
    print("endpoint: %s, ingraph: %s, outGraph: %s" % (triplestore_endpoint, triplestore_ingraph, triplestore_outgraph))

	# add your functionality here    

    return jsonify(request.get_json())

@question_validator_component.route("/", methods=['GET'])
def index():
    """an examplary GET endpoint returning "hello world2 (String)"""
    print(request.host_url)
    return "Hello, World!"


@question_validator_component.route("/", methods=['POST'])
def indexJson():
    """a POST endpoint returning a hello world JSON"""
    data = {'Hello': 'World'}
    return jsonify(data)
