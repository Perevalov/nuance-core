#!/bin/bash
if [ -n $SERVICE_TYPE ]
then
  if [ $SERVICE_TYPE == "backend" ]
  then
    exec gunicorn -b :5050 --access-logfile - --error-logfile - app:app
    exit
  fi
else
  echo -e "SERVICE_TYPE not set\n"
fi
