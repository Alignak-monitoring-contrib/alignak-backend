#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of influxdb
"""


def get_name(friendly=False):
    """Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    if friendly:  # pragma: no cover
        return "InfluxDB connection"
    return 'influxdb'


def get_doc():  # pragma: no cover
    """Get documentation of this resource

    :return: rst string
    :rtype: str
    """
    return """
    The ``influxdb`` model contains information to provide the monitored system performance
    data to InfluxDB.

    The Alignak backend will use those information to connect to an Influx DB and send the
    timeseries data. If you are using a StatsD daemon as a front-end of the InfluxDB
    create a relation with a StatsD data model instance. To make the Alignak backend
    create some Grafana panels for the metrics sent to Graphite create a relation with
    a Grafana data model instance.
    """


def get_schema():
    """Schema structure of this resource

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'schema': {
            'name': {
                "title": "Influx connection name",
                "comment": "Unique InfuxDB connection name",
                'type': 'string',
                'required': True,
                'empty': False,
                'unique': True,
            },
            'address': {
                "title": "Server address",
                "comment": "",
                'type': 'string',
                'required': True,
                'empty': False,
            },
            'port': {
                "title": "Server port",
                "comment": "",
                'type': 'integer',
                'default': 8086,
                'empty': False,
            },
            'database': {
                "title": "Database name",
                "comment": "",
                'type': 'string',
                'required': True,
                'empty': False,
                'default': 'alignak'
            },
            'login': {
                "title": "Database login username",
                "comment": "",
                'type': 'string',
                'required': True,
                'empty': False,
            },
            'password': {
                "title": "Database login password",
                "comment": "",
                'type': 'string',
                'required': True,
                'empty': False,
            },
            'prefix': {
                "title": "Metrics prefix",
                "comment": "Prefix that will be prepended to the metrics sent to this TS DB.",
                'type': 'string',
                'default': '',
            },
            'grafana': {
                "title": "Grafana relation",
                "comment": "If set, the Alignak backend will use this Grafana relation for "
                           "the metrics sent to the Influx DB. It will create/update the "
                           "Grafana panels accordindgly.",
                'type': 'objectid',
                'data_relation': {
                    'resource': 'grafana',
                    'embeddable': True
                },
                'nullable': True,
                'default': None
            },
            'statsd': {
                "title": "StatsD relation",
                "comment": "If set, the Alignak backend will use this StatsD relation for "
                           "the metrics sent to the Influx DB.",
                'type': 'objectid',
                'data_relation': {
                    'resource': 'statsd',
                    'embeddable': True
                },
                'nullable': True,
                'default': None
            },

            # Realm
            '_realm': {
                "title": "Realm",
                "comment": "Realm this element belongs to.",
                'type': 'objectid',
                'data_relation': {
                    'resource': 'realm',
                    'embeddable': True
                },
                'required': True,
            },
            '_sub_realm': {
                "title": "Sub-realms",
                "comment": "Is this element visible in the sub-realms of its realm?",
                'type': 'boolean',
                'default': True
            },

            # Users CRUD permissions
            '_users_read': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'user',
                        'embeddable': True,
                    }
                },
            },
            '_users_update': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'user',
                        'embeddable': True,
                    }
                },
            },
            '_users_delete': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'user',
                        'embeddable': True,
                    }
                },
            },
        }
    }
