#!/bin/bash

# Install npm
NPMDIR="`pwd`/argus/static/npm"
npm install --prefix ${NPMDIR} bootstrap-icons@1.10.3
npm install --prefix ${NPMDIR} bootstrap@5.2.3
npm install --prefix ${NPMDIR} chart.js@4.3.0
npm install --prefix ${NPMDIR} jquery@3.6.3

# Create argus image
if [ "$1" == "package" ]; then
    cp package/Dockerfile.argus.package Dockerfile
    cp package/requirements.txt.argus argus/requirements.txt
else
    cp package/Dockerfile.argus Dockerfile
    cp package/requirements.txt.argus requirements.txt
fi
DOCKER_BUILDKIT=1 docker build -t ben3329/argus:latest .

# Create celery image
cp package/Dockerfile.celery_worker Dockerfile
DOCKER_BUILDKIT=1 docker build -t ben3329/argus-celery-worker:latest .

# Create scrape image
if [ "$1" == "package" ]; then
    cp package/Dockerfile.scrape.package Dockerfile
    cp package/requirements.txt.scrape scrape/requirements.txt
else
    cp package/Dockerfile.scrape Dockerfile
    cp package/requirements.txt.scrape requirements.txt
fi
DOCKER_BUILDKIT=1 docker build -t ben3329/scrape:latest .
