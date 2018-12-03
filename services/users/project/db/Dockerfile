# base image
FROM postgres:10.4-alpine

# run create.sql on init - adds file to this directory, which is autorun on startup of container
ADD create.sql /docker-entrypoint-initdb.d