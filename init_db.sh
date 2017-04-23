#!/bin/sh

#first arg username , second arg database name
cd /
psql -c "CREATE USER tweet WITH PASSWORD 'tweet';"
sudo -u zeljko createdb "sedam_cvrkuta" --owner="tweet"