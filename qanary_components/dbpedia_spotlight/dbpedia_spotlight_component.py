from flask import Blueprint, Flask, render_template, jsonify, request
import sys
import uuid

sys.path.insert(1, '../../')

from resources.qanary_helpers import *
import config
from nlu.ner import DBPediaSpotlightNER as ner
from resources.constants import *
from resources.utils import preprocess_text, map_template_and_relation_to_intent

dbpedia_spotlight_component = Blueprint('dbpedia_spotlight_component', __name__, template_folder='templates')

@dbpedia_spotlight_component.route("/annotatequestion", methods=['POST'])
def qanaryService():
    """the POST endpoint required for a Qanary service"""
    
    triplestore_endpoint = request.json["values"]["urn:qanary#endpoint"]
    triplestore_ingraph  = request.json["values"]["urn:qanary#inGraph"]
    triplestore_outgraph = request.json["values"]["urn:qanary#outGraph"]

    text = get_text_question_in_graph(triplestore_endpoint=triplestore_endpoint, graph=triplestore_ingraph)[0]['text']
    print("Question Text: {0}".format(text))
    preprocessed_text = preprocess_text(text)
    print("Preprocessed text: {0}".format(preprocessed_text))

    annotation_dict = ner.annotate_text({"text": preprocessed_text, "confidence": 0.3})

    guid = str(uuid.uuid4())

    SPARQLquery = """
                PREFIX oa: <http://www.w3.org/ns/openannotation/core/>

                INSERT DATA 
                {{ 
                    GRAPH <{graph_guid}>
                      {{ 
                        <urn:cqa:annotation:{guid}> oa:spotlightAnnotation \"{annotation}\" . 
                      }}
                }}
            """.format(graph_guid=triplestore_ingraph, guid=guid, annotation=annotation_dict)

    insert_into_triplestore(triplestore_endpoint, triplestore_ingraph, SPARQLquery)

    print(triplestore_ingraph)
    print("endpoint: %s, ingraph: %s, outGraph: %s" % (triplestore_endpoint, triplestore_ingraph, triplestore_outgraph))

    return jsonify(request.get_json())

@dbpedia_spotlight_component.route("/", methods=['GET'])
def index():
    """an examplary GET endpoint returning "hello world2 (String)"""
    print(request.host_url)
    return "Hello, World!"


@dbpedia_spotlight_component.route("/", methods=['POST'])
def indexJson():
    """a POST endpoint returning a hello world JSON"""
    data = {'Hello': 'World'}
    return jsonify(data)
