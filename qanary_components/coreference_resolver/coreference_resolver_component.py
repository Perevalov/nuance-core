import sys

from flask import Blueprint, jsonify, request

sys.path.insert(1, '../../')

from resources.qanary_helpers import *
from nlu.ner import coreference_resolver as coref
from resources.utils import preprocess_text, find_best_string_match

coreference_resolver_component = Blueprint('coreference_resolver_component', __name__, template_folder='templates')


@coreference_resolver_component.route("/annotatequestion", methods=['POST'])
def qanaryService():
    """the POST endpoint required for a Qanary service"""

    triplestore_endpoint = request.json["values"]["urn:qanary#endpoint"]
    triplestore_ingraph = request.json["values"]["urn:qanary#inGraph"]
    triplestore_outgraph = request.json["values"]["urn:qanary#outGraph"]

    text = get_text_question_in_graph(triplestore_endpoint=triplestore_endpoint, graph=triplestore_ingraph)[0]['text']
    # TODO: this is temporary solution
    values = text.split('$')
    text = values[0]
    session_id = values[1]

    print("Question Text: {0}".format(text))
    preprocessed_text = preprocess_text(text, remove_stopwords=True, lowercase=False)
    print("Preprocessed text: {0}".format(preprocessed_text))

    has_coref = coref.has_coref(text)

    if has_coref:
        qa_pair_id = get_most_recent_qa_pair(triplestore_endpoint, session_id)
        qa_pair = get_qa_text_from_graph(triplestore_endpoint, qa_pair_id)

        # if another question has previously been asked
        if qa_pair:
            # only examine it at first
            question_1 = qa_pair["question_text"]
            answer = qa_pair["answer_text"]
            question_2 = text

            result = coref.get_coreferent_label(question_1, question_2, answer)

            if result:
                # TODO: decide which annotation should we retrieve (answer or question)
                if result['index'] == 0:  # that means we search for question's annotation
                    annotation, intent = get_annotation_and_intent(triplestore_endpoint, qa_pair_id)
                    label = result['label']
                    # TODO: fuzzy search for entity in annotation dict (if found - put it to annotation)
                    list_of_labels = [annotation[key]['@surfaceForm'] for key in list(annotation.keys())]
                    idx, ratio = find_best_string_match(list_of_labels, label)
                    uri = list(annotation.keys())[idx]

                    insert_coreference_uri(uri, ratio > 75, triplestore_ingraph, triplestore_endpoint)

                else:
                    annotation = get_answer_uri(triplestore_endpoint, qa_pair_id)
                    insert_coreference_uri(annotation, True, triplestore_ingraph, triplestore_endpoint)

    print(triplestore_ingraph)
    print("endpoint: %s, ingraph: %s, outGraph: %s" % (triplestore_endpoint, triplestore_ingraph, triplestore_outgraph))

    return jsonify(request.get_json())


@coreference_resolver_component.route("/", methods=['GET'])
def index():
    """an examplary GET endpoint returning "hello world2 (String)"""
    print(request.host_url)
    return "Hello, World!"


@coreference_resolver_component.route("/", methods=['POST'])
def indexJson():
    """a POST endpoint returning a hello world JSON"""
    data = {'Hello': 'World'}
    return jsonify(data)
