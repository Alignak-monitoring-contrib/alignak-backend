.. _configuration:

Configuration
=============

Introduction
------------

The backend uses a configuration file that is located in one of these folders:

   * /usr/local/etc/alignak_backend/settings.json
   * /etc/alignak_backend/settings.json
   * etc/alignak_backend/settings.json
   * ./etc/settings.json
   * ../etc/settings.json
   * ./settings.json

If an environment variable `ALIGNAK_BACKEND_CONFIGURATION_FILE` exist, the file name defined in this variable takes precedence over the default files list.

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

You need to fill information about the MongoDB used to store and retrieve data.

The hostname of the server where the MongoDB run::

    "MONGO_HOST": "localhost",

The port of the MongoDB::

    "MONGO_PORT": 27017,

The database name of MongoDB used for the Backend::

    "MONGO_DBNAME": "alignak-backend",

The username and password to access MongoDB and the database defined previously::

    "MONGO_USERNAME": null,
    "MONGO_PASSWORD": null,


Timeseries databases
--------------------

To activate the timeseries database feeding from the backend, you need to activate the timeseries scheduler.

Activate the scheduler to push performance data to the configured database::

  "SCHEDULER_TIMESERIES_ACTIVE": false,

Activate the scheduler to create Grafana panels for the host/service performance data::

  "SCHEDULER_GRAFANA_ACTIVE": false

Logger configuration
--------------------

The Alignak backend sends information to a logger that is configured thanks to a JSON file.::

  "LOGGER": "alignak-backend-logger.json"

 All the API requests will be logged:
    * at INFO level for the
If the file name defined in this configuration variable is not an absolute file name, the configuration file is searched in the same directory where the *settings.json* was found.

 The Alignak backend logger is configured with the content of the found configuration file, but some specific variables are used in this file:
    * `%(logdir)s`, will be replaced with the log files directory
    * `%(daemon)s`.log, will be replaced with the backend name

 The directory where the log file will be stored is searched in this ordered directory list:
    * /usr/local/var/log/alignak_backend
    * /var/log/alignak_backend
    * /usr/local/var/log/alignak
    * /var/log/alignak
    * /usr/local/var/log
    * /var/log
    * /tmp

 Once a directory in this list exists and is writable, it will be retained as the log files directory.

 The alignak backend name is built as a concatenation of:
    * the `NAME` configuration variable if it not null, else 'alignak-backend'
    * the `MONGO_DBNAME`

 If the log files directory do not contain `alignak-backend`, this text is prepended.

Livesynthesis history
---------------------

To have an history of the live synthesis (every minute) during xx minutes, you need to activate the history scheduler.

To activate, define the number of minutes you want to keep history, *0* to disable, example for 30 minutes::

  "SCHEDULER_LIVESYNTHESIS_HISTORY": 30
