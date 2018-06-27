.. _run:

Run
===

Preparing...
------------

The alignak backend installation script used when you install with pip:

* creates a *alignak-backend-uwsgi* launch script located in */usr/local/bin*

* ships some files in */usr/local/share/alignak-backend*

Environment variables
---------------------

Some useful environment variables exist:

- `ALIGNAK_BACKEND_CONFIGURATION_FILE`, the file name defined in this variable takes precedence over the default files list.

- `ALIGNAK_BACKEND_UWSGI_FILE`, the `alignak-backend-uwsgi` script will use the file name defined in this variable as the uWSGI configuration file.

- `ALIGNAK_BACKEND_LIVESYNTHESIS_TSDB`, and its value equals '0' then the counters of the livesynthesis will not be sent to the timeseries databases.

- `ALIGNAK_BACKEND_LOGGER_CONFIGURATION`, it will define the settings file for the logger configuration file.

- `ALIGNAK_BACKEND_MONGO_URI`, it will be used as the MongoDB connection string.

- `ALIGNAK_BACKEND_MONGO_DBNAME`, it will be used as the database name.


Running from the commad line
----------------------------
Thanks to this, you can simply run::

    alignak-backend-uwsgi

 When started with uWSGI the Alignak backend logs its activity in a file */usr/local/var/log/alignak-backend/backend-error.log*. This file is the log file built by the uWSGI server.

.. warning:: If you do not have this file when the backend is started, make sure that the user account used to run the backend is allowed to write in the */usr/local/var/log* directory ;)

 The Alignak backend configuration allows to define and configure a logger that will log the backend API endpoints to file located in the same directory. see the configuration page for more information on how to configure this logger.


To stop / reload the Alignak backend application::

    # Ctrl+C in the session where you started the alignak-backend-uwsgi script will stop the Alignak backend

    # To gracefully reload all the workers
    $ kill -SIGHUP `cat /tmp/alignak-backend.pid`

    # To gently kill and restart all the workers
    $ kill -SIGTERM `cat /tmp/alignak-backend.pid`

    # To brutally kill all the workers
    $ kill -SIGINT `cat /tmp/alignak-backend.pid`


Systemd service
---------------

If your system is a recent Linux distribution (Debian 7, Ubuntu 16) using *systemctl*, and you installed from the distro packaging, you should have installed a system service that allow starting Alignak backend with the standard `systemctl` command.

All you need to do is to inform Alignak backend where it should find the main configuration file. Using the ``ALIGNAK_BACKEND_CONFIGURATION_FILE`` environment variable is the simplest solution.

This variable is configured, as default, in the Alignak backend service unit::

   # Environment variables - may be overriden in the /etc/default/alignak-backend
   Environment=ALIGNAK_BACKEND_CONFIGURATION_FILE=/usr/local/share/alignak-backend/etc/settings.json
   Environment=ALIGNAK_BACKEND_PID=/var/run/alignak-backend/alignak-backend.pid
   Environment=ALIGNAK_BACKEND_LOG=/var/log/alignak-backend/alignak-backend.log
   Environment=ALIGNAK_BACKEND_UWSGI_LOG=/var/log/uwsgi/alignak-backend.log
   Environment=ALIGNAK_BACKEND_HOST=127.0.0.1
   Environment=ALIGNAK_BACKEND_PORT=5000
   Environment=ALIGNAK_BACKEND_PROCESSES=4
   Environment=ALIGNAK_USER=alignak
   Environment=ALIGNAK_GROUP=alignak
   EnvironmentFile=-/etc/default/alignak-backend

To change its value, you can create an environment configuration file in */etc/default/alignak*::

   ALIGNAK_BACKEND_CONFIGURATION_FILE=/usr/local/etc/my-alignak-backend.json
   ALIGNAK_USER=my-alignak
   ALIGNAK_GROUP=my-alignak

.. note:: that the Alignak user/group information are also configurable thanks to this feature. If you did not created the default proposed user account, you must update the default information in the service unit file or default configuration file.

