"""
The sparql_worker component executes the current question's sparql query saved under oa:sparqlQuery on the DBpedia API
and stores the result under oa:sparqlResult in the current question's subgraph
"""
import sys

from flask import Blueprint, jsonify, request

sys.path.insert(1, '../../')

from resources.qanary_helpers import *
from dblayer import SPARQLWorker

sparql_worker_component = Blueprint('sparql_worker_component', __name__, template_folder='templates')


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
                                  VALUES ?p {{oa:isQuestionValidated}}
                                  ?s ?p ?o
                                }}
                            """.format(graph_guid=triplestore_ingraph)

    validation_result = get_validation_result(triplestore_endpoint=triplestore_endpoint,
                                              graph=triplestore_ingraph,
                                              SPARQLquery=SPARQLquery)

    if not validation_result:
        return jsonify(request.get_json())

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
    # TODO: &quot; &apos;
    try:
        result['results']['bindings'][0]['a']['value'] = result['results']['bindings'][0]['a']['value'].replace("\"", "").replace("\'", "")
    except:
        print("BAD conversion")

    guid = str(uuid.uuid4())

    SPARQLquery = """
            PREFIX oa: <http://www.w3.org/ns/openannotation/core/>

            INSERT DATA 
            {{ 
                GRAPH <{graph_guid}>
                  {{ 
                    <urn:cqa:annotation:{guid}> oa:sparqlResult \"{sparql_result}\"^^<http://www.w3.org/2001/XMLSchema#string>
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
