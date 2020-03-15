# Relation Classifier Qanary component
The component classifies a relation (or predicate) which is intended in the question.

Given a following question text:

Who wrote **Bohemian Rhapsody** song?

The component outputs intened relation in the question, which is http://dbpedia.org/ontology/writer.

## Required data input

* Question text (string);
* Pre-trained model (binary).

## Produced data (output)

* Relation (predicate) (string).

## Typical use within a QA pipeline
1. Template Classifier;
1. **Relation Classifier**;
1. Dbpedia Spotlight NED;
1. Coreference Resolver;
1. Question Validator;
1. SPARQL Builder;
1. DBpedia SPARQL Worker;
1. Template Generator.

## Libraries/approaches used for the implementation

* SimpleQuestions DBpedia dataset;
* Sklearn library;
