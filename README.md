This is a [Django](https://www.djangoproject.com/) backend for [sátni.org](http://sátni.org) that uses [Mongodb](https://www.mongodb.com/) to serve a GraphQL-endpoint to the [sátni.org-frontend](https://github.com/divvun/satni-frontend) application.

# Prerequites
* Install and setup mongodb
* Checkout the langtech svn repo parallel to this one (svn checkout https://gtsvn.uit.no/langtech/trunk langtech)
* Set the environment variable GTHOME to point to the working copy of langtech
* Fetch [poetry](https://python-poetry.org/docs/#installation)

# Initial setup
* cp .env.example to .env
* set the app secret (follow the link in .env)
* set the mongodb username and password

```bash
poetry install # install dependencies
poetry run python manage.py migrate # migrate the database
poetry run python manage.py from_dump # import content from langtech
```

## Development
Set DEBUG=True in .env, then run the following command

```bash
poetry run python manage.py runserver
```

Find out which queries are available by going to the built-in GraphQL IDE at http://localhost:8000/graphql/

## Null the database, migrate and import content
```bash
./init_backend.sh
```

The startup of this repo was the [Django and GraphQL intro](https://www.howtographql.com/graphql-python/1-getting-started/)

# Queries

Get all the possible queries

```bash
curl https://satni.uit.no/newsatni/ \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
--compressed \
--data-binary '{"query":"{ __schema{  queryType { fields{ name } } } }"}'
```

Gives this answer:

```json
{
  "data": {
    "__schema": {
      "queryType": {
        "fields": [
          {
            "name": "conceptList"
          },
          {
            "name": "dictEntryList"
          },
          {
            "name": "stemList"
          },
          {
            "name": "hasStem"
          }
        ]
      }
    }
  }
}
```

## stemList

Search the database for lookup words.

Download [lemmas.json](lemmas.json) and run the command:

```bash
curl https://satni.uit.no/newsatni/ \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
--compressed \
--data-binary '@lemmas.json'
```

This command looks for first hundred search words starting with "arg" from our database. The variable `inputValue` is used to define what we look for.
The list `wantedLangs` tells which languages we both do the search in and want an answer for.
The list `wantedDicts` tells which dictionaries we would like answers from.

Edit `lemmas.json` to experiment with the query.

## conceptList and dictEntryList

Get dictionary and terminology articles.

Download [articles.json](artibles.json) and run the command:

```bash
curl https://satni.uit.no/newsatni/ \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
--compressed \
--data-binary '@lemmas.json'
```

This command looks for articles that has `bil` as a lookup word. The variable `lemma` is used to define this. `lemma` must be an exact hit, usually this is fetched from the stemlist.
The list `wantedLangs` tells which languages we both do the search in and want an answer for.
The list `wantedDicts` tells which dictionaries we would like answers from.

Edit `articles.json` to experiment with the query.

## hasStem

Used to decide whether `stem` is in the stemList. In [satni-frontend](https://github.com/divvun/satni-frontend) this is used to decide if a reverse lookup can be done from a translation.

Download [hasStem.json](hasStem.json) and run the command:

```bash
curl https://satni.uit.no/newsatni/ \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
--compressed \
--data-binary '@hasStem.json'
```

## Find all capabilities

To get a complete overview what this backend offers, download [all.json](all.json) and do the command:

```bash
curl https://satni.uit.no/newsatni/ \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
--compressed \
--data-binary '@all.json'
```
