Alignak Backend
===============

*Python Eve REST Backend for Alignak monitoring framework*

.. image:: https://travis-ci.org/Alignak-monitoring-contrib/alignak-backend.svg?branch=develop
    :target: https://travis-ci.org/Alignak-monitoring-contrib/alignak-backend
    :alt: Develop branch build status

.. image:: https://landscape.io/github/Alignak-monitoring-contrib/alignak-backend/develop/landscape.svg?style=flat
    :target: https://landscape.io/github/Alignak-monitoring-contrib/alignak-backend/develop
    :alt: Development code static analysis

.. image:: https://coveralls.io/repos/Alignak-monitoring-contrib/alignak-backend/badge.svg?branch=develop&service=github
    :target: https://coveralls.io/github/Alignak-monitoring-contrib/alignak-backend?branch=develop
    :alt: Development code coverage

.. image:: http://readthedocs.org/projects/alignak-backend/badge/?version=latest
    :target: http://alignak-backend.readthedocs.io/en/latest/?badge=latest
    :alt: Latest documentation Status

.. image:: http://readthedocs.org/projects/alignak-backend/badge/?version=develop
    :target: http://alignak-backend.readthedocs.io/en/latest/?badge=develop
    :alt: Development documentation Status

.. image:: https://badge.fury.io/py/alignak_backend.svg
    :target: https://badge.fury.io/py/alignak_backend
    :alt: Most recent PyPi version

.. image:: https://img.shields.io/badge/IRC-%23alignak-1e72ff.svg?style=flat
    :target: http://webchat.freenode.net/?channels=%23alignak
    :alt: Join the chat #alignak on freenode.net

.. image:: https://img.shields.io/badge/License-AGPL%20v3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0
    :alt: License AGPL v3


Short description
-----------------

This package is an Alignak Backend.

It is used to:

* manage monitoring configuration (hosts, services, contacts, timeperiods...)

    end user (WebUI, alignak-backend-cli, python/php client, curl command line,...) can get, add, edit monitoring configurations elements
    inner templating system to easily create new hosts, services, users, ...
    Alignak gets this configuration when its arbiter module starts

* manage retention

    Alignak saves and loads retention information for checks/hosts/services from the backend

* manage the monitoring live state

    Alignak add/update states for hosts and services
    end user (webui, command line...) can get these information

* manage the metrics from the checks performance data

    Alignak backend automatically send metrics to Graphite / InfluxDB timeseries databases
    Alignak backend automatically creates Grafana panels for hosts / services metrics


Installation
------------

From PyPI
~~~~~~~~~
To install the package from PyPI:
::

   sudo pip install alignak-backend


From source files
~~~~~~~~~~~~~~~~~
To install the package from the source files:
::

   git clone https://github.com/Alignak-monitoring-contrib/alignak-backend
   cd alignak-backend
   sudo pip install .


Documentation
-------------

The Alignak backend documentation is available on `Read the docs <http://alignak-backend.readthedocs.io/en/latest/?badge=develop>`_ or in the */docs* folder of this repository.

To build the doc:
::

    cd docs
    python models_to_rst.py
    make clear
    make html


Release strategy
----------------

Alignak backend and its *satellites* (backend client, and backend import tools) must all have the
same features level. As of it, take care to install the same minor version on your system to
ensure compatibility between all the packages. Use 0.4.x version of Backend import and Backend
client with a 0.4.x version of the Backend.

Bugs, issues and contributing
-----------------------------

Please report any issue using the project `issues page <https://github.com/Alignak-monitoring-contrib/alignak-backend/issues>`_.

