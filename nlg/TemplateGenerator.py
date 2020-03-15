import random
import string
from resources.constants import TEMPLATES, TELL_ME_MORE_TEMPLATE, WHAT_I_SEE_INTENT


def generate_answer(intents_dict, intent, sparql_result, annotation_dict):
    """

    :param intents_dict: dictionary filled with intent classes with their corresponding:
                            - answer_templates
                            -
    :param intent:
    :param sparql_result:
    :param annotation_dict:
    :return:
    """
    if intent == WHAT_I_SEE_INTENT:
        names = list()

        for node in annotation_dict.nodes:
            if "name" in node.tags.keys():
                names.append(node.tags["name"])

        if len(names) > 1:
            answer = "There are " + ', '.join(name for name in names) + " around you."
        elif len(names) == 1:
            answer = "There is " + ', '.join(name for name in names) + " around you."
        else:
            answer = "I don't see anything around you, sorry"

        return answer, "http://example.come/None"

    if "results" in sparql_result.keys() and len(list(sparql_result["results"]["bindings"])) > 0:
        if intent == "distance":
            dist = sparql_result["results"]["bindings"][0]["distanceBetweenCities"]["value"]
            template = prepare_template(intents_dict, intent, dist, annotation_dict)

            return template, "http://example.come/None"
        elif intent == TELL_ME_MORE_TEMPLATE:
            if len(sparql_result["results"]["bindings"]) == 0:
                return "Sorry, I don't know any other information", "http://example.come/None"

            for binding in sparql_result["results"]["bindings"]:
                template = binding["a"]["value"]
                return template.split('.')[0], "http://example.come/None"
        else:
            labels_list = list()
            for binding in sparql_result["results"]["bindings"]:
                if "aLabel" in binding and len(binding["aLabel"]) > 0:
                    labels_list.append((binding["aLabel"]["value"], binding["a"]["value"]))

            if len(labels_list) > 0:
                result = random.choice(labels_list)
                label = result[0]
                uri = result[1]

                template = prepare_template(intents_dict, intent, label, annotation_dict)

                return template, uri

            uri = random.choice(sparql_result["results"]["bindings"])["a"]["value"]
            template = prepare_template(intents_dict, intent, uri, annotation_dict)

            return template, uri

    elif "boolean" in sparql_result.keys():
        res = sparql_result["boolean"]
        if res:
            template = "Yes, it is true."
        else:
            template = "No, that is false"
        return template, "http://example.come/None"

    else:
        return "Sorry, there is not enough information in my database", "http://example.come/None"


def prepare_template(intents_dict, intent, result, annotation_dict):
    template = random.choice(intents_dict[intent][TEMPLATES])
    # check what arguments we have in string
    arguments = [arg[1] for arg in string.Formatter().parse(template) if arg[1] is not None]
    # if we have original one - we pass annotation parameters
    if 'original' not in arguments:
        template = template.format(result=result)
    else:
        # if intent is a distance - insert two places into one string
        if intent == "distance":
            original = annotation_dict[list(annotation_dict.keys())[0]]['@surfaceForm'] + " and " + \
                       annotation_dict[list(annotation_dict.keys())[1]]['@surfaceForm']
        else:
            original = annotation_dict[list(annotation_dict.keys())[0]]['@surfaceForm']

        template = template.format(result=result, original=original)

    return template
