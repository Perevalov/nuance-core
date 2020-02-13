import os
import subprocess

process = subprocess.Popen("python -m spacy download en".split(), stdout=subprocess.PIPE)
output, error = process.communicate()

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

INTENTS_PATH = os.path.join(PROJECT_PATH, "intents")

TEST_PATH = os.path.join(PROJECT_PATH, "test")

DB_PATH = os.path.join(PROJECT_PATH, "cerence-db")
