import random
import string
from resources.constants import TEMPLATES


def generate_answer(intents_dict, intent, sparql_result, annotation_dict):
    if "results" in sparql_result.keys() and len(list(sparql_result["results"]["bindings"][0].keys())) > 0:
        if intent == "distance":
            dist = sparql_result["results"]["bindings"][0]["distanceBetweenCities"]["value"]
            template = prepare_template(intents_dict, intent, dist, annotation_dict)

            return template
        else:
            labels_list = list()
            for binding in sparql_result["results"]["bindings"]:
                if "aLabel" in binding and len(binding["aLabel"]) > 0:
                    labels_list.append(binding["aLabel"]["value"])

            if len(labels_list) > 0:
                result = random.choice(labels_list)
                template = prepare_template(intents_dict, intent, result, annotation_dict)

                return template

            result = random.choice(sparql_result["results"]["bindings"])["a"]["value"]
            template = prepare_template(intents_dict, intent, result, annotation_dict)

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


def prepare_template(intents_dict, intent, result, annotation_dict):
    template = random.choice(intents_dict[intent][TEMPLATES])
    # check what arguments we have in string
    arguments = [arg[1] for arg in string.Formatter().parse(template) if arg[1] is not None]
    # if we have original one - we pass annotation parameters
    if 'original' not in arguments:
        template = template.format(result=result)
    else:
        #if intent is a distance - concat two places into one string
        if intent == "distance":
            original = annotation_dict[list(annotation_dict.keys())[0]]['@surfaceForm'] + " and " + \
                       annotation_dict[list(annotation_dict.keys())[1]]['@surfaceForm']
        else:
            original = annotation_dict[list(annotation_dict.keys())[0]]['@surfaceForm']

        template = template.format(result=result, original=original)

    return template
