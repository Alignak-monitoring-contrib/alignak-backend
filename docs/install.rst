.. _install:

Installation
============


Install from pip
----------------

You can install with pip::

    pip install alignak_backend

**This not work for the moment because not yet released**

Install from source
-------------------

You can install it from source::

    git clone https://github.com/Alignak-monitoring/alignak-backend
    cd alignak-backend
    pip install .


Install for contributors
------------------------

If you want to hack into the codebase (e.g for future contribution), just install like this::

    pip install -e .


Install with source without pip
-------------------------------

If you are on Debian::

    apt-get -y install python python-dev python-pip git


Get the project sources::

    git clone https://github.com/Alignak-monitoring/alignak-backend


Install python prerequisites::

    pip install -r alignak-backend/requirements.txt


And install::

    cd alignak-backend
    python setup.py install


Run alignak_backend
-------------------

To run the backend, you have only to do::

    alignak_backend run

URL of API REST
---------------

Alignak-backend run on port 5000, so use::

    http://ip:5000/
