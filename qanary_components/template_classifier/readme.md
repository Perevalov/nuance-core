# Template Classifier Qanary component
The component recognizes the query template by question text.

Given a following question text:

Where is the artist Vitas from?

The component outputs a classified template:

**Forward Query**

List of all templates:
* Forward - Subject-Predicate-?;
* Backward - ?-Predicate-Object;
* Boolean - SPARQL ASK query;
* Distance - Distance between X and Y;
* Tell me more about - Get abstract of an entity;
* What i see - Giving a list of places around.


## Required data input

* Question text (string).

## Produced data (output)

* Query template (string).

## Typical use within a QA pipeline
1. **Template Classifier**;
1. Relation Classifier;
1. Dbpedia Spotlight NED;
1. Coreference Resolver;
1. Question Validator;
1. SPARQL Builder;
1. DBpedia SPARQL Worker;
1. Template Generator.

## Libraries/approaches used for the implementation

* Sklearn.
