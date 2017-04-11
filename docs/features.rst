.. _features:

Features
========

Authentication in the backend
-----------------------------

The Alignak backend requires a user authentication. To access any backend enpoint, you need to provide the *token* associated to your user account.

To get your backend *token*, POST on *http://127.0.0.1:5000/login* with your credentials:

* *username*: xxx
* *password*: xxx

and the response will provide the token to use in the next requests.


Rights management
-----------------

There is a user's rights management feature in the Alignak backend. This feature allows to easily create a frontend with user rights ;)

Right to all data without restrictions in a realm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You have the possibility to give access (read, create, update and delete) to all resources without any restrictions for a user (the same as the *admin* account)

In the *user* resource, set:

* *back_role_super_admin* to *True*
* *_realm* to the realm identifier you want to give access to
* *_sub_realm* to *True* if you want to target this realm and its children realms or *False* to target only this realm


Rights to a resource in a realm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each resource (endpoint) can have its own rights for a logged-in user. To set some CRUD rights on a resource, add a *userrestrictrole* for each crud (create, read, update, delete) and concerned resource:

* *user*: identifier of the user
* *realm*: identifier of the realm where you want to set the rights
* *sub_realm* to *True* if you want have to set the rights for all the children of the realm
* *resource*: is the name of the targeted resource
* *crud*: concerned right

To set the read-only rights on all the commands, use `command` as a resource and `['read']` as *crud*.

To set the full-access rights on all the hosts, use `host` as a resource and `['create', 'read', 'update', 'delete']` as *crud*.

For each resource and each crud you need to define a *userrestrictrole*.


Rights to an object of a resource in a realm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's even possible to give access to a specific object of a resource.

As an example, you have 3 hosts in the realm *reamlxxx* and you want to give a read-only access to host *host 1*. You can do this with *custom* right in *userrestrictrole* (see previous point and replace the *read* right with *custom*).

When a *custom* right is defined, you need to add the user identifier in the object itself. So in the host, set the field: *_users_read* to the user identifier.

**Remember** the realm identifier of the resource (*realm* or *_realm* according the resource) must be the same as the realm of the *userrestrictrole* or in a children of the realm if *sub_realm* is *True*


Templating system
-----------------

The alignak backend implements a templating system to ease the resource creation. This feature allows to easily create some elements based upon pre-defined templates.

Resources using the templating system
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The resources using the backend templating system are:

   * host
   * service
   * user


Creating templates
~~~~~~~~~~~~~~~~~~

To use the Alignak backend templating system, you need to have templates defined in your backend. For this, simply create an object (*host*, *service* or *user*) and specify that it is a template by setting its *_is_template* property to True. It is as simple as creating an *host* and you just need to add *_is_template = True* in the provided data.

A *service* template may be linked to an host template, so you must also specify an host template identifier when you create the service template. If no host template is specified, the service template will be automatically linked to the `dummy` host that exists in the backend.

**Note** that a template can also use some other templates making it easy to have several levels of inheritance.


Use simple template system
~~~~~~~~~~~~~~~~~~~~~~~~~~

When you create a new object (*host*, *service* or *user*) in the backend you can specify the list of templates it will use with the *_templates* property. Once created, this new object will automatically be linked to the corresponding templates and it will inherit all its templates properties. Creating a new *host* with all its check, notification, ... properties is as easy as providing its name and templates on creation!

When a field is modified in a template, all the elements linked to this template will automatically get the modifications. When a field is modified in a templated element, this modification will take precedence over the template value.


Powerful template system
~~~~~~~~~~~~~~~~~~~~~~~~

Creating hosts and all their services is really easy with the backend templating system. Let's imagine that we already created those templates:
::

    nrpe_host (host template)
            |------------> nrpe_check_cpu (service template)
            |------------> nrpe_check_mem (service template)
            |------------> nrpe_check_load (service template)

All 3 service templates were created with a link to the *nrpe_host* template.


Now, if you create a new host with:
    * *_templates*: [*id_of_nrpe_host_template*]
    * *name*: 'new_host'

The Alignak backend will create the host **and** all its services at once!

We now have:
::

    nrpe_host (host template)
            |------------> nrpe_check_cpu (service template)
            |------------> nrpe_check_mem (service template)
            |------------> nrpe_check_load (service template)

    new_host(host)
            |------------> check_cpu (service)
            |------------> check_mem (service)
            |------------> check_load (service)



Timeseries databases
--------------------

Introduction
~~~~~~~~~~~~

To store the metrics, we need to configure Carbon/Graphite or/and InfluxDB.

These timeseries interfaces can be defined by realm + sub realm, and so you can have multiple
timeseries database in a realm.

Carbon / Graphite
~~~~~~~~~~~~~~~~~

