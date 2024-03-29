import logging
from SPARQLWrapper import SPARQLWrapper, JSON
import requests
from urllib.parse import urlparse
from pprint import pprint
import re
import uuid


def get_text_question_in_graph(triplestore_endpoint, graph):
    """
        retrieves the questions from the triplestore returns an array
    """
    questions = []
    query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT (?s AS ?questionURI) (URI(CONCAT(STR(?s),"/raw")) AS ?questionURIraw)
        FROM <%s> 
        WHERE {
            ?s ?p ?o . 
            ?s rdf:type <http://www.wdaqua.eu/qa#Question> .
        }
    """ % graph
    results = selectFromTriplestore(triplestore_endpoint, graph, query)
    for result in results["results"]["bindings"]:
        logging.info("found: questionURI=%s  questionURIraw=%s" % (result['questionURI']['value'], result['questionURIraw']['value']) )
        questionText = requests.get(result['questionURIraw']['value'])
        logging.info("found question: \""+questionText.text+"\"")
        questions.append({"uri": result['questionURI']['value'], "text": questionText.text})
    
    pprint(questions)
    return questions


def getComputedSparqlQueryAsAnswer(triplestore_endpoint, graph):
    """
        retrieves the SPARQL query from the triplestore that should be executed to get the answer from the knowledge graph
    """
    query = """
        PREFIX oa: <http://www.w3.org/ns/openannotation/core/>
        PREFIX qa: <http://www.wdaqua.eu/qa#> 
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT *
        FROM <%s> 
        WHERE {
            ?s ?p ?o . 
            ?s rdf:type qa:AnnotationOfAnswerSPARQL .
        }
    """ % graph 
    results = selectFromTriplestore(triplestore_endpoint, graph, query)
    #for result in results["results"]["bindings"]:
        #logging.info("found triple: %s %s %s " % (result['s']['value'], result['p']['value'], result['o']['value']) )
    
    return results


def getTextSelectors(triplestore_endpoint, graph):
    query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT * 
        FROM <%s>
        WHERE {
            ?annotation rdf:type <http://www.wdaqua.eu/qa#AnnotationOfInstance>.
            ?annotation ?p ?o 

            OPTIONAL {
                ?o ?p2 ?o2
                OPTIONAL {
                    ?o2 ?p3 ?o3
                }
            }
        }
    """ % graph
    results = selectFromTriplestore(triplestore_endpoint, graph, query)
    return results

def selectFromTriplestore(triplestore_endpoint, graph, SPARQLquery):
    """
        execute SELECT query on triplestore and returns the result object
    """ 
    # required for Stardog
    return queryTriplestore(triplestore_endpoint+"/query", graph, SPARQLquery)


def get_dialogue_state(triplestore_endpoint, session_id):
    SPARQLquery = """
               PREFIX oa: <http://www.w3.org/ns/openannotation/core/>

               SELECT *
               WHERE 
               {{ 
                   <urn:cqa:dialogue:{session_id}> oa:hasQuestion ?question
               }}
           """.format(session_id=session_id)

    result = queryTriplestore(triplestore_endpoint + "/query", None, SPARQLquery)
    #TODO: do something with it
    return -1

def insert_into_triplestore(triplestore_endpoint, graph, SPARQLquery):
    """
        execute INSERT query on triplestore and returns the result object
    """ 
    # required for Stardog
    return queryTriplestore(triplestore_endpoint+"/update", graph, SPARQLquery)


def constructIntoTriplestore(triplestore_endpoint, graph, SPARQLquery):
    """
        execute CONSTRUCT query on triplestore and returns the result object
    """ 
    # redirect: required for Stardog
    return insertIntoTriplestore(triplestore_endpoint, graph, SPARQLquery)


def get_most_recent_qa_pair(triplestore_endpoint, session_id):
    SPARQLquery = """
            PREFIX oa: <http://www.w3.org/ns/openannotation/core/>

            SELECT ?graphGuid
            WHERE 
            {{
                <urn:cqa:dialogue:{session_id}> oa:hasQuestion ?graphGuid ;
                    oa:hasTimeAnswered ?time .
            }}
            ORDER BY DESC(?time)
            LIMIT 1
        """.format(session_id=session_id)

    graph_guid = None
    result = queryTriplestore(triplestore_endpoint + "/query", None, SPARQLquery)
    for binding in result['results']['bindings']:
        graph_guid = binding['graphGuid']['value']

    return graph_guid


