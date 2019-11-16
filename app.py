from flask import Flask, render_template, request
from datetime import datetime
from managers.DialogueManager import DialogueManager
from nlu.classifiers.KeywordClassifier import KeywordClassifier
from flask_cors import CORS
import config
import os
import json

app = Flask(__name__)
CORS(app)
app.secret_key = str(datetime.now().time())

with open(os.path.join(config.INTENTS_PATH, "intents.json")) as json_file:
    intents = json.load(json_file)

with open(os.path.join(config.INTENTS_PATH, 'sparql_templates.json')) as json_file:
    sparql = json.load(json_file)

classifier = KeywordClassifier(intents)
dialogue_manager = DialogueManager(classifier=classifier, intents=intents, sparql=sparql)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_answer", methods=['GET'])
def get_answer():
    print("get_answer Started")
    question_text = request.args.get("user_text")

    answer_text = dialogue_manager.get_answer(question_text)

    response_array = list()

    return json.dumps({"system_text": answer_text})


if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5001)
