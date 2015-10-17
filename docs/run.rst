.. _run:

Run
===

Production mode
---------------

First create a file anywhere on your system, named 'alignakbackend.py' and containing::

    from alignak_backend.app import app

You can use many possibilities, but we suggest you use uwsgi and start it in the same directory as the file created previously.

With socket (+ nginx / apache in frontal)::

   uwsgi -s /tmp/uwsgi.sock -w alignakbackend:app --enable-threads

With direct http port::

   uwsgi -w alignakbackend:app --socket 0.0.0.0:80 --protocol=http --enable-threads


Alignak-backend runs on port 80 like specified in arguments, so use::

    http://ip/

Developer mode
--------------

To run in developper mode (mean with few connections), you can start with command::

    alignak_backend

Alignak-backend run on port 5000, so use::

    http://ip:5000/