def get_coreference_uri(triplestore_endpoint, graph):
    SPARQLquery = """
                           PREFIX oa: <http://www.w3.org/ns/openannotation/core/>

                           SELECT ?p ?o
                           FROM <{graph_guid}>
                           WHERE 
                           {{
                             VALUES ?p {{oa:coreferenceURI}}
                             ?s ?p ?o
                           }}
                       """.format(graph_guid=graph)

    uri = None

    result = queryTriplestore(triplestore_endpoint + "/query", graph, SPARQLquery)
    for binding in result['results']['bindings']:
        if 'coreferenceURI' in binding['p']['value']:
            uri = binding['o']['value']

    return {uri: ''}


def insert_coreference_uri(uri, is_confident, graph, triplestore_endpoint):
    guid = str(uuid.uuid4())

    SPARQLquery = """
                    PREFIX oa: <http://www.w3.org/ns/openannotation/core/>

                    INSERT DATA 
                    {{ 
                        GRAPH <{graph_guid}>
                          {{ 
                            <urn:cqa:annotation:{guid}> oa:coreferenceURI <{uri}> .
                            <urn:cqa:annotation:{guid}> oa:isCoreferenceConfident \"{is_confident}\" .
                          }}
                    }}
                """.format(graph_guid=graph, guid=guid, uri=uri, is_confident=is_confident)

    insert_into_triplestore(triplestore_endpoint, graph, SPARQLquery)


def get_qa_text_from_graph(triplestore_endpoint, graph_guid):
    question_text = get_text_question_in_graph(triplestore_endpoint, graph_guid)[0]['text']
    # TODO: this is temporary solution
    question_text = question_text.split('$')[0]

    SPARQLquery = """
            PREFIX oa: <http://www.w3.org/ns/openannotation/core/>

            SELECT ?answerText
            FROM <{graph_guid}>
            WHERE 
            {{ 
              VALUES ?p {{oa:textResponse}}
              ?s ?p ?answerText
            }}
        """.format(graph_guid=graph_guid)

    answer_text = None
    result = queryTriplestore(triplestore_endpoint + "/query", graph_guid, SPARQLquery)

    for binding in result['results']['bindings']:
        answer_text = binding['answerText']['value']

    return {'question_text': question_text, "answer_text": answer_text}


def get_answer_uri(triplestore_endpoint, graph):
    SPARQLquery = """
            PREFIX oa: <http://www.w3.org/ns/openannotation/core/>

            SELECT ?uri
            FROM <{graph_guid}>
            WHERE 
            {{ 
              VALUES ?p {{oa:uriResponse}}
              ?s ?p ?uri
            }}
        """.format(graph_guid=graph)

    uri = None
    result = queryTriplestore(triplestore_endpoint + "/query", graph, SPARQLquery)

    for binding in result['results']['bindings']:
        uri = binding['uri']['value']

    return uri


def get_annotation_and_intent(triplestore_endpoint, graph):
    import ast

    SPARQLquery = """
                        PREFIX oa: <http://www.w3.org/ns/openannotation/core/>

                        SELECT ?p ?o
                        FROM <{graph_guid}>
                        WHERE 
                        {{
                          VALUES ?p {{oa:namedEntities oa:intent}}
                          ?s ?p ?o
                        }}
                    """.format(graph_guid=graph)

    annotation = "{}"
    intent = None

    result = queryTriplestore(triplestore_endpoint + "/query", graph, SPARQLquery)
    for binding in result['results']['bindings']:
        if 'namedEntities' in binding['p']['value']:
            annotation = binding['o']['value']
        elif 'intent' in binding['p']['value']:
            intent = binding['o']['value'].replace("http://www.w3.org/ns/openannotation/core/intent:", "")

    return ast.literal_eval(annotation), intent


def get_sparql(triplestore_endpoint, graph, SPARQLquery):

    sparql = None

    result = queryTriplestore(triplestore_endpoint + "/query", graph, SPARQLquery)
    for binding in result['results']['bindings']:
        if 'sparqlQuery' in binding['p']['value']:
            sparql = binding['o']['value']

    return sparql


def get_text_response(triplestore_endpoint, graph, SPARQLquery):

    text_response = None

    result = queryTriplestore(triplestore_endpoint + "/query", graph, SPARQLquery)
    for binding in result['results']['bindings']:
        if 'textResponse' in binding['p']['value']:
            text_response = binding['o']['value']

    return text_response


