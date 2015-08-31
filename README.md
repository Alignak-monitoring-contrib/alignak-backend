# Alignak-backend

[![Build Status](https://travis-ci.org/Alignak-monitoring-contrib/alignak-backend.svg?branch=master)](https://travis-ci.org/Alignak-monitoring-contrib/alignak-backend)

# Documentation

Documentation is available here: [http://alignak-backend.readthedocs.org](http://alignak-backend.readthedocs.org)

# Short description

This project is a Alignak Backend.
It is used to:

* manage configuration (hosts, services, contacts, timeperiods...)

    * end user (webui, command line...) can get and add configurations elements
    * Alignak get this configuration when start arbiter module

* manage retention

    * Alignak load and save retention information about checks/hosts/services

* manage live states

    * Alignak add/update states of hosts and services
    * end user (webui, command line...) can get these information

