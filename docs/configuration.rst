.. _configuration:

Configuration
=============

Introduction
------------

The Alignak backend uses a configuration file that it searchs for in one of these folders:

   * /usr/local/etc/alignak-backend/settings.json
   * /etc/alignak-backend/settings.json
   * etc/alignak-backend/settings.json
   * ./etc/settings.json
   * ../etc/settings.json
   * ./settings.json

.. note:: that the default installation directory is not in this list; this to avoid using the default shipped file by mistake !

The best solution to define which configuration file is to be used is to set an environment variable. If ``ALIGNAK_BACKEND_CONFIGURATION_FILE`` is defined, the file name defined in this variable takes precedence over the default files list.

.. warning:: it is not recommended to use the default shipped configuration file because an update of the installed application will almost surely replace the content of this file and you will loose any modification you did in the file!

The configuration file is a JSON structured file in which comments are allowed. the default shipped file is commented to explain all the configuration variables::

   {
     "DEBUG": false, /* To run underlying server in debug mode, define true */

     "HOST": "",           /* Backend server listening address, empty = all */
     "PORT": 5000,         /* Backend server listening port */
     "SERVER_NAME": null,  /* Backend server listening server name */

     "X_DOMAINS": "*", /* CORS (Cross-Origin Resource Sharing) support. Accept *, empty or a list of domains */

     "PAGINATION_LIMIT": 5000,   /* Pagination: maximum value for number of results */
     "PAGINATION_DEFAULT": 50,   /* Pagination: default value for number of results */

     /* Limit number of requests. For example, [300, 900] limit 300 requests every 15 minutes */
     "RATE_LIMIT_GET": null,     /* Limit number of GET requests */
     "RATE_LIMIT_POST": null,    /* Limit number of POST requests */
     "RATE_LIMIT_PATCH": null,   /* Limit number of PATCH requests */
     "RATE_LIMIT_DELETE": null,  /* Limit number of DELETE requests */

     "MONGO_URI": "mongodb://localhost:27017/alignak-backend",
     "MONGO_HOST": "localhost",          /* Address of MongoDB */
     "MONGO_PORT": 27017,                /* port of MongoDB */
     "MONGO_DBNAME": "alignak-backend",  /* Name of database in MongoDB */
     "MONGO_USERNAME": null,             /* Username to access to MongoDB */
     "MONGO_PASSWORD": null,             /* Password to access to MongoDB */

     "IP_CRON": ["127.0.0.1"],  /* List of IP allowed to use cron routes/endpoint of the backend */


     "LOGGER": "alignak-backend-logger.json",  /* Python logger configuration file */

     /* Address of Alignak arbiter
     The Alignak backend will use this adress to notify Alignak about backend newly created
     or deleted items
     Set to an empty value to disable this feature
     */
     "ALIGNAK_URL": "http://127.0.0.1:7770",

     /* Alignak event reporting scheduler
     Every SCHEDULER_ALIGNAK_PERIOD, an event is raised to the ALIGNAK_URL if an host/realm/user
     was created or deleted

     Only raise notifications every 10 minutes
     */
     "SCHEDULER_ALIGNAK_ACTIVE": true,
     "SCHEDULER_ALIGNAK_PERIOD": 600,

     /* As soon as a Graphite or Influx is existing in the backend, the received metrics are sent
     to the corresponding TSDB. If the TSDB is not available, metrics are stored internally
     in the backend.
     The timeseries scheduler will check periodially if some some metrics are existing in the
     retention and will send them to the configured TSDB.
      BE CAREFULL, ACTIVATE THIS ON ONE BACKEND ONLY! */
     "SCHEDULER_TIMESERIES_ACTIVE": false,
     "SCHEDULER_TIMESERIES_PERIOD": 10,
     /* This scheduler will create / update dashboards in grafana.
      BE CAREFULL, ACTIVATE IT ONLY ON ONE BACKEND */
     "SCHEDULER_GRAFANA_ACTIVE": false,
     "SCHEDULER_GRAFANA_PERIOD": 120,
     /* Enable/disable this backend instance as a Grafana datasource */
     "GRAFANA_DATASOURCE": true,
     /* Name of the file that contains the list of proposed queries in a Grafana table panel */
     "GRAFANA_DATASOURCE_QUERIES": "grafana_queries.json",
     /* Name of the file that contains the list of fields returned for a Grafana table */
     "GRAFANA_DATASOURCE_TABLES": "grafana_tables.json",
     /* if 0, disable it, otherwise define the history in minutes.
      It will keep history each minute.
      BE CAREFULL, ACTIVATE IT ONLY ON ONE BACKEND */
     "SCHEDULER_LIVESYNTHESIS_HISTORY": 60
   }


If an environment variable `ALIGNAK_BACKEND_LOGGER_CONFIGURATION` exist, it will override the one defined in the settings file for the logger configuration file.

If an environment variable `ALIGNAK_BACKEND_MONGO_URI` exist, it will override the one defined in the settings file for the MongoDB connection string.
If an environment variable `ALIGNAK_BACKEND_MONGO_DBNAME` exist, it will override the one defined in the settings file and will be used as the database name.

Debug section
-------------

By default, debug mode is disabled, if you want to activate it (developer mode...), modify for::

    "DEBUG": true,


It's used in case you want to run the backend in developer mode.

Web server configuration
------------------------

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


In place of all these configuration variables you can more simply define a Mongo connection string that will take precedence over the formerly defined variables::

    "MONGO_URI": "mongodb://[username:password@]host1[:port1][,host2[:port2],...[,hostN[:portN]]][/[database][?options]]"

If the ``MONGO_URI`` variable is not empty it takes precedence over the ``MONGO_HOST``, ``MONGO_PORT``, ... definitions.
**Note** the slashes escaping...

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

Grafana datasource
------------------

The Grafana datasource available queries are defined in a json file which name is declared in:
 ::

    "GRAFANA_DATASOURCE_QUERIES": "grafana_queries.json"

This configuration file variable may be overriden with an environment variable: `ALIGNAK_BACKEND_GRAFANA_DATASOURCE_QUERIES`.

The Grafana datasource tables available are defined in a json file which name is declared in:
 ::

    "GRAFANA_DATASOURCE_TABLES": "grafana_tables.json"

This configuration file variable may be overriden with an environment variable: `ALIGNAK_BACKEND_GRAFANA_DATASOURCE_TABLES`.
