"""
Different questions require different database search queries for retrieving their answer.
Depending on the type of question we are dealing with, the template_classifier component
determines which query template should be used and stores the result as oa:templateType into the question's subgraph
"""

from flask import Blueprint, jsonify, request
import pickle
import os
import sys

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


def tell_me_more_classifier(question_text):
    """
    Rule based method for TELL_ME_MORE intent classification
    :param question_text: user's text
    :return: boolean value
    """
    return "tell me more" in question_text.lower()


@template_classifier_component.route("/annotatequestion", methods=['POST'])
def qanaryService():
    """the POST endpoint required for a Qanary service"""
    
    triplestore_endpoint = request.json["values"]["urn:qanary#endpoint"]
    triplestore_ingraph  = request.json["values"]["urn:qanary#inGraph"]
    triplestore_outgraph = request.json["values"]["urn:qanary#outGraph"]

    text = get_text_question_in_graph(triplestore_endpoint=triplestore_endpoint, graph=triplestore_ingraph)[0]['text']

    # TODO: this is temporary solution
    values = text.split('$')
    text = values[0]
    session_id = values[1]

    #dialogue_state = get_dialogue_state(triplestore_endpoint, session_id)

    print("Question Text: {0}".format(text))

    is_tell_me_more = tell_me_more_classifier(text)

    if is_tell_me_more:
        template_prediction = TELL_ME_MORE_TEMPLATE
        is_confident = True
    else:
        preprocessed_text = preprocess_text(text, remove_stopwords=False)
        print("Preprocessed text: {0}".format(preprocessed_text))
        template_prediction, is_confident = template_classifier.predict(preprocessed_text)

        if template_prediction == 'FWD_BWD':
            template_prediction, is_confident = fwd_bwd_classifier.predict(preprocessed_text)
        template_prediction = template_prediction[0]

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
    """.format(graph_guid=triplestore_ingraph, guid=guid, template_type=template_prediction, is_confident=is_confident)

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
