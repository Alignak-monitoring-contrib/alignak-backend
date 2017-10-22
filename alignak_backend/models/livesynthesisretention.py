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
        return 'LS history'
    return 'livesynthesisretention'


def get_doc():  # pragma: no cover
    """Get documentation of this resource

    :return: rst string
    :rtype: str
    """
    return """
    The ``livesynthesisretention`` model is a cache used internally by the backend to store the
    last computed live synthesis information. If the live synthesis history is configured,
    a count of ``SCHEDULER_LIVESYNTHESIS_HISTORY`` live synthesis elements will be store in the
    live synthesis retention data model.
    """


def get_schema():
    """Schema structure of this resource

    For an element type and a state, store values computed from the hosts/services livestate:
    - a counter containing the number of element_type in the state
    - a percentage of element_type in the state
    - a counter containing the number of element_type in the state and acknowledged
    - a counter containing the number of element_type in the state and in downtime
    - a counter containing the number of element_type in the state and flapping
    - the maximum business impact of the element_type in the state

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'internal_resource': True,
        'schema': {
            'schema_version': {
                'type': 'integer',
                'default': 1,
            },
            'hosts_total': {
                'schema_version': 1,
                'type': 'integer',
                'default': 0,
            },
            'hosts_up_hard': {
                'schema_version': 1,
                'type': 'integer',
                'default': 0,
            },
            'hosts_up_soft': {
                'schema_version': 1,
                'type': 'integer',
                'default': 0,
            },
            'hosts_down_hard': {
                'schema_version': 1,
                'type': 'integer',
                'default': 0,
            },
            'hosts_down_soft': {
                'schema_version': 1,
                'type': 'integer',
                'default': 0,
            },
            'hosts_unreachable_hard': {
                'schema_version': 1,
                'type': 'integer',
                'default': 0,
            },
            'hosts_unreachable_soft': {
                'schema_version': 1,
                'type': 'integer',
                'default': 0,
            },
            'hosts_acknowledged': {
                'schema_version': 1,
                'type': 'integer',
                'default': 0
            },
            'hosts_in_downtime': {
                'schema_version': 1,
                'type': 'integer',
                'default': 0
            },
            'hosts_flapping': {
                'schema_version': 1,
                'type': 'integer',
                'default': 0
            },
            'hosts_business_impact': {
                'schema_version': 1,
                'type': 'integer',
                'default': 0
            },
            'services_total': {
                'schema_version': 1,
                'type': 'integer',
                'default': 0,
            },
            'services_ok_hard': {
                'schema_version': 1,
                'type': 'integer',
                'default': 0,
            },
            'services_ok_soft': {
                'schema_version': 1,
                'type': 'integer',
                'default': 0,
            },
            'services_warning_hard': {
                'schema_version': 1,
                'type': 'integer',
                'default': 0,
            },
            'services_warning_soft': {
                'schema_version': 1,
                'type': 'integer',
                'default': 0,
            },
            'services_critical_hard': {
                'schema_version': 1,
                'type': 'integer',
                'default': 0,
            },
            'services_critical_soft': {
                'schema_version': 1,
                'type': 'integer',
                'default': 0,
            },
            'services_unknown_hard': {
                'schema_version': 1,
                'type': 'integer',
                'default': 0,
            },
            'services_unknown_soft': {
                'schema_version': 1,
                'type': 'integer',
                'default': 0,
            },
            'services_unreachable_hard': {
                'schema_version': 1,
                'type': 'integer',
                'default': 0,
            },
            'services_unreachable_soft': {
                'schema_version': 1,
                'type': 'integer',
                'default': 0,
            },
            'services_acknowledged': {
                'schema_version': 1,
                'type': 'integer',
                'default': 0
            },
            'services_in_downtime': {
                'schema_version': 1,
                'type': 'integer',
                'default': 0
            },
            'services_flapping': {
                'schema_version': 1,
                'type': 'integer',
                'default': 0
            },
            'services_business_impact': {
                'schema_version': 1,
                'type': 'integer',
                'default': 0
            },
            'livesynthesis': {
                'schema_version': 1,
                'type': 'objectid',
                'data_relation': {
                    'resource': 'livesynthesis',
                },
                'required': True,
            }
        },
        'schema_deleted': {}
    }
