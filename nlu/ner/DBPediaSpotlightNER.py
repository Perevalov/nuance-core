import requests
from resources import constants

def annotate_text(params):
    response = requests.get(url="https://api.dbpedia-spotlight.org/en/annotate",
                            params=params,
                            headers={'accept': 'application/json'}).json()

    entities_dict = dict()

    for res in response["Resources"]:
        if any(word.lower() in res["@types"].lower() for word in constants.PERSON_KEYWORDS):
            entities_dict[res["@URI"]] = "person"
        elif any(word.lower() in res["@types"].lower() for word in constants.CITY_KEYWORDS):
            entities_dict[res["@URI"]] = "city"
        elif any(word.lower() in res["@types"].lower() for word in constants.COUNTRY_KEYWORDS):
            entities_dict[res["@URI"]] = "country"
        elif any(word.lower() in res["@URI"].lower() for word in constants.MONTH_KEYWORDS):
            entities_dict[res["@URI"]] = "month"

    return entities_dict
