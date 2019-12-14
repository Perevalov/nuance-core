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
  fi
else
  echo -e "SERVICE_TYPE not set\n"
fi
