import requests
from resources import constants

def annotate_text(params):
    response = requests.get(url="https://api.dbpedia-spotlight.org/en/annotate",
                            params=params,
                            headers={'accept': 'application/json'}).json()

    entities_dict = dict()

    if 'Resources' in response:
        for resource in response['Resources']:
            if len(resource['@types']) > 0 and "Disease" not in resource["@types"]:
                entities_dict[resource["@URI"]] = resource['@types']

    return entities_dict
