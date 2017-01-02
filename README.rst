Alignak Backend
===============

*Python Eve REST Backend for Alignak monitoring framework*

.. image:: https://travis-ci.org/Alignak-monitoring-contrib/alignak-backend.svg?branch=develop
    :target: https://travis-ci.org/Alignak-monitoring-contrib/alignak-backend
    :alt: Develop branch build status

.. image:: https://readthedocs.org/projects/alignak-backend/badge/?version=latest
    :target: http://alignak-backend.readthedocs.org/en/latest/?badge=latest
    :alt: Latest documentation Status

.. image:: https://readthedocs.org/projects/alignak-backend/badge/?version=develop
    :target: http://alignak-backend.readthedocs.org/en/develop/?badge=develop
    :alt: Development documentation Status

.. image:: https://badge.fury.io/py/alignak_backend.svg
    :target: https://badge.fury.io/py/alignak_backend
    :alt: Last PyPi version

.. image:: https://img.shields.io/badge/License-AGPL%20v3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0
    :alt: License AGPL v3


Short description
-----------------

This package is an Alignak Backend.

It is used to:

* manage configuration (hosts, services, contacts, timeperiods...)

   * end user (webui, command line...) can get and add configurations elements
   * Alignak gets this configuration when its arbiter module starts

* manage retention

   * Alignak load and save retention information for checks/hosts/services

* manage live states

   * Alignak add/update states for hosts and services
   * end user (webui, command line...) can get these information


Release strategy
----------------

Alignak backend and its *satellites* (backend client, and backend import tools) must all have the
same features level. As of it, take care to install the same minor version on your system to
ensure compatibility between all the packages. Use 0.4.x version of Backend import and Backend
client with a 0.4.x version of the Backend.

The current version of Alignak backend is 0.5.5.

This version is published on PyPi and can be installed with ``pip install alignak_backend``.

It contains:

- compatibility with new upcoming Alignak 1.0 version

- modified data model:
    - live state in the host/service elements
    - user preferences in the user data model
    - unreachable managed for the hosts and services

Previous versions:

- 0.4: version compatible with Alignak version 0.2 (objects serialization and uuid)

- 0.3: version compatible with Alignak version 0.1

Bugs, issues and contributing
-----------------------------

Please report any issue using the project `issues page <https://github.com/Alignak-monitoring-contrib/alignak-backend/issues>`_.

