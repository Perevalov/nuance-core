# DBpedia Spotlight NED Qanary component
The component solves named entity disambiguation task.

Given a following question:

Where was **Barack Obama** born?

We have to extract **Barack Obama** (NER) and link in to http://dbpedia.org/page/Barack_Obama (NEL).

## Required data input

* Question text (string).

## Produced data (output)

* Found entities and links to it (dictionary).

## Typical use within a QA pipeline
1. Template Classifier;
1. Relation Classifier;
1. **Dbpedia Spotlight NED**;
1. Coreference Resolver;
1. Question Validator;
1. SPARQL Builder;
1. DBpedia SPARQL Worker;
1. Template Generator.

## Libraries/approaches used for the implementation

* DBpedia Spotlight API (https://www.dbpedia-spotlight.org/api).
