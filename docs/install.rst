.. _install:

Installation
============

Requirements
------------

MongoDB
~~~~~~~

To use this Alignak backend, you first need to install and run MongoDB_

.. _MongoDB: http://docs.mongodb.org/manual/

As an excerpt of the MongoDB installation documentation, this script will install the Mongo DB community edition on a Linux Ubuntu 16 (https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/)::

    sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2930ADAE8CAF5059EE73BB4B58712A2291FA4AD5
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.6 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.6.list
    sudo apt-get update
    sudo apt-get install -y mongodb-org
    sudo service mongod start


.. warning:: Check for your specific Unix/Linux distribution in the `MongoDB_` installation documentation.


uWSGI
~~~~~

We recommend to use uWSGI as an application server for the Alignak backend and we provide a python pip installer that has `uwsgi` as a requirement.

If you prefer using your Unix/Linux ditribution packaging to install uWSGI and the alignak backend (not yet packaged... help needed for this), please refer to your distribution packages for installing. You will also need to install the uWSGI Python plugin.

As an example on Debian::

    sudo apt-get install uwsgi uwsgi-plugin-python


.. warning:: If you get some errors with the plugins, you will need to set some options in the alignak backend */usr/local/etc/alignak-backend/uwsgi.ini* configuration file. See this configuration file commented accordingly.

Install with pip
----------------

**Note** that the recommended way for installing on a production server is mostly often to use the packages existing for your distribution.

Nevertheless, the pip installation provides:
- a startup script using an uwsgi server,
- for FreeBSD users, an rc.d sample script
- for system based systems (Debian, CentOS), an alignak-backend service unit example.

All this stuff is available in the repository *bin* directory.

For freeBSD system service
~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    # Enable the system service
    echo 'alignak_backend_enable="YES"' >> /etc/rc.conf
    # Declare the configuration file
    echo 'alignak_backend_config="/root/git/DCS_IPM/config/alignak-backend/settings.json"' >> /etc/rc.conf
    # Enable uwsgi log
    echo 'alignak_backend_log="YES"' >> /etc/rc.conf
    # Define network interface
    echo 'alignak_backend_host="0.0.0.0"' >> /etc/rc.conf
    echo 'alignak_backend_port="5000"' >> /etc/rc.conf
    # # # Send uWsgi metrics to Graphite
    echo 'alignak_backend_metrics="YES"' >> /etc/rc.conf
    echo 'alignak_backend_carbon="127.0.0.1:2003 --carbon-root uwsgi -s /tmp/uwsgi.sock"' >> /etc/rc.conf


    # Check all the available configuration variables in the /usr/local/etc/rc.d/alignak-backend file!


    # Alignak-backend
    service alignak-backend status
    service alignak-backend stop
    service alignak-backend start

With pip
~~~~~~~~

You can install with pip::

    pip install alignak_backend


The required Python modules are automatically installed if not they are not yet present on your system.

**Note** that if you need to `sudo pip install alignak-backend` on your system, you will probably need to set proper user's rights on some folders created by the installer. The concerned folders are */usr/local/etc/alignak-backend* and */usr/local/var/log/alignak-backend*.

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
