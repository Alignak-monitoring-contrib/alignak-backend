Alignak Backend
===============

*Python Eve REST Backend for Alignak monitoring framework*

Build status (stable release)
----------------------------------------

.. image:: https://travis-ci.org/Alignak-monitoring-contrib/alignak-backend.svg?branch=master
    :target: https://travis-ci.org/Alignak-monitoring-contrib/alignak-backend

.. image:: https://readthedocs.org/projects/alignak-backend/badge/?version=latest
  :target: http://alignak-backend.readthedocs.org/en/latest/?badge=latest
  :alt: Documentation Status


Build status (development release)
----------------------------------------

.. image:: https://travis-ci.org/Alignak-monitoring-contrib/alignak-backend.svg?branch=develop
    :target: https://travis-ci.org/Alignak-monitoring-contrib/alignak-backend

.. image:: https://readthedocs.org/projects/alignak-backend/badge/?version=develop
  :target: http://alignak-backend.readthedocs.org/en/develop/?badge=develop
  :alt: Documentation Status


Documentation
----------------------------------------

You can find online documentation on `Read The Docs <http://alignak-backend.readthedocs.org>`_.

Short description
-------------------

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


Bugs, issues and contributing
----------------------------------------

Please report any issue using the project GitHub repository: <https://github.com/Alignak-monitoring-contrib/alignak-backend/issues>`_.

License
----------------------------------------

Alignak Backend is available under the `GPL version 3 <http://opensource.org/licenses/GPL-3.0>`_.

