from resources.constants import PARAMETER_NUM, QUERY, QUERY_TYPE, QUERY_HEAD, QUERY_BODY, QUERY_CLOSURE, PREDICATES,\
    FALLBACK_CLASS, PREFIXES, QUERY_VALUES


def generate_label_query(result: str):
    return """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?aLabel WHERE {{ <{0}> rdfs:label ?alabel}}
    """.format(result)


class SPARQLBuilder:

    def __init__(self, sparql_templates):
        self.sparql_templates = sparql_templates

    def generate_sparql(self, query_type: str, entities: list, relations: list):
        """
        :param query_type: must be one of the supported query types in sparql_templates
        :param entities:
        :param relations:
        :return: assembles and returns a SPARQL query string that's ready for execution
        """

        head = self.sparql_templates[PREFIXES]
        head += self.sparql_templates[query_type][QUERY][QUERY_HEAD]

        body = ''
        if query_type == "forward" or query_type == "backward":
            # This will produce an optional statement for each of the given relations
            values = ' '.join("<{0}>".format(relation) for relation in relations)
            body += self.sparql_templates[query_type][QUERY][QUERY_VALUES].format(values=values)
            body += self.sparql_templates[query_type][QUERY][QUERY_BODY].format(entity=entities[0])

        elif query_type == "distance":
            body = self.sparql_templates[query_type][QUERY][QUERY_BODY].format(point_1=entities[0], point_2=entities[1])

        elif query_type == "boolean":
            values = ' '.join("<{0}>".format(relation) for relation in relations)
            body += self.sparql_templates[query_type][QUERY][QUERY_VALUES].format(values=values)
            body = self.sparql_templates[query_type][QUERY][QUERY_BODY].format(entity_1=entities[0],
                                                                               entity_2=entities[1])
        elif query_type == "abstract":
            body = self.sparql_templates[query_type][QUERY][QUERY_BODY].format(entity=entities[0])

        else:
            raise QueryTypeError('The passed argument "'+query_type+'" is not a supported query_class')

        closure = self.sparql_templates[query_type][QUERY][QUERY_CLOSURE]   # just in case a query doesn't end with "}" alone

        result = head + body + closure
        return result


class QueryTypeError(ValueError):
    def __init__(self, message: str):
        super().__init__(message)