.. warning:: only use the default shipped configuration file if you do not have any modification to do in the content of this file. An update of the installed application will almost surely replace the content of this file and you will loose any modification you did in the file!


To make Alignak backend start automatically when the system boots up::

      # Enable Alignak backend on system start
      sudo systemctl enable alignak-backend.service

And to manage Alignak backend services::

      # Start Alignak backend
      sudo systemctl start alignak-backend

      # Stop Alignak backend
      sudo systemctl stop alignak-backend



Developer mode
--------------

To run in developper mode (meaning with few connections), you can start the backend with this command::

   alignak-backend

On start, some useful information are printed on the console::

    *** Starting uWSGI 2.0.12-debian (64bit) on [Thu Dec 15 08:32:51 2016] ***
    compiled with version: 5.3.1 20160412 on 13 April 2016 08:36:06
    os: Linux-4.4.0-53-generic #74-Ubuntu SMP Fri Dec 2 15:59:10 UTC 2016
    nodename: Alignak-VirtualBox
    machine: x86_64
    clock source: unix
    pcre jit disabled
    detected number of CPU cores: 2
    current working directory: /home/alignak/alignak-backend
    detected binary path: /usr/bin/uwsgi-core
    *** WARNING: you are running uWSGI without its master process manager ***
    your processes number limit is 15649
    your memory page size is 4096 bytes
    detected max file descriptor number: 1024
    lock engine: pthread robust mutexes
    thunder lock: disabled (you can enable it with --thunder-lock)
    uwsgi socket 0 bound to TCP address 0.0.0.0:5000 fd 3
    Python version: 2.7.12 (default, Nov 19 2016, 06:48:10)  [GCC 5.4.0 20160609]
    Python main interpreter initialized at 0x26e7760
    python threads support enabled
    your server socket listen backlog is limited to 100 connections
    your mercy for graceful operations on workers is 60 seconds
    mapped 291072 bytes (284 KB) for 4 cores
    *** Operational MODE: preforking ***
    --------------------------------------------------------------------------------
    Alignak_Backend, version 0.5.5
    Copyright (c) 2015 - Alignak team
    License GNU Affero General Public License, version 3
    --------------------------------------------------------------------------------
    Doc: https://github.com/Alignak-monitoring-contrib/alignak-backend
    Release notes: Alignak REST Backend
    --------------------------------------------------------------------------------
    Using settings file: /etc/alignak-backend/settings.json
    Application settings: {'CARBON_PORT': 2004, 'XML': False, 'GRAPHITE_PORT': 8080, 'JOBS': [], 'PAGINATION_DEFAULT': 25, u'GRAFANA_HOST': None, 'GRAPHITE_HOST': u'', u'RATE_LIMIT_POST': None, 'PORT': 5000, u'MONGO_USERNAME': None, 'SERVER_NAME': None, 'X_HEADERS': 'Authorization, If-Match, X-HTTP-Method-Override, Content-Type', 'X_DOMAINS': u'*', 'SCHEDULER_TIMESERIES_ACTIVE': False, u'GRAFANA_PORT': 3000, 'INFLUXDB_PORT': 8086, u'RATE_LIMIT_DELETE': None, 'INFLUXDB_DATABASE': u'alignak', 'SCHEDULER_TIMEZONE': 'Etc/GMT', u'MONGO_PASSWORD': None, 'CARBON_HOST': u'', 'MONGO_PORT': 27017, 'RESOURCE_METHODS': ['GET', 'POST', 'DELETE'], 'MONGO_DBNAME': u'alignak-backend', 'HOST': u'', u'GRAFANA_APIKEY': u'', 'DEBUG': False, u'RATE_LIMIT_PATCH': None, 'INFLUXDB_PASSWORD': u'admin', 'PAGINATION_LIMIT': 50, 'INFLUXDB_HOST': u'', 'INFLUXDB_LOGIN': u'admin', 'SCHEDULER_GRAFANA_ACTIVE': False, 'ITEM_METHODS': ['GET', 'PATCH', 'DELETE'], u'RATE_LIMIT_GET': None, 'MONGO_HOST': u'localhost', 'MONGO_QUERY_BLACKLIST': ['$where'], u'GRAFANA_TEMPLATE_DASHBOARD': {u'timezone': u'browser', u'refresh': u'1m'}}
    WSGI app 0 (mountpoint='') ready in 3 seconds on interpreter 0x26e7760 pid: 1721 (default app)
    *** uWSGI is running in multiple interpreter mode ***
    spawned uWSGI worker 1 (pid: 1721, cores: 1)
    spawned uWSGI worker 2 (pid: 1729, cores: 1)
    spawned uWSGI worker 3 (pid: 1730, cores: 1)
    spawned uWSGI worker 4 (pid: 1731, cores: 1)


