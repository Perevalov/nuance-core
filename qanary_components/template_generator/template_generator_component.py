from flask import Blueprint, Flask, render_template, jsonify, request
import os
import sys
import uuid
import json

sys.path.insert(1, '../../')

from resources.qanary_helpers import *
from nlg import TemplateGenerator
import config

template_generator_component = Blueprint('template_generator_component', __name__, template_folder='templates')

with open(os.path.join(config.INTENTS_PATH, "intents.json")) as json_file:
    intents = json.load(json_file)


@template_generator_component.route("/text_answer", methods=['GET'])
def get_text_answer():
    triplestore_endpoint = request.args["endpoint"]
    triplestore_ingraph = request.args["inGraph"]
    print(triplestore_ingraph)

    SPARQLquery = """
                        PREFIX oa: <http://www.w3.org/ns/openannotation/core/>

                        SELECT ?p ?o
                        FROM <{graph_guid}>
                        WHERE 
                        {{
                          VALUES ?p {{oa:textResponse}}
                          ?s ?p ?o
                        }}
                    """.format(graph_guid=triplestore_ingraph)

    text_response = get_text_response(triplestore_endpoint=triplestore_endpoint,
                                                   graph=triplestore_ingraph,
                                                   SPARQLquery=SPARQLquery)

    return jsonify({"answer": text_response})

@template_generator_component.route("/annotatequestion", methods=['POST'])
def qanaryService():
    """the POST endpoint required for a Qanary service"""
    
    triplestore_endpoint = request.json["values"]["urn:qanary#endpoint"]
    triplestore_ingraph  = request.json["values"]["urn:qanary#inGraph"]
    triplestore_outgraph = request.json["values"]["urn:qanary#outGraph"]
    print(triplestore_ingraph)
    print("endpoint: %s, ingraph: %s, outGraph: %s" % (triplestore_endpoint, triplestore_ingraph, triplestore_outgraph))

    SPARQLquery = """
                    PREFIX oa: <http://www.w3.org/ns/openannotation/core/>

                    SELECT ?p ?o
                    FROM <{graph_guid}>
                    WHERE 
                    {{
                      VALUES ?p {{oa:isQuestionValidated}}
                      ?s ?p ?o
                    }}
                """.format(graph_guid=triplestore_ingraph)

    validation_result = get_validation_result(triplestore_endpoint=triplestore_endpoint,
                                              graph=triplestore_ingraph,
                                              SPARQLquery=SPARQLquery)

    if validation_result:
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

        SPARQLquery = """
                        PREFIX oa: <http://www.w3.org/ns/openannotation/core/>
    
                        SELECT ?p ?o
                        FROM <{graph_guid}>
                        WHERE 
                        {{
                          VALUES ?p {{oa:sparqlResult}}
                          ?s ?p ?o
                        }}
                    """.format(graph_guid=triplestore_ingraph)

        sparql_result = get_sparql_result(triplestore_endpoint=triplestore_endpoint,
                                                       graph=triplestore_ingraph,
                                                       SPARQLquery=SPARQLquery)

        text_response = TemplateGenerator.generate_answer(intents, intent, sparql_result, annotation)

    else:
        text_response = "Sorry, please ask again in different way"

    guid = str(uuid.uuid4())

    SPARQLquery = """
                PREFIX oa: <http://www.w3.org/ns/openannotation/core/>

                INSERT DATA 
                {{ 
                    GRAPH <{graph_guid}>
                      {{ 
                        <urn:cqa:annotation:{guid}> oa:textResponse \"{text_response}\" 
                      }}
                }}
            """.format(graph_guid=triplestore_ingraph, guid=guid, text_response=text_response)

    insert_into_triplestore(triplestore_endpoint, triplestore_ingraph, SPARQLquery)

    return jsonify(request.get_json())

@template_generator_component.route("/", methods=['GET'])
def index():
    """an examplary GET endpoint returning "hello world2 (String)"""
    print(request.host_url)
    return "Hello, World!"


@template_generator_component.route("/", methods=['POST'])
def indexJson():
    """a POST endpoint returning a hello world JSON"""
    data = {'Hello': 'World'}
    return jsonify(data)
