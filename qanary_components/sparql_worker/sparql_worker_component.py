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
from dblayer import SPARQLWorker

sparql_worker_component = Blueprint('sparql_worker_component', __name__, template_folder='templates')

from dblayer import SPARQLWorker as sparql

@sparql_worker_component.route("/annotatequestion", methods=['POST'])
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
                      VALUES ?p {{oa:sparqlQuery}}
                      ?s ?p ?o
                    }}
                """.format(graph_guid=triplestore_ingraph)

    sparql_query = get_sparql(triplestore_endpoint=triplestore_endpoint,
                                                   graph=triplestore_ingraph,
                                                   SPARQLquery=SPARQLquery)

    result = SPARQLWorker.execute_query({"query": sparql_query})

    guid = str(uuid.uuid4())

    SPARQLquery = """
            PREFIX oa: <http://www.w3.org/ns/openannotation/core/>

            INSERT DATA 
            {{ 
                GRAPH <{graph_guid}>
                  {{ 
                    <urn:cqa:annotation:{guid}> oa:sparqlResult \"{sparql_result}\" 
                  }}
            }}
        """.format(graph_guid=triplestore_ingraph, guid=guid, sparql_result=str(result).replace("\"", "\\\""))

    insert_into_triplestore(triplestore_endpoint, triplestore_ingraph, SPARQLquery)

    return jsonify(request.get_json())

@sparql_worker_component.route("/", methods=['GET'])
def index():
    """an examplary GET endpoint returning "hello world2 (String)"""
    print(request.host_url)
    return "Hello, World!"


@sparql_worker_component.route("/", methods=['POST'])
def indexJson():
    """a POST endpoint returning a hello world JSON"""
    data = {'Hello': 'World'}
    return jsonify(data)
