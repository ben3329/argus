# argus

Monitoring system for Server and Process.
**As this is currently under development, backwards compatibility is not guaranteed.**

## built-in function

* system memory used, utilization

# Installation

## requirements

docker, docker-compose

## with source

1. clone repository
  <pre>git clone https://github.com/ben3329/argus.git</pre>
2. build image
  <pre>./build_image.sh</pre>
  * this command will create images. ben3329/argus, bene3329/argus-celery-worker, ben3329/scrape
3. edit environment variable
  * Edit values in `.env`. especially starting with EMAIL
4. run docker container
  <pre>docker-compose up -d</pre>

## without source

1. download directory
  * download `without_src/docker-compose`
2. edit environment variable
  * Edit values in `.env`. especially starting with EMAIL
3. run docker container
  <pre>docker-compose up -d</pre>

# System Structure

![structure](doc/images/structure.drawio.svg)