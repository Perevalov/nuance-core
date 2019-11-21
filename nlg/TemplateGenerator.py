import random
from resources.constants import TEMPLATES


def generate_answer(intents_dict, intent, sparql_result):
    #TODO receive annotation parameters and customize responses

    if "results" in sparql_result.keys() and len(list(sparql_result["results"]["bindings"][0].keys())) > 0:
        if intent == "distance":
            dist = sparql_result["results"]["bindings"][0]["distanceBetweenCities"]["value"]
            template = "The distance between these cities is {0} km".format(dist)
            return template
        else:
            labels_list = list()
            for binding in sparql_result["results"]["bindings"]:
                if "aLabel" in binding and len(binding["aLabel"]) > 0:
                    labels_list.append(binding["aLabel"]["value"])

            if len(labels_list) > 0:
                result = random.choice(labels_list)
                template = random.choice(intents_dict[intent][TEMPLATES]).format(result=result)

                return template

            result = random.choice(sparql_result["results"]["bindings"])["a"]["value"]
            template = random.choice(intents_dict[intent][TEMPLATES]).format(result=result)

            return template

    elif "boolean" in sparql_result.keys():
        if intent == "was_born":
            res = sparql_result["boolean"]
            if res:
                template = "Yes, it is true."
            else:
                template = "No, that is false"
            return template

    else:
        return "Sorry, there is not enough information in my database"
