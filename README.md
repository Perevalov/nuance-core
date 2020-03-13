# Cerence Complex Question Answering system

## Definition

## How to start

Requirements:

* Check if you have docker and docker-compose installed on your system;
* Check if Java 8 (`java -version`) and Maven 3.5.2 (`mvn -v`) or higher are available on your system (system requirements).

1. Clone repo with server side: https://github.com/Perevalov/nuance-core using (`git clone`)
1. Clone repo with client side: https://github.com/Perevalov/nuance-web using (`git clone`)
1. Build and start Qanary pipeline: https://github.com/WDAqua/Qanary#without-creating-docker-images
1. Start server side application by running following commands in nuance-core folder:
    1. ```sudo docker build -t nuance-core:latest .```
    1. ```sudo docker-compose up```
1. Start client side application by running following commands in nuance-core folder:
    1. ```sudo docker build -t nuance-web:latest .```
    1. ```sudo docker-compose up```
1. Go to 127.0.0.1:41210 and enjoy the running application!
