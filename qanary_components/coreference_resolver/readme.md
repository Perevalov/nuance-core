# Coreference Resolver Qanary component
The component solves coreference resolution task.

Given a following dialogue:

* Q1: Who was the director of **Django Unchained**?
* A1: The director is Quentin Tarantino.
* Q2: Tell me more about **it**
* A2: Django Unchained is a 2012 American western film ...

We have to make a direct link between **Django Unchained** from Q1 and **it** from Q2 to give more information about coreferenced entity.

## Required data input

* Question text (string);
* Dialogue (or session) id (string);

## Produced data (output)

* A link to coreferenced entity (string).

## Typical use within a QA pipeline
1. Template Classifier;
1. Relation Classifier;
1. Dbpedia Spotlight NED;
1. **Coreference Resolver**;
1. Question Validator;
1. SPARQL Builder;
1. DBpedia SPARQL Worker;
1. Template Generator.

## Libraries/approaches used for the implementation

* Neuralcoref - for making coreference resolution (https://github.com/huggingface/neuralcoref);
* SpaCy - for providing required interfaces for neuralcoref (https://spacy.io/).
