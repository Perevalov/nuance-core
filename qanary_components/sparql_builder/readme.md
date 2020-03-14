# SPARQL Builder Qanary component
The component compiles a SPARQL query to the Knowledge Base in order to retrieve an answer.

Given a following question text:

Name an elvis presley album

And outputs from Template-, Relation Classifier, DBpedia Spotlight NED, Question Validator

The component outputs a ready to run SPARQL query:

```
PREFIX dbr: <http://dbpedia.org/resource/>
PREFIX dbo: <http://dbpedia.org/ontology/>
SELECT ?album 
WHERE 
{
  ?album dbo:artist dbr:Elvis_Presley .
}
```


## Required data input

* Validation result (boolean);
* NED output (dictionary);
* Intent (string).

## Produced data (output)

* SPARQL query (string).

## Typical use within a QA pipeline
1. Template Classifier;
1. Relation Classifier;
1. Dbpedia Spotlight NED;
1. Coreference Resolver;
1. Question Validator;
1. **SPARQL Builder**;
1. DBpedia SPARQL Worker;
1. Template Generator.

## Libraries/approaches used for the implementation

* Basic Python libraries.
