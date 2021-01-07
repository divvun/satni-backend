#!/bin/bash

mongo localhost:27017/satnibackend drop_satnibackend.js
rm -v db.sqlite3
for i in lemmas terms
  do rm -v $i/migrations/0*
done
poetry run python manage.py makemigrations
poetry run python manage.py migrate
poetry run python manage.py runscript from_dump
