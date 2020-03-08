import json
import os
import config
from string import Formatter
from resources.qanary_helpers import *

def evaluate_components(queries, annotation):
    for question in annotation:
        question_text = question["question"]

        response = requests.post(url="http://localhost:8080/startquestionansweringwithtextquestion",
                                 params={
                                     "question": question_text,
                                     "componentlist[]": ["template_classifier",
                                                         "relation_classifier",
                                                         "dbpedia_spotlight_annotator",
                                                         "question_validator",
                                                         "sparql_builder",
                                                         "dbpedia_sparql_worker",
                                                         "template_generator"]
                                 }).json()

        endpoint = response['endpoint']
        in_graph = response['inGraph']

        query_header = None
        graph = in_graph

        for key in list(queries.keys()):
            if key != "query_header":
                SPARQLquery = query_header + queries[key]

                field_names = [fname for _, fname, _, _ in Formatter().parse(SPARQLquery) if fname]
                question_annotation = question[key]
                question_annotation["graph_urn"] = graph

                data_dict = dict()
                for name in field_names:
                    data_dict[name] = question_annotation[name]

                SPARQLquery = SPARQLquery.format(**data_dict)
                
                result = queryTriplestore(endpoint + "/query", graph, SPARQLquery)
                print("Q:{0}, C:{1}, R:{2}".format(question_text, key, result['boolean']))
            else:
                query_header = queries[key]


if __name__ == "__main__":
    with open(os.path.join("", "sparql_queries.json")) as json_file:
        queries = json.load(json_file)

    with open(os.path.join("", "questions_annotation.json")) as json_file:
        annotation = json.load(json_file)

    evaluate_components(queries, annotation)