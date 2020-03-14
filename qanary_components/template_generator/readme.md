# Template Generator Qanary component
The component generates a natural language output based on templates.

Given a following question text:

Who wrote the film Goodfellas?

and outputs from previous components.

The component outputs a response in natural language:

The author of GOODFELLAS is Nicholas Pileggi.


## Required data input

* Validation result (boolean);
* DBpedia Spotlight NED output (dictionary);
* Intent (string);
* SPARQL worker result.

## Produced data (output)

* Natural Language response (string).

## Typical use within a QA pipeline
1. Template Classifier;
1. Relation Classifier;
1. Dbpedia Spotlight NED;
1. Coreference Resolver;
1. Question Validator;
1. SPARQL Builder;
1. DBpedia SPARQL Worker;
1. **Template Generator**.

## Libraries/approaches used for the implementation

* Basic Python libraries.
