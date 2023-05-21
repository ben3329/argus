#!/bin/bash
NPMDIR="`pwd`/argus/static/npm"
npm install --prefix ${NPMDIR} bootstrap-icons@1.10.3
npm install --prefix ${NPMDIR} bootstrap@5.2.3
npm install --prefix ${NPMDIR} chart.js@4.3.0
npm install --prefix ${NPMDIR} jquery@3.6.3
cd argus
DOCKER_BUILDKIT=1 docker build -t argus:latest .
cd ../scrape
DOCKER_BUILDKIT=1 docker build -t scrape:latest .
