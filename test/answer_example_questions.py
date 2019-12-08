"""
This little program outputs a set of example questions along with their generated answers
"""
import os
import json

from app import app
import config
from managers.DialogueManager import DialogueManager


def answer_example_questions():
    with open(os.path.join(config.TEST_PATH, "example_questions.json")) as json_file:
        example_questions = json.load(json_file)
    with app.test_client() as client:
        for question in example_questions:
            data = {"user_text": question}
            print(client.get("/get_answer", data=data))


if __name__ == "__main__":
    answer_example_questions()
