#!/bin/bash
if [ -n $SERVICE_TYPE ]
then
  if [ $SERVICE_TYPE == "dbpedia_spotlight" ]
  then
    exec gunicorn -b :5000 --access-logfile - --error-logfile - --chdir /home/nuance-core/qanary_components/dbpedia_spotlight app:app
    exit
  elif [ $SERVICE_TYPE == "template_classifier" ]
  then
    exec gunicorn -b :5001 --access-logfile - --error-logfile - --chdir /home/nuance-core/qanary_components/template_classifier app:app
    exit
  elif [ $SERVICE_TYPE == "question_validator" ]
  then
    exec gunicorn -b :5003 --access-logfile - --error-logfile - --chdir /home/nuance-core/qanary_components/question_validator app:app
    exit
  elif [ $SERVICE_TYPE == "relation_classifier" ]
  then
    exec gunicorn -b :5004 --access-logfile - --error-logfile - --chdir /home/nuance-core/qanary_components/relation_classifier app:app
    exit
  elif [ $SERVICE_TYPE == "sparql_builder" ]
  then
    exec gunicorn -b :5005 --access-logfile - --error-logfile - --chdir /home/nuance-core/qanary_components/sparql_builder app:app
    exit
  elif [ $SERVICE_TYPE == "sparql_worker" ]
  then
    exec gunicorn -b :5006 --access-logfile - --error-logfile - --chdir /home/nuance-core/qanary_components/sparql_worker app:app
    exit
  elif [ $SERVICE_TYPE == "template_generator" ]
  then
    exec gunicorn -b :5007 --access-logfile - --error-logfile - --chdir /home/nuance-core/qanary_components/template_generator app:app
    exit
  fi
else
  echo -e "SERVICE_TYPE not set\n"
fi
