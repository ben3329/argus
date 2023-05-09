#!/bin/bash
docker-compose down
rm -rf database-data/*
rm -rf argus/monitoring/migrations
rm -rf logs/*
docker-compose up -d