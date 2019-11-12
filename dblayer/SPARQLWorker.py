import requests


def execute_query(params):
    response = requests.post(url="http://dbpedia.org/sparql",
                            params=params,
                            headers={'accept': 'application/sparql-results+json'}).json()

    return response
