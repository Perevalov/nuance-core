import requests
from resources import constants

def annotate_text(params):
    response = requests.get(url="https://api.dbpedia-spotlight.org/en/annotate",
                            params=params,
                            headers={'accept': 'application/json'}).json()

    entities_dict = dict()

    for resource in response['Resources']:
        if len(resource['@types']) > 0:
            entities_dict[resource["@URI"]] = resource['@types']

    return entities_dict
