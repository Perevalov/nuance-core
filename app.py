from flask import Flask, render_template, request, flash, session, url_for, redirect, make_response
import json
from passlib.hash import sha256_crypt
from datetime import timedelta, datetime
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
import spacy

nlp = spacy.load("en_core_web_sm")
app = Flask(__name__)
app.secret_key = str(datetime.now().time())


def get_cities_for_a_text(text):
    doc = nlp(text)

    cities = list()
    for ent in doc.ents:
        if ent.label_ == 'GPE':
            cities.append(ent.text)

    return cities


@app.route("/get_answer", methods=['GET'])
def get_answer():
    print("get_answer Started")
    question_text = request.form.get("question_text")
    supported_question_prefix = "How many people live in "
    cities = get_cities_for_a_text(question_text)
    results: json

    # TODO the following if statement shall be replaced with a more sophisticated question answering algorithm
    if question_text.lower().strip().startswith(supported_question_prefix.lower()) and len(cities) > 0:

        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        sparql.setQuery("""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX yago: <http://dbpedia.org/class/yago/>
            SELECT DISTINCT ?cityLabel ?numberOfInhabitants
            WHERE {
                    VALUES ?placeType { dbo:City yago:City108524735 }
                    ?s rdf:type ?placeType .
                    ?s rdfs:label ?cityLabel .
                    filter(contains(lcase(?cityLabel),"%s")) .
                    filter(LANG(?cityLabel) = "en") .
                    ?s dbo:populationTotal ?numberOfInhabitants .  
            }
            ORDER BY DESC (?numberOfInhabitants)
            LIMIT 100
        """ % (cities[0].lower()))  # only searches for the very first city mentioned

        sparql.setReturnFormat(JSON)
        results = json.dump(sparql.query().convert())

    else:
        # TODO: improve error handling for unsupported questions (if they exist)
        results = json.dump(
            {'Question \"%s\" is not supported.' % question_text:
                'Only questions starting with the phrase \"%s\" and containing a city name might be evaluated.'
                    % supported_question_prefix}
        )

    print("get_answer Ended")
    return results


if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=6000)