For Carbon/Graphite, use resource _graphite_, composed with information:

* *carbon_address*: address of carbon (IP, DNS),
* *carbon_port*: port of carbon, default 2004,
* *graphite_address*: address of graphite (IP, DNS),
* *graphite_port*: port of graphite, default 8080,
* *prefix*: a prefix to use in carbon for our data
* *grafana*: id of grafana

Curl example::

    curl -X POST -H "Content-Type: application/json"
    --user "1442583814636-bed32565-2ff7-4023-87fb-34a3ac93d34c:"
    -H "Cache-Control: no-cache" -d '[
	{
        "name": "graphite_001",
        "carbon_address": "192.168.0.200",
        "carbon_port": 2004,
        "graphite_address": "192.168.0.200",
        "graphite_port": 8080,
        "prefix": "001.a",
        "grafana": "5864c1c98bde9c8bd787a779",
        "_realm": "5864c1c98bde9c8bd787a781",
        "_sub_realm": true
	}
    ]' "http://192.168.0.10:5000/graphite"

InfluxDB
~~~~~~~~

For InfluxDB, use resource _influxdb_:

* *address*: address of influxdb (IP, DNS),
* *port*: port of influxdb, default 8086,
* *database*: database name in influxdb
* *login*: login to access to influxdb
* *password*: password to access to influxdb
* *grafana*: id of grafana

Curl example::

    curl -X POST -H "Content-Type: application/json"
    --user "1442583814636-bed32565-2ff7-4023-87fb-34a3ac93d34c:"
    -H "Cache-Control: no-cache" -d '[
	{
        "name": "influx_001",
        "address": "192.168.0.200",
        "port": 8086,
        "database": "alignak",
        "login": "alignak",
        "password": "mypass",
        "grafana": "5864c1c98bde9c8bd787a779",
        "_realm": "5864c1c98bde9c8bd787a781",
        "_sub_realm": true
	}
    ]' "http://192.168.0.10:5000/influxdb"

Manage retention
~~~~~~~~~~~~~~~~

The timeseries information are stored in the backend (like retention) when the timeserie database
is not available. A scheduled cron (internal in the Backend) is used to push the retention in the
timeserie database when become available again, so need to activate this cron, but only on one
Backend in case you have a cluster of Backend (many backends).

Activate in configuration file with::

    "SCHEDULER_TIMESERIES_ACTIVE": true,

IMPORTANT: you can't have more than one timeserie database (carbon / influxdb) linked to a grafana
on each realm!

Statsd
~~~~~~

If you want use Statsd to put metrics and statsd will manage the metrics with Graphite / InfluxDB,
you can define a statsd server in endpoint *statsd* and add this id in items of *graphite* /
*influxdb* endpoint. It can be useful in case you manage passive checks.


Grafana: the dashboard/graph tool
---------------------------------

The backend can create the dashboards (one per host) and the graphs (one per host and one per
services in the dashboard of the host related).

We need define grafana server and activate the _cron_ on one Backend in case you have
a cluster of Backend (many backends).

For that, activate it in configuration file::

    "SCHEDULER_GRAFANA_ACTIVE": true,

Define the Grafana with resource _grafana_:

* *address*: address of grafana (IP, DNS),
* *port*: port of grafana, default 3000
* *apikey*: the API KEY in grafana with right *admin*
* *timezone*: the timezone used, default _browser_
* *refresh*: refresh time of dashboards, default _1m_ (all 1 minutes)

Curl example::

    curl -X POST -H "Content-Type: application/json"
    --user "1442583814636-bed32565-2ff7-4023-87fb-34a3ac93d34c:"
    -H "Cache-Control: no-cache" -d '[
	{
        "name": "influx_001",
        "address": "192.168.0.11",
        "port": 3000,
        "apikey": "43483998029a049494b536aa684398439d",
        "_realm": "5864c1c98bde9c8bd787a781",
        "_sub_realm": true
	}
    ]' "http://192.168.0.10:5000/grafana"


You can create many grafana in the backend, for example a different grafana for each realm. This
possibility can be used to give different access to grafana to different users (with different
grafana server or with same grafana server but with different organizations and so different
API KEYS).

It's possible to force to regenerate all dashboards in grafana (works only from localhost):
::

    curl "http://127.0.0.1:5000/cron_grafana?forcegenerate=1"


Special parameters for livesynthesis
------------------------------------

When you get a livesynthesis item, you can use 2 special parameters:

* *history=1*: get the history in field *history* with all history for each last minutes
* *concatenation=1*: get the livesynthesis data merged with livesynthesis of sub-realm. If you use with parameter with *history* parameter, the history will be merged with livesynthesis history of sub-realm.

