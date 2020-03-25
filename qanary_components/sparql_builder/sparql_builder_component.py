"""
The SPARQLBuilder component generates a SPARQL query that can be used to retrieve the question's potential answer from
DBPedia Spotlight.
"""

from flask import Blueprint, Flask, render_template, jsonify, request
import os
import sys
import uuid
import json

sys.path.insert(1, '../../')

from resources.qanary_helpers import *
import config
from SPARQL.sparql_builder import SPARQLBuilder
from resources.constants import *

sparql_builder_component = Blueprint('sparql_builder_component', __name__, template_folder='templates')

with open(os.path.join(config.INTENTS_PATH, "sparql_templates.json")) as json_file:
    sparql_templates = json.load(json_file)

with open(os.path.join(config.INTENTS_PATH, "intents.json")) as json_file:
    intents = json.load(json_file)


@sparql_builder_component.route("/annotatequestion", methods=['POST'])
def qanaryService():
    """the POST endpoint required for a Qanary service"""

    triplestore_endpoint = request.json["values"]["urn:qanary#endpoint"]
    triplestore_ingraph = request.json["values"]["urn:qanary#inGraph"]
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

    if not validation_result:
        return jsonify(request.get_json())

    annotation, intent = get_annotation_and_intent(triplestore_endpoint=triplestore_endpoint,
                                                   graph=triplestore_ingraph)

    if intent == TELL_ME_MORE_TEMPLATE:
        annotation = get_coreference_uri(triplestore_endpoint=triplestore_endpoint,
                                         graph=triplestore_ingraph)

    sparql_builder = SPARQLBuilder(sparql_templates)
    query_type = intents[intent][QUERY_TYPE]

    predicates = list(intents[intent][PREDICATES])

    sparql_query = sparql_builder.generate_sparql(query_type, list(annotation.keys()), predicates)

    guid = str(uuid.uuid4())

    SPARQLquery = """
                    PREFIX oa: <http://www.w3.org/ns/openannotation/core/>

                    INSERT DATA 
                    {{ 
                        GRAPH <{graph_guid}>
                          {{ 
                            <urn:cqa:annotation:{guid}> oa:sparqlQuery \"{sparql_query}\" .
                          }}
                    }}
                """.format(graph_guid=triplestore_ingraph, guid=guid, sparql_query=sparql_query.replace("\"", "\\\""))

    insert_into_triplestore(triplestore_endpoint, triplestore_ingraph, SPARQLquery)

    return jsonify(request.get_json())


@sparql_builder_component.route("/", methods=['GET'])
def index():
    """an exemplary GET endpoint returning "hello world2 (String)"""
    print(request.host_url)
    return "Hello, World!"


@sparql_builder_component.route("/", methods=['POST'])
def indexJson():
    """a POST endpoint returning a hello world JSON"""
    data = {'Hello': 'World'}
    return jsonify(data)
