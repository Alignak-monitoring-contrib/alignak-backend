Alignak-backend
=================

.. image:: https://travis-ci.org/Alignak-monitoring-contrib/alignak-backend.svg?branch=master
    :target: https://travis-ci.org/Alignak-monitoring-contrib/alignak-backend

Documentation
-------------------

Documentation is available on `Read the docs <http://alignak-backend.readthedocs.org/>`_.

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
