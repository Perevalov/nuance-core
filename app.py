from flask import Flask, render_template, request, flash, session, url_for, redirect, make_response
from datetime import timedelta, datetime
from managers.DialogueManager import DialogueManager
from nlu.classifiers.KeywordClassifier import  KeywordClassifier
from resources import constants
from flask_cors import CORS
import json
from SPARQLWrapper import SPARQLWrapper, JSON

app = Flask(__name__)
CORS(app)
app.secret_key = str(datetime.now().time())

classifier = KeywordClassifier(constants.CLASSES)
dialogue_manager = DialogueManager(classifier=classifier)

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
