.. _run:

Run
===

Production mode
---------------

First create a file anywhere on your system, with name 'alignakbackend.py' and with the content::

    from alignak_backend.app import app

You can use many possibilities, we suggest you with uwsgi and start it in sme directory of file created previously.

With socket (+ nginx / apache in frontal)::

   uwsgi -s /tmp/uwsgi.sock -w alignakbackend:app --enable-threads

With http port directly::

   uwsgi -w alignakbackend:app --socket 0.0.0.0:80 --protocol=http --enable-threads


Alignak-backend run on port 80 like specified in arguments, so use::

    http://ip/

Developer mode
--------------

To run in developper mode (mean with few connections), you can start with command::

    alignak_backend

Alignak-backend run on port 5000, so use::

    http://ip:5000/
