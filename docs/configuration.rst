.. _configuration:

Configuration
=============

Introduction
------------

The backend uses a configuration file.
It is located in one of these folders:

* /usr/local/etc/alignak_backend/settings.json
* /etc/alignak_backend/settings.json

It's a JSON structured file.

Debug section
-------------

By default, debug mode is disabled, if you want to activate it, modify for::

    "DEBUG": true,


Webserver configuration
-----------------------

It's used in case you want to run the backend in developer mode.

Define IP listening (empty value = listen on all IP)::

    "HOST": "",

Define port listening::

    "PORT": 5000,

Define server name listening::

    "SERVER_NAME": null,


Cross-Origin Resource Sharing
-----------------------------

You can configure the Cross-Origin Resource Sharing (CORS) to define who can access with cross-origin.
To accept all::

    "X_DOMAINS": "*",


Pagination
----------

it's possible to modify the maximum pagination (limit) of items returned by the backend::

    "PAGINATION_LIMIT": 50,

And the default value for the pagination::

    "PAGINATION_DEFAULT": 25,

Rate limit
----------

It's possible to limit the number of requests.
For example, define value [300, 900] will limit 300 requests every 15 minutes.
You define the values for each methods (GET, POST, PATCH, DELETE). An example::

    "RATE_LIMIT_GET": [300, 900],
    "RATE_LIMIT_POST": null,
    "RATE_LIMIT_PATCH": null,
    "RATE_LIMIT_DELETE": null,


MongoDB access
--------------

You need to fill information about the MongoDB to access it in goal to store and get data.

The hostname of the server where the MongoDB run::

    "MONGO_HOST": "localhost",

The port of the MongoDB::

    "MONGO_PORT": 27017,

The database name of MongoDB used for the Backend::

    "MONGO_DBNAME": "alignak-backend",

The username and password to access MongoDB and the database defined previously::

    "MONGO_USERNAME": null,
    "MONGO_PASSWORD": null,