def get_validation_result(triplestore_endpoint, graph, SPARQLquery):
    validation_result = None

    result = queryTriplestore(triplestore_endpoint + "/query", graph, SPARQLquery)
    for binding in result['results']['bindings']:
        if 'isQuestionValidated' in binding['p']['value']:
            validation_result = binding['o']['value'].replace("http://www.w3.org/ns/openannotation/core/boolean:", "")
            if validation_result == 'True':
                validation_result = True
            elif validation_result == 'False':
                validation_result = False

    return validation_result


def get_sparql_result(triplestore_endpoint, graph, SPARQLquery):
    import ast
    sparql_result = None

    result = queryTriplestore(triplestore_endpoint + "/query", graph, SPARQLquery)
    for binding in result['results']['bindings']:
        if 'sparqlResult' in binding['p']['value']:
            sparql_result = binding['o']['value']

    return ast.literal_eval(sparql_result)


def get_template_prediction(triplestore_endpoint, graph, SPARQLquery):

    template_prediction = None
    is_confident = None

    result = queryTriplestore(triplestore_endpoint + "/query", graph, SPARQLquery)
    for binding in result['results']['bindings']:
        if 'templateType' in binding['p']['value']:
            template_prediction = binding['o']['value'].replace("http://www.w3.org/ns/openannotation/core/templateType:", "")
        elif 'isTemplateClassifierConfident' in binding['p']['value']:
            if 'True' in binding['o']['value']:
                is_confident = True
            else:
                is_confident = False

    return template_prediction, is_confident

def queryTriplestore(triplestore_endpoint, graph, SPARQLquery):
    """
        execute query on the triplestore and returns the result object
    """
    triplestore_endpoint_parsed=urlparse(triplestore_endpoint)
    triplestore_endpoint_parsed_split=re.split("^(\w+):(\w+)@(.*)$", triplestore_endpoint_parsed.netloc)
    username = triplestore_endpoint_parsed_split[1]
    password = triplestore_endpoint_parsed_split[2]
    triplestore_endpoint_new=triplestore_endpoint_parsed.scheme+"://"+triplestore_endpoint_parsed_split[3]+triplestore_endpoint_parsed.path
    logging.info("found: endpoint=%s,  username=%s,  password=%s" % (triplestore_endpoint_new, username, password))
    logging.info("execute SPARQL query:\n%s" % SPARQLquery)
    sparql = SPARQLWrapper(triplestore_endpoint_new)
    sparql.setCredentials(username, password)
    sparql.setQuery(SPARQLquery);
    sparql.setReturnFormat(JSON)
    sparql.setMethod("POST")
    results = sparql.query().convert()
    logging.debug(results)
    return results


"""@myservice.route("/annotatequestion", methods=['POST'])
def qanaryService():

    triplestore_endpoint = request.json["values"]["urn:qanary#endpoint"]
    triplestore_ingraph = request.json["values"]["urn:qanary#inGraph"]
    triplestore_outgraph = request.json["values"]["urn:qanary#outGraph"]

    logging.info("endpoint: %s, ingraph: %s, outGraph: %s" % (triplestore_endpoint, triplestore_ingraph, triplestore_outgraph))

    print("\n")
    print("\n")
    print(request.get_json())
    print("\n")
    print("\n")


    # use this if you want to get the textual input of the user (i.e., the question)
    questions = getTextQuestionInGraph( triplestore_endpoint=triplestore_endpoint, graph=triplestore_ingraph )
    pprint("found questions (actually there should only be one) in current graph: %s" % triplestore_ingraph)
    pprint(questions )

    # use this if you want to retrieve the SPARQL query that might be generated by a QueryBuilder component
    results = getComputedSparqlQueryAsAnswer( triplestore_endpoint=triplestore_endpoint, graph=triplestore_ingraph )
    pprint("results of getComputedSparqlQueryAsAnswer in current graph: %s" % triplestore_ingraph)
    pprint(results)

    # use this if you want to get the markers in a text (e.g., from DBpedia Spotlight)
    results = getTextSelectors( triplestore_endpoint=triplestore_endpoint, graph=triplestore_ingraph )
    pprint("results of getTextQuestionInGraph in current graph: %s" % triplestore_ingraph)
    pprint(results)


    return jsonify(request.get_json())"""

