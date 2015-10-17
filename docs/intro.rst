.. _intro:

Introduction
============

This project is a Alignak Backend.
It is used to:

* manage configuration (hosts, services, contacts, timeperiods...)

    * end user (webui, command line...) can get and add configurations elements
    * Alignak gets its configuration from the backend when the arbiter module is starting

* manage retention

    * Alignak loads and saves retention information in the backend for checks/hosts/services

* manage live states

    * Alignak adds/updates hosts and services states in the backend
    * end user (webui, command line...) can get this information
