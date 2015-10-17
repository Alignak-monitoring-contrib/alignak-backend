.. _install:

Installation
============

Requirements
------------

To use this backend, you first need to install and run MongoDB_

.. _MongoDB: http://docs.mongodb.org/manual/

Install with pip
----------------

With pip
~~~~~~~~

You can install with pip::

    pip install alignak_backend


From source
~~~~~~~~~~~

You can install it from source::

    git clone https://github.com/Alignak-monitoring/alignak-backend
    cd alignak-backend
    pip install .


For contributors
~~~~~~~~~~~~~~~~

If you want to hack into the codebase (e.g for future contribution), just install like this::

    pip install -e .


Install from source without pip
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
