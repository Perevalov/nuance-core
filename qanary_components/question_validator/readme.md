# Question Validator Qanary component
The component checks if the number of parameters in the recognized question's query type equals retrieved parameters from NED component.

Given a following question and it's recognized template:

Was Angela Merkel born in Hamburg?

```
  "boolean": {
    "query": {
      "head": "PREFIX dbr: <http://dbpedia.org/resource/> ASK where { ",
      "values": " VALUES ?p {{{values}}} . ",
      "body": " <{entity_1}> ?p <{entity_2}> . ",
      "closure": " }"
    },
    "parameters_number": 2
    }
```

And following dictionary from NED component:

`{'Angela Merkel': 'http://dbpedia.org/page/Angela_Merkel', 'Hamburg': 'http://dbpedia.org/page/Hamburg'}`

The component says that the question is **valid**.

If the number of keys in the dictionary is not equal to the required number, then the question is **not valid**.

**TODO:** check the type of the keys and entities also.

## Required data input

* Question text (string);
* Recognized question's template;
* Dictionary from DBpedia NED component.

## Produced data (output)

* Valid or not valid (boolean).

## Typical use within a QA pipeline
1. Template Classifier;
1. Relation Classifier;
1. Dbpedia Spotlight NED;
1. Coreference Resolver;
1. **Question Validator**;
1. SPARQL Builder;
1. DBpedia SPARQL Worker;
1. Template Generator.

## Libraries/approaches used for the implementation

* Python basic libraries.
