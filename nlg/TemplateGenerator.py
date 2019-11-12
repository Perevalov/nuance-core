
def generate_answer(q_class, sparql_result):
    if "results" in sparql_result.keys() and len(sparql_result["results"]["bindings"]) > 0:
        if q_class == "distance":
            dist = sparql_result["results"]["bindings"][0]["distanceBetweenCities"]["value"]
            template = "The distance between these cities is {0} km".format(dist)
            return template
        if q_class == "temp-month":
            dist = sparql_result["results"]["bindings"][0]["tempMonth"]["value"]
            template = "The temperature equals {0} degrees".format(dist)
            return template
        if q_class == "city":
            amount = sparql_result["results"]["bindings"][0]["numberOfInhabitants"]["value"]
            template = "The amount of people living in this city is {0} ".format(amount)
            return template
    elif "boolean" in sparql_result.keys():
        if q_class == "was-born":
            res = sparql_result["boolean"]
            if res:
                template = "Yes, it is true."
            else:
                template = "No, that is false"
            return template

    else:
        return "Sorry, there is not enough information in my database"