Alignak-backend runs on port 5000, so you should use ``http://ip:5000/`` as a base URL for the API.

Change default admin password
-----------------------------

The default login / password is *admin* / *admin*.

To change the default password, do:

* get the current admin token and it will give you something like *1442583814636-bed32565-2ff7-4023-87fb-34a3ac93d34c*::

    curl -H "Content-Type: application/json" -X POST -d '{"username":"admin","password":"admin"}' http://127.0.0.1:5000/login

* get the *_id* and the *_etag* fields with the command::

    curl -H "Content-Type: application/json" --user "1442583814636-bed32565-2ff7-4023-87fb-34a3ac93d34c:" 'http://127.0.0.1:5000/user?projection=\{"name":1\}'

* update the password::

    curl -X PATCH -H "Content-Type: application/json" -H "If-Match: the_etag"
    --user "1442583814636-bed32565-2ff7-4023-87fb-34a3ac93d34c:"
    -d '{"password": "yournewpassword"}' http://127.0.0.1:5000/user/the_id

What about MongoDB and the Alignak backend?
-------------------------------------------

On the very first Alignak backend start, a connection is established with the configured MongoDB. The configured database is created if it does not exist and some collections and indexes are set-up in this database. For MongoDB DBA, the mongo log for this operation::

   2018-06-28T11:39:46.050+0200 I CONTROL  [initandlisten]
   2018-06-28T11:39:46.059+0200 I STORAGE  [initandlisten] createCollection: admin.system.version with provided UUID: f60914c4-0586-4857-8806-08cca9b498b6
   2018-06-28T11:39:46.076+0200 I COMMAND  [initandlisten] setting featureCompatibilityVersion to 4.0
   2018-06-28T11:39:46.083+0200 I STORAGE  [initandlisten] createCollection: local.startup_log with generated UUID: 2aa3f574-afc3-457b-ae1a-63bdb2e4ca31
   2018-06-28T11:39:46.114+0200 I FTDC     [initandlisten] Initializing full-time diagnostic data capture with directory '/var/lib/mongodb/diagnostic.data'
   2018-06-28T11:39:46.116+0200 I NETWORK  [initandlisten] waiting for connections on port 27017
   2018-06-28T11:39:46.117+0200 I STORAGE  [LogicalSessionCacheRefresh] createCollection: config.system.sessions with generated UUID: e64bb8c0-c607-4947-bfa6-61e7bbd04605
   2018-06-28T11:39:46.136+0200 I INDEX    [LogicalSessionCacheRefresh] build index on: config.system.sessions properties: { v: 2, key: { lastUse: 1 }, name: "lsidTTLIndex", ns: "config.system.sessions", expireAfterSeconds: 1800 }
   2018-06-28T11:39:46.136+0200 I INDEX    [LogicalSessionCacheRefresh] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:39:46.137+0200 I INDEX    [LogicalSessionCacheRefresh] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:13.891+0200 I NETWORK  [listener] connection accepted from 127.0.0.1:47172 #1 (1 connection now open)
   2018-06-28T11:40:13.894+0200 I NETWORK  [conn1] received client metadata from 127.0.0.1:47172 conn1: { driver: { name: "PyMongo", version: "3.7.0" }, os: { type: "Linux", name: "Ubuntu 16.04 xenial", architecture: "x86_64", version: "4.4.0-128-generic" }, platform: "CPython 2.7.12.final.0" }
   2018-06-28T11:40:13.896+0200 I NETWORK  [listener] connection accepted from 127.0.0.1:47174 #2 (2 connections now open)
   2018-06-28T11:40:13.896+0200 I NETWORK  [conn2] received client metadata from 127.0.0.1:47174 conn2: { driver: { name: "PyMongo", version: "3.7.0" }, os: { type: "Linux", name: "Ubuntu 16.04 xenial", architecture: "x86_64", version: "4.4.0-128-generic" }, platform: "CPython 2.7.12.final.0" }
   2018-06-28T11:40:13.897+0200 I STORAGE  [conn2] createCollection: alignak-backend.logcheckresult with generated UUID: 0a81e5ca-a610-4be5-b215-9bebc86e8827
   2018-06-28T11:40:13.936+0200 I INDEX    [conn2] build index on: alignak-backend.logcheckresult properties: { v: 2, key: { _created: 1 }, name: "index_created", ns: "alignak-backend.logcheckresult" }
   2018-06-28T11:40:13.936+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:13.937+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:13.944+0200 I INDEX    [conn2] build index on: alignak-backend.logcheckresult properties: { v: 2, key: { host_name: 1 }, name: "index_host_name", ns: "alignak-backend.logcheckresult" }
   2018-06-28T11:40:13.944+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:13.945+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:13.953+0200 I INDEX    [conn2] build index on: alignak-backend.logcheckresult properties: { v: 2, key: { host: 1 }, name: "index_host", ns: "alignak-backend.logcheckresult" }
   2018-06-28T11:40:13.953+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:13.954+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:13.967+0200 I INDEX    [conn2] build index on: alignak-backend.logcheckresult properties: { v: 2, key: { service_name: 1 }, name: "index_service_name", ns: "alignak-backend.logcheckresult" }
   2018-06-28T11:40:13.967+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:13.968+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:13.986+0200 I INDEX    [conn2] build index on: alignak-backend.logcheckresult properties: { v: 2, key: { _updated: 1 }, name: "index_updated", ns: "alignak-backend.logcheckresult" }
   2018-06-28T11:40:13.986+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:13.987+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.007+0200 I INDEX    [conn2] build index on: alignak-backend.logcheckresult properties: { v: 2, key: { service: 1 }, name: "index_service", ns: "alignak-backend.logcheckresult" }
   2018-06-28T11:40:14.007+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.008+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.016+0200 I INDEX    [conn2] build index on: alignak-backend.logcheckresult properties: { v: 2, key: { host_name: 1, service_name: 1 }, name: "index_host_service_name", ns: "alignak-backend.logcheckresult" }
   2018-06-28T11:40:14.016+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.017+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.024+0200 I STORAGE  [conn2] createCollection: alignak-backend.usergroup with generated UUID: 06addce0-f6f2-4ffa-a2b2-e538a44ad608
   2018-06-28T11:40:14.051+0200 I INDEX    [conn2] build index on: alignak-backend.usergroup properties: { v: 2, key: { _updated: 1 }, name: "index_updated", ns: "alignak-backend.usergroup" }
   2018-06-28T11:40:14.052+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.052+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.061+0200 I INDEX    [conn2] build index on: alignak-backend.usergroup properties: { v: 2, key: { name: 1 }, name: "index_name", ns: "alignak-backend.usergroup" }
   2018-06-28T11:40:14.061+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.062+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.072+0200 I STORAGE  [conn2] createCollection: alignak-backend.realm with generated UUID: dd31d611-b746-4c78-8db1-8d351f1a39aa
   2018-06-28T11:40:14.095+0200 I INDEX    [conn2] build index on: alignak-backend.realm properties: { v: 2, key: { _updated: 1 }, name: "index_updated", ns: "alignak-backend.realm" }
   2018-06-28T11:40:14.095+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.097+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.108+0200 I INDEX    [conn2] build index on: alignak-backend.realm properties: { v: 2, key: { name: 1 }, name: "index_name", ns: "alignak-backend.realm" }
   2018-06-28T11:40:14.108+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.110+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.113+0200 I STORAGE  [conn2] createCollection: alignak-backend.service with generated UUID: b16c83e4-aec6-4c02-80ec-0d2ad63dac7f
   2018-06-28T11:40:14.135+0200 I INDEX    [conn2] build index on: alignak-backend.service properties: { v: 2, key: { _is_template: 1 }, name: "index_tpl", ns: "alignak-backend.service" }
   2018-06-28T11:40:14.135+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.139+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.149+0200 I INDEX    [conn2] build index on: alignak-backend.service properties: { v: 2, key: { host: 1, name: 1 }, name: "index_host", ns: "alignak-backend.service" }
   2018-06-28T11:40:14.149+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.150+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.158+0200 I INDEX    [conn2] build index on: alignak-backend.service properties: { v: 2, key: { _realm: 1, _is_template: 1 }, name: "index_realm", ns: "alignak-backend.service" }
   2018-06-28T11:40:14.158+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.159+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.172+0200 I INDEX    [conn2] build index on: alignak-backend.service properties: { v: 2, key: { _realm: 1, _is_template: 1, ls_state: 1, ls_state_type: 1, ls_downtimed: 1 }, name: "index_state_3", ns: "alignak-backend.service" }
   2018-06-28T11:40:14.172+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.178+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.187+0200 I INDEX    [conn2] build index on: alignak-backend.service properties: { v: 2, key: { name: 1 }, name: "index_name", ns: "alignak-backend.service" }
   2018-06-28T11:40:14.187+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.189+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.199+0200 I INDEX    [conn2] build index on: alignak-backend.service properties: { v: 2, key: { _realm: 1, _is_template: 1, ls_state: 1, ls_state_type: 1, ls_acknowledged: 1 }, name: "index_state_2", ns: "alignak-backend.service" }
   2018-06-28T11:40:14.199+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.200+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.213+0200 I INDEX    [conn2] build index on: alignak-backend.service properties: { v: 2, key: { _updated: 1 }, name: "index_updated", ns: "alignak-backend.service" }
   2018-06-28T11:40:14.213+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.214+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.226+0200 I INDEX    [conn2] build index on: alignak-backend.service properties: { v: 2, key: { _realm: 1, _is_template: 1, ls_state: 1, ls_state_type: 1 }, name: "index_state_1", ns: "alignak-backend.service" }
   2018-06-28T11:40:14.226+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.227+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.235+0200 I INDEX    [conn2] build index on: alignak-backend.service properties: { v: 2, key: { _realm: 1, _is_template: 1, ls_state: 1, ls_state_type: 1, active_checks_enabled: 1, passive_checks_enabled: 1 }, name: "index_state_4", ns: "alignak-backend.service" }
   2018-06-28T11:40:14.235+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.236+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.241+0200 I STORAGE  [conn2] createCollection: alignak-backend.livesynthesis with generated UUID: a1483c70-2cb2-430e-be95-26655c3339b7
   2018-06-28T11:40:14.265+0200 I INDEX    [conn2] build index on: alignak-backend.livesynthesis properties: { v: 2, key: { _is_template: 1 }, name: "index_tpl", ns: "alignak-backend.livesynthesis" }
   2018-06-28T11:40:14.265+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.266+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.273+0200 I INDEX    [conn2] build index on: alignak-backend.livesynthesis properties: { v: 2, key: { host: 1, name: 1 }, name: "index_host", ns: "alignak-backend.livesynthesis" }
   2018-06-28T11:40:14.273+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.274+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.282+0200 I INDEX    [conn2] build index on: alignak-backend.livesynthesis properties: { v: 2, key: { name: 1 }, name: "index_name", ns: "alignak-backend.livesynthesis" }
   2018-06-28T11:40:14.282+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.284+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.292+0200 I STORAGE  [conn2] createCollection: alignak-backend.command with generated UUID: c81f9a99-858f-49c3-9d7d-4850b21d9efe
   2018-06-28T11:40:14.310+0200 I INDEX    [conn2] build index on: alignak-backend.command properties: { v: 2, key: { _updated: 1 }, name: "index_updated", ns: "alignak-backend.command" }
   2018-06-28T11:40:14.311+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.319+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.337+0200 I INDEX    [conn2] build index on: alignak-backend.command properties: { v: 2, key: { name: 1 }, name: "index_name", ns: "alignak-backend.command" }
   2018-06-28T11:40:14.337+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.338+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.340+0200 I STORAGE  [conn2] createCollection: alignak-backend.timeperiod with generated UUID: 3f172576-a646-4e9d-9a6a-93f6c3f822cd
   2018-06-28T11:40:14.358+0200 I INDEX    [conn2] build index on: alignak-backend.timeperiod properties: { v: 2, key: { _updated: 1 }, name: "index_updated", ns: "alignak-backend.timeperiod" }
   2018-06-28T11:40:14.358+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.359+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.375+0200 I INDEX    [conn2] build index on: alignak-backend.timeperiod properties: { v: 2, key: { name: 1 }, name: "index_name", ns: "alignak-backend.timeperiod" }
   2018-06-28T11:40:14.375+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.376+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.381+0200 I STORAGE  [conn2] createCollection: alignak-backend.servicegroup with generated UUID: e4a2d60f-f856-4414-8ff6-21ea0dab3490
   2018-06-28T11:40:14.401+0200 I INDEX    [conn2] build index on: alignak-backend.servicegroup properties: { v: 2, key: { _updated: 1 }, name: "index_updated", ns: "alignak-backend.servicegroup" }
   2018-06-28T11:40:14.401+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.402+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.413+0200 I INDEX    [conn2] build index on: alignak-backend.servicegroup properties: { v: 2, key: { name: 1 }, name: "index_name", ns: "alignak-backend.servicegroup" }
   2018-06-28T11:40:14.413+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.414+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.418+0200 I STORAGE  [conn2] createCollection: alignak-backend.host with generated UUID: b46f3b2e-f8fe-4bf1-99ea-9e34ba1e7752
   2018-06-28T11:40:14.437+0200 I INDEX    [conn2] build index on: alignak-backend.host properties: { v: 2, key: { _is_template: 1 }, name: "index_tpl", ns: "alignak-backend.host" }
   2018-06-28T11:40:14.437+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.438+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.450+0200 I INDEX    [conn2] build index on: alignak-backend.host properties: { v: 2, key: { _realm: 1, _is_template: 1 }, name: "index_realm", ns: "alignak-backend.host" }
   2018-06-28T11:40:14.450+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.451+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.459+0200 I INDEX    [conn2] build index on: alignak-backend.host properties: { v: 2, key: { _realm: 1, _is_template: 1, ls_state: 1, ls_state_type: 1, ls_downtimed: 1 }, name: "index_state_3", ns: "alignak-backend.host" }
   2018-06-28T11:40:14.459+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.460+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.480+0200 I INDEX    [conn2] build index on: alignak-backend.host properties: { v: 2, key: { name: 1 }, name: "index_name", ns: "alignak-backend.host" }
   2018-06-28T11:40:14.480+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.481+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.493+0200 I INDEX    [conn2] build index on: alignak-backend.host properties: { v: 2, key: { _realm: 1, _is_template: 1, ls_state: 1, ls_state_type: 1, ls_acknowledged: 1 }, name: "index_state_2", ns: "alignak-backend.host" }
   2018-06-28T11:40:14.493+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.494+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.503+0200 I INDEX    [conn2] build index on: alignak-backend.host properties: { v: 2, key: { _updated: 1 }, name: "index_updated", ns: "alignak-backend.host" }
   2018-06-28T11:40:14.503+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.504+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.515+0200 I INDEX    [conn2] build index on: alignak-backend.host properties: { v: 2, key: { _realm: 1, _is_template: 1, ls_state: 1, ls_state_type: 1 }, name: "index_state_1", ns: "alignak-backend.host" }
   2018-06-28T11:40:14.515+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.516+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.526+0200 I INDEX    [conn2] build index on: alignak-backend.host properties: { v: 2, key: { _realm: 1, _is_template: 1, ls_state: 1, ls_state_type: 1, active_checks_enabled: 1, passive_checks_enabled: 1 }, name: "index_state_4", ns: "alignak-backend.host" }
   2018-06-28T11:40:14.526+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.528+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.531+0200 I STORAGE  [conn2] createCollection: alignak-backend.user with generated UUID: 7207cda9-1980-4510-9c0d-8c7935ea5a7c
   2018-06-28T11:40:14.550+0200 I INDEX    [conn2] build index on: alignak-backend.user properties: { v: 2, key: { _is_template: 1 }, name: "index_tpl", ns: "alignak-backend.user" }
   2018-06-28T11:40:14.550+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.551+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.560+0200 I INDEX    [conn2] build index on: alignak-backend.user properties: { v: 2, key: { _updated: 1 }, name: "index_updated", ns: "alignak-backend.user" }
   2018-06-28T11:40:14.560+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.561+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.577+0200 I INDEX    [conn2] build index on: alignak-backend.user properties: { v: 2, key: { name: 1 }, name: "index_name", ns: "alignak-backend.user" }
   2018-06-28T11:40:14.577+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.579+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.582+0200 I STORAGE  [conn2] createCollection: alignak-backend.hostgroup with generated UUID: 269019f9-6557-43e4-a2a1-d71058bb13c1
   2018-06-28T11:40:14.602+0200 I INDEX    [conn2] build index on: alignak-backend.hostgroup properties: { v: 2, key: { _updated: 1 }, name: "index_updated", ns: "alignak-backend.hostgroup" }
   2018-06-28T11:40:14.603+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.604+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.619+0200 I INDEX    [conn2] build index on: alignak-backend.hostgroup properties: { v: 2, key: { name: 1 }, name: "index_name", ns: "alignak-backend.hostgroup" }
   2018-06-28T11:40:14.619+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.620+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.625+0200 I STORAGE  [conn2] createCollection: alignak-backend.history with generated UUID: faa52fc0-234c-40fb-996d-92574c494b8b
   2018-06-28T11:40:14.649+0200 I INDEX    [conn2] build index on: alignak-backend.history properties: { v: 2, key: { _created: 1 }, name: "index_created", ns: "alignak-backend.history" }
   2018-06-28T11:40:14.649+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.649+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.657+0200 I INDEX    [conn2] build index on: alignak-backend.history properties: { v: 2, key: { host_name: 1 }, name: "index_host_name", ns: "alignak-backend.history" }
   2018-06-28T11:40:14.657+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.658+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.676+0200 I INDEX    [conn2] build index on: alignak-backend.history properties: { v: 2, key: { host: 1 }, name: "index_host", ns: "alignak-backend.history" }
   2018-06-28T11:40:14.676+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.677+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.685+0200 I INDEX    [conn2] build index on: alignak-backend.history properties: { v: 2, key: { service_name: 1 }, name: "index_service_name", ns: "alignak-backend.history" }
   2018-06-28T11:40:14.685+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.686+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.693+0200 I INDEX    [conn2] build index on: alignak-backend.history properties: { v: 2, key: { _updated: 1 }, name: "index_updated", ns: "alignak-backend.history" }
   2018-06-28T11:40:14.693+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.695+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.703+0200 I INDEX    [conn2] build index on: alignak-backend.history properties: { v: 2, key: { service: 1 }, name: "index_service", ns: "alignak-backend.history" }
   2018-06-28T11:40:14.703+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.704+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.717+0200 I INDEX    [conn2] build index on: alignak-backend.history properties: { v: 2, key: { host_name: 1, service_name: 1 }, name: "index_host_service_name", ns: "alignak-backend.history" }
   2018-06-28T11:40:14.717+0200 I INDEX    [conn2] 	 building index using bulk method; build may temporarily use up to 500 megabytes of RAM
   2018-06-28T11:40:14.718+0200 I INDEX    [conn2] build index done.  scanned 0 total records. 0 secs
   2018-06-28T11:40:14.835+0200 I STORAGE  [conn2] createCollection: alignak-backend.userrestrictrole with generated UUID: 1aca4da1-c9f6-4f4c-97db-a7e4abf116e0

