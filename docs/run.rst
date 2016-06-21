.. _run:

Run
===

Production mode
---------------

First create a file anywhere on your system, named 'alignakbackend.py' and containing::

    from alignak_backend.app import app

You can use many possibilities, but we suggest you use uwsgi and start it in the same directory as the file created previously.

With socket (+ nginx / apache in frontal)::

   uwsgi -s /tmp/uwsgi.sock -w alignakbackend:app --enable-threads -p 4

With direct http port::

   uwsgi -w alignakbackend:app --socket 0.0.0.0:80 --protocol=http --enable-threads -p 4


Alignak-backend runs on port 80 like specified in arguments, so use::

    http://ip/

Developer mode
--------------

To run in developper mode (mean with few connections), you can start with command::

    alignak_backend

On start, some useful information are printed on the console::

      $ alignak_backend
      --------------------------------------------------------------------------------
      Alignak_Backend, version 0.2.4
      Copyright (c) 2015 - Alignak team
      License GNU Affero General Public License, version 3
      --------------------------------------------------------------------------------
      Doc: https://github.com/Alignak-monitoring-contrib/alignak-backend
      Release notes: Alignak REST Backend
      --------------------------------------------------------------------------------
      Configuration read from file(s): ['/etc/alignak_backend/settings.json']
      Application settings: {'MONGO_PORT': '27017', 'RATE_LIMIT_POST': 'None', 'X_HEADERS': 'Authorization, If-Match, X-HTTP-Method-Override, Content-Type', 'X_DOMAINS': '*', 'MONGO_DBNAME': 'alignak-backend', 'RATE_LIMIT_GET': 'None', 'MONGO_HOST': 'localhost', 'DEBUG': 'False', 'RATE_LIMIT_PATCH': 'None', 'PAGINATION_LIMIT': '100', 'RATE_LIMIT_DELETE': 'None'}


Alignak-backend run on port 5000, so use::

    http://ip:5000/
