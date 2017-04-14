#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of livestate synthesis
"""


def get_name(friendly=False):
    """Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    if friendly:  # pragma: no cover
        return "Alignak live state synthesis"
    return 'livesynthesis'


def get_doc():  # pragma: no cover
    """Get documentation of this resource

    :return: rst string
    :rtype: str
    """
    return """
    The ``livesynthesis`` model is maintained by the Alignak to get an easy overview of
    the monitored system state.

    For hosts and services, the live synthesis stores values computed from the real
    live state, each time an element state is updated:
    - a counter containing the number of host/service in each state
    - a counter containing the number of host/service acknowledged
    - a counter containing the number of host/service in downtime
    - a counter containing the number of host/service flapping
    - the maximum business impact of the host/service in the state
    """


def get_schema():
    """Schema structure of this resource

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'schema': {
            'hosts_total': {
                "title": "Hosts count",
                'type': 'integer',
                'default': 0,
            },
            'hosts_up_hard': {
                "title": "Hosts Up hard",
                'type': 'integer',
                'default': 0,
            },
            'hosts_up_soft': {
                "title": "Hosts Up soft",
                'type': 'integer',
                'default': 0,
            },
            'hosts_down_hard': {
                "title": "Hosts Down hard",
                'type': 'integer',
                'default': 0,
            },
            'hosts_down_soft': {
                "title": "Hosts Down soft",
                'type': 'integer',
                'default': 0,
            },
            'hosts_unreachable_hard': {
                "title": "Hosts Unreachable hard",
                'type': 'integer',
                'default': 0,
            },
            'hosts_unreachable_soft': {
                "title": "Hosts Unreachable soft",
                'type': 'integer',
                'default': 0,
            },
            'hosts_acknowledged': {
                "title": "Hosts ackowledged",
                'type': 'integer',
                'default': 0
            },
            'hosts_in_downtime': {
                "title": "Hosts in downtime",
                'type': 'integer',
                'default': 0
            },
            'hosts_flapping': {
                "title": "Hosts flapping",
                'type': 'integer',
                'default': 0
            },
            'hosts_business_impact': {
                "title": "Hosts business impact",
                'type': 'integer',
                'default': 0
            },

            'services_total': {
                "title": "Services count",
                'type': 'integer',
                'default': 0,
            },
            'services_ok_hard': {
                "title": "Services Ok hard",
                'type': 'integer',
                'default': 0,
            },
            'services_ok_soft': {
                "title": "Services Ok soft",
                'type': 'integer',
                'default': 0,
            },
            'services_warning_hard': {
                "title": "Services Warning hard",
                'type': 'integer',
                'default': 0,
            },
            'services_warning_soft': {
                "title": "Services Warning soft",
                'type': 'integer',
                'default': 0,
            },
            'services_critical_hard': {
                "title": "Services Critical hard",
                'type': 'integer',
                'default': 0,
            },
            'services_critical_soft': {
                "title": "Services Criticl soft",
                'type': 'integer',
                'default': 0,
            },
            'services_unknown_hard': {
                "title": "Services Unknown hard",
                'type': 'integer',
                'default': 0,
            },
            'services_unknown_soft': {
                "title": "Services Unknown soft",
                'type': 'integer',
                'default': 0,
            },
            'services_unreachable_hard': {
                "title": "Services Unreachable hard",
                'type': 'integer',
                'default': 0,
            },
            'services_unreachable_soft': {
                "title": "Services Unreachable soft",
                'type': 'integer',
                'default': 0,
            },
            'services_acknowledged': {
                "title": "Services acknowledged",
                'type': 'integer',
                'default': 0
            },
            'services_in_downtime': {
                "title": "Services in downtime",
                'type': 'integer',
                'default': 0
            },
            'services_flapping': {
                "title": "Services flapping",
                'type': 'integer',
                'default': 0
            },
            'services_business_impact': {
                "title": "Services business impact",
                'type': 'integer',
                'default': 0
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
        }
    }
