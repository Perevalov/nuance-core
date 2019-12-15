from flask import Blueprint, Flask, render_template, jsonify, request
import pickle
import os
import sys
import uuid

sys.path.insert(1, '../../')

from resources.qanary_helpers import *
import config
from nlu.classifiers.MLClassifier import MLClassifier
from resources.constants import *
from resources.utils import preprocess_text

template_classifier_component = Blueprint('template_classifier_component', __name__, template_folder='templates')

#loading the model
template_vectorizer = pickle.load(open(os.path.join(config.PROJECT_PATH, "models", "template_vectorizer.model"), 'rb'))
template_encoder = pickle.load(open(os.path.join(config.PROJECT_PATH, "models", "template_encoder.model"), 'rb'))
template_classifier = pickle.load(open(os.path.join(config.PROJECT_PATH, "models", "template_classifier.model"), 'rb'))

template_classifier = MLClassifier(template_classifier, template_vectorizer, template_encoder)

#loading the model
fwd_bwd_vectorizer = pickle.load(open(os.path.join(config.PROJECT_PATH, "models", "fwd_bwd_vectorizer.model"), 'rb'))
fwd_bwd_encoder = pickle.load(open(os.path.join(config.PROJECT_PATH, "models", "fwd_bwd_encoder.model"), 'rb'))
fwd_bwd_classifier = pickle.load(open(os.path.join(config.PROJECT_PATH, "models", "fwd_bwd_classifier.model"), 'rb'))

fwd_bwd_classifier = MLClassifier(fwd_bwd_classifier, fwd_bwd_vectorizer, fwd_bwd_encoder)

@template_classifier_component.route("/annotatequestion", methods=['POST'])
def qanaryService():
    """the POST endpoint required for a Qanary service"""
    
    triplestore_endpoint = request.json["values"]["urn:qanary#endpoint"]
    triplestore_ingraph  = request.json["values"]["urn:qanary#inGraph"]
    triplestore_outgraph = request.json["values"]["urn:qanary#outGraph"]

    text = get_text_question_in_graph(triplestore_endpoint=triplestore_endpoint, graph=triplestore_ingraph)[0]['text']
    print("Question Text: {0}".format(text))
    preprocessed_text = preprocess_text(text, remove_stopwords=False)
    print("Preprocessed text: {0}".format(preprocessed_text))
    template_prediction, is_confident = template_classifier.predict(preprocessed_text)

    if template_prediction == 'FWD_BWD':
        template_prediction, is_confident = fwd_bwd_classifier.predict(preprocessed_text)

    guid = str(uuid.uuid4())

    SPARQLquery = """
        PREFIX oa: <http://www.w3.org/ns/openannotation/core/>
        
        INSERT DATA 
        {{ 
            GRAPH <{graph_guid}>
              {{ 
                <urn:cqa:annotation:{guid}> oa:templateType oa:templateType:{template_type} . 
                <urn:cqa:annotation:{guid}> oa:isTemplateClassifierConfident oa:boolean:{is_confident}
              }}
        }}
    """.format(graph_guid=triplestore_ingraph, guid=guid, template_type=template_prediction[0], is_confident=is_confident)

    insert_into_triplestore(triplestore_endpoint, triplestore_ingraph, SPARQLquery)

    print("endpoint: %s, ingraph: %s, outGraph: %s" % (triplestore_endpoint, triplestore_ingraph, triplestore_outgraph))

    return jsonify(request.get_json())

@template_classifier_component.route("/", methods=['GET'])
def index():
    """an examplary GET endpoint returning "hello world2 (String)"""
    print(request.host_url)
    return "Hello from template_classifier!"


@template_classifier_component.route("/", methods=['POST'])
def indexJson():
    """a POST endpoint returning a hello world JSON"""
    data = {'Hello': 'World'}
    return jsonify(data)
