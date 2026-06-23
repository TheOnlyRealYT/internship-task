DarkAtlas Attack Surface Monitoring platform

SETUP:

1- Clone the github repo
2- run "docker compose up" in the root directory
3- to seed an admin run docker exec python -m backend.scripts.seed_admin in cmd or in the built-in docker exec
   inside docker desktop app

ENVIROMENTAL VARIABLES:



RUN INSTRUCTIONS:

The app API runs on port 0.0.0.0:80, you can access it on any browser with just localhost:/
In case of any changes to data schema (EX: adding columns, tables or changing them) run the following two commands:

alembic revision --autogenerate -m "initial schema"
alembic stamp head

we are using stamp head to preseve the prexisting data in the database

The database runs on port 5432 and is a part of the application

Bulk import (ingesting): User must enter asset data in json form, the form provided in the example input is considered
but IDs are explicitly forced to be unique UUIDs for data integrety

When accessing any asset do keep inmind that you are also "activating" that asset via touch, which will happen on get operations (bulk or single)
and on resighting in a bulk ingest or conflict in creating new asset