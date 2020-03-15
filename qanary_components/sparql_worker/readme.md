# DBpedia SPARQL Worker Qanary component
The component executes a SPARQL query on a Knowledge Base endpoint and returns the response.

Given a following SPARQL query:

```
PREFIX dbr: <http://dbpedia.org/resource/>
PREFIX dbo: <http://dbpedia.org/ontology/>
SELECT ?album 
WHERE 
{
  ?album dbo:artist dbr:Elvis_Presley .
}
LIMIT 1
```

The component outputs a json response:

```
{
  "head": {
    "link": [],
    "vars": [
      "album"
    ]
  },
  "results": {
    "distinct": false,
    "ordered": true,
    "bindings": [
      {
        "album": {
          "type": "uri",
          "value": "http://dbpedia.org/resource/Today,_Tomorrow,_and_Forever_(Elvis_Presley_album)"
        }
      }
    ]
  }
}
```


## Required data input

* SPARQL query (string).

## Produced data (output)

* JSON response (string).

## Typical use within a QA pipeline
1. Template Classifier;
1. Relation Classifier;
1. Dbpedia Spotlight NED;
1. Coreference Resolver;
1. Question Validator;
1. SPARQL Builder;
1. **DBpedia SPARQL Worker**;
1. Template Generator.

## Libraries/approaches used for the implementation

* Basic Python libraries;
* DBpedia SPARQL endpoint https://dbpedia.org/sparql.
