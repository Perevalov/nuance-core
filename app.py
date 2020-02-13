import nltk

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

from flask import Flask, render_template, request
from datetime import datetime
from managers.DialogueManager import DialogueManager
from nlu.classifiers.KeywordClassifier import KeywordClassifier
from resources.utils import init_ml_classifiers
from resources.qanary_helpers import *
from flask_cors import CORS
import config
import os
import json
import requests
import uuid
from time import gmtime, strftime


app = Flask(__name__)
CORS(app)
app.secret_key = str(datetime.now().time())

with open(os.path.join(config.INTENTS_PATH, "intents.json")) as json_file:
    intents = json.load(json_file)

with open(os.path.join(config.INTENTS_PATH, 'sparql_templates.json')) as json_file:
    sparql = json.load(json_file)

keyword_classifier = KeywordClassifier(intents)
template_classifier, fwd_bwd_classifier, relation_classifier = init_ml_classifiers()

dialogue_manager = DialogueManager(keyword_classifier=keyword_classifier,
                                   template_classifier=template_classifier,
                                   fwd_bwd_classifier=fwd_bwd_classifier,
                                   relation_classifier=relation_classifier,
                                   intents=intents,
                                   sparql_templates=sparql)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_answer", methods=['GET'])
def get_answer():
    print("[/get_answer] Started")
    session_id = request.args.get("session_id")

    if not session_id:
        session_id = str(uuid.uuid4())

    question_text = request.args.get("user_text")

    #TODO error message for when user_text is not a proper string
    print("Original question text: {0}".format(question_text))

    answer_text = dialogue_manager.get_answer(question_text, session_id)
    print("Answer text is: {0}".format(answer_text))


    print("[/get_answer] Ended")

    return json.dumps({"system_text": answer_text, "session_id": session_id})


@app.route("/get_answer_qanary", methods=['GET'])
def get_answer_qanary():
    session_id = request.args.get("session_id")

    if not session_id:
        session_id = str(uuid.uuid4())

    question_text = request.args.get("user_text")

    response = requests.post(url="http://localhost:8080/startquestionansweringwithtextquestion",
                            params={
                                # TODO: this is temporary solution
                                "question": question_text+"$"+session_id,
                                "componentlist[]": ["template_classifier",
                                                    "relation_classifier",
                                                    "dbpedia_spotlight_annotator",
                                                    "coreference_resolver",
                                                    "question_validator",
                                                    "sparql_builder",
                                                    "dbpedia_sparql_worker",
                                                    "template_generator"]
                            }).json()

    endpoint = response['endpoint']
    in_graph = response['inGraph']

    template_generator_endpoint = "http://127.0.0.1:5007/text_answer"

    response = requests.get(url=template_generator_endpoint,
                            params={
                                'endpoint': endpoint,
                                'inGraph': in_graph
                            }).json()

    answer_text = response['answer']

    #Save session_id, question and answer text to tripletstore
    SPARQLquery = """
               PREFIX oa: <http://www.w3.org/ns/openannotation/core/>

               INSERT DATA 
               {{ 
                   <urn:cqa:dialogue:{session_id}> oa:hasQuestion <{graph_guid}> .
                   <urn:cqa:dialogue:{session_id}> oa:hasTimeAnswered "{current_time}"^^xsd:dateTime
               }}
           """.format(session_id=session_id, graph_guid=in_graph, current_time=strftime("%Y-%m-%dT%H:%M:%S", gmtime()))

    insert_into_triplestore(endpoint, in_graph, SPARQLquery)


    return json.dumps({"system_text": answer_text, "session_id": session_id, "in_graph": in_graph})

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5050)
