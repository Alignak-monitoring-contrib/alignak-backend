#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of grafana
"""


def get_name(friendly=False):
    """Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    if friendly:  # pragma: no cover
        return 'Grafana connection'
    return 'grafana'


def get_doc():  # pragma: no cover
    """Get documentation of this resource

    :return: rst string
    :rtype: str
    """
    return """
    The ``grafana`` model contains information to manage Grafana panels for the monitored
    system performance data.

    The Alignak backend will use those information to create/update Grafana panels for each
    managed timeseries. A Grafana dashboard is created automatically for each host in the
    monitored system. A panel is created automatically in this dashboard for each metric
    of the concerned host.
    """


def get_schema():
    """Schema structure of this resource

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'schema': {
            'schema_version': {
                'type': 'integer',
                'default': 1,
            },
            'name': {
                'schema_version': 1,
                'title': 'Grafana connection name',
                'comment': 'Unique Grafana connection name',
                'type': 'string',
                'required': True,
                'empty': False,
                'unique': True,
            },
            'address': {
                'schema_version': 1,
                'title': 'Server address',
                'comment': '',
                'type': 'string',
                'required': True,
                'empty': False,
            },
            'port': {
                'schema_version': 1,
                'title': 'Server port',
                'comment': '',
                'type': 'integer',
                'empty': False,
                'default': 3000
            },
            'apikey': {
                'schema_version': 1,
                'title': 'Grafana API key',
                'comment': 'This API key is defined in the Grafana administration Web '
                           'interface and it must have administrator rights in your '
                           'Grafana organization.',
                'type': 'string',
                'required': True,
                'empty': False,
            },
            'timezone': {
                'schema_version': 1,
                'title': 'Grafana timezone',
                'comment': 'This timezone is used, if needed, to define the Alignak Timezone.',
                'type': 'string',
                'empty': False,
                'default': 'browser'
            },
            'refresh': {
                'schema_version': 1,
                'title': 'Dashboard refresh period',
                'comment': 'The default Grafana dashboard refresh time.',
                'type': 'string',
                'empty': False,
                'default': '1m'
            },
            'ssl': {
                'schema_version': 1,
                'title': 'SSL',
                'comment': 'Set this property if your Grafana requires SSL connection.',
                'type': 'boolean',
                'default': False
            },

            # Realm
            '_realm': {
                'schema_version': 1,
                'title': 'Realm',
                'comment': 'Realm this element belongs to.',
                'type': 'objectid',
                'data_relation': {
                    'resource': 'realm',
                    'embeddable': True
                },
                'required': True,
            },
            '_sub_realm': {
                'schema_version': 1,
                'title': 'Sub-realms',
                'comment': 'Is this element visible in the sub-realms of its realm?',
                'type': 'boolean',
                'default': True
            },

            # Users CRUD permissions
            '_users_read': {
                'schema_version': 1,
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
                'schema_version': 1,
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
                'schema_version': 1,
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'user',
                        'embeddable': True,
                    }
                },
            },
        },
        'schema_deleted': {}
    }
