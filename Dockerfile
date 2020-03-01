FROM python:3.6.6-slim

WORKDIR /home/nuance-core

COPY requirements.txt ./

# Install required libs
RUN pip install --upgrade pip -r requirements.txt; exit 0

RUN pip install gunicorn
RUN python -m spacy download en

# Копирование файлов проекта
COPY data data
COPY dblayer dblayer
COPY intents intents
COPY managers managers
COPY models models
COPY nlg nlg
COPY nlu nlu
COPY notebooks notebooks
COPY qanary_components qanary_components
COPY resources resources
COPY SPARQL SPARQL
COPY test test
COPY app.py config.py boot.sh ./

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


RUN chmod +x boot.sh

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
