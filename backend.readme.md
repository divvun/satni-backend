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
