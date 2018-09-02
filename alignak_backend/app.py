#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    ``alignak_backend.app`` module

    This module manages the backend, its configuration and starts the backend

    Default date format is:
        '%a, %d %b %Y %H:%M:%S GMT'
"""

from __future__ import print_function

import json
import os
import re
import sys
import time
import uuid
import socket
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from collections import OrderedDict
from datetime import datetime, timedelta

import logging
from logging.config import dictConfig as logger_dictConfig

import requests

from dateutil import parser

from future.utils import iteritems

import pymongo
from jsmin import jsmin

from eve import Eve
from eve.auth import TokenAuth
from eve.io.mongo import Validator
from eve.methods.delete import deleteitem_internal
from eve.methods.patch import patch_internal
from eve.methods.post import post_internal
from eve.utils import debug_error_message
from eve_swagger import swagger
from flask import current_app, g, request, abort, jsonify, make_response, send_from_directory, \
    redirect
from flask_apscheduler import APScheduler
from flask_bootstrap import Bootstrap
from werkzeug.security import check_password_hash, generate_password_hash
from bson.objectid import ObjectId

import alignak_backend
from alignak_backend import manifest
from alignak_backend.grafana import Grafana
from alignak_backend.livesynthesis import Livesynthesis
from alignak_backend.models import register_models
from alignak_backend.template import Template
from alignak_backend.timeseries import Timeseries

_subcommands = OrderedDict()


class MyTokenAuth(TokenAuth):
    """
    Class to manage authentication
    """
    children_realms = {}
    parent_realms = {}

    """Authentication token class"""
    def check_auth(self, token, allowed_roles, resource, method):
        # pylint: disable=too-many-locals
        """
        Check if account exist and get roles for this user

        :param token: token for auth
        :type token: str
        :param allowed_roles:
        :type allowed_roles:
        :param resource: name of the resource requested by user
        :type resource: str
        :param method: method used: GET | POST | PATCH | DELETE
        :type method: str
        :return: True if user exist and password is ok or if no roles defined, otherwise False
        :rtype: bool
        """
        user = current_app.data.driver.db['user'].find_one({'token': token})
        if user:
            # We get all resources we have in the backend for the userrestrictrole with *
            resource_list = list(current_app.config['DOMAIN'])

            g.updateRealm = False
            g.updateGroup = False
            g.user_realm = user['_realm']

            # get children of realms for rights
            realmsdrv = current_app.data.driver.db['realm']
            allrealms = realmsdrv.find()
            self.children_realms = {}
            self.parent_realms = {}
            for realm in allrealms:
                self.children_realms[realm['_id']] = realm['_all_children']
                self.parent_realms[realm['_id']] = realm['_tree_parents']

            g.back_role_super_admin = user['back_role_super_admin']
            g.can_submit_commands = user['can_submit_commands']
            userrestrictroles = current_app.data.driver.db['userrestrictrole']
            userrestrictrole = userrestrictroles.find({'user': user['_id']})
            g.resources_get = {}
            g.resources_get_parents = {}
            get_parents = {}
            g.resources_get_custom = {}
            g.resources_post = {}
            g.resources_post_parents = {}
            g.resources_patch = {}
            g.resources_patch_parents = {}
            g.resources_patch_custom = {}
            g.resources_delete = {}
            g.resources_delete_parents = {}
            g.resources_delete_custom = {}
            for rights in userrestrictrole:
                self.add_resources_realms('read', rights, False, g.resources_get, resource_list,
                                          get_parents)
                self.add_resources_realms('read', rights, True, g.resources_get_custom,
                                          resource_list)
                self.add_resources_realms('create', rights, False, g.resources_post, resource_list)
                self.add_resources_realms('update', rights, False, g.resources_patch,
                                          resource_list)
                self.add_resources_realms('update', rights, True, g.resources_patch_custom,
                                          resource_list)
                self.add_resources_realms('delete', rights, False, g.resources_delete,
                                          resource_list)
                self.add_resources_realms('delete', rights, True, g.resources_delete_custom,
                                          resource_list)
            for res in g.resources_get:
                g.resources_get[res] = list(set(g.resources_get[res]))
                if res in g.resources_get_custom:
                    g.resources_get_custom[res] = list(set(g.resources_get_custom[res]))
                g.resources_get_parents[res] = [item for item in get_parents[res]
                                                if item not in g.resources_get[res]]
            for res in g.resources_post:
                g.resources_post[res] = list(set(g.resources_post[res]))
            for res in g.resources_patch:
                g.resources_patch[res] = list(set(g.resources_patch[res]))
            for res in g.resources_delete:
                g.resources_delete[res] = list(set(g.resources_delete[res]))
            g.users_id = user['_id']
            self.set_request_auth_value(user['_id'])
        return user

    def add_resources_realms(self, right, data, custom, resource, resource_list, parents=None):
        """
        Add realms found for rights. it's used to fill rights when connect to app

        :param right: right in list: create, read, update, delete
        :type right: str
        :param data: data (one record) from userrestrictrole (from mongo)
        :type data: dict
        :param custom: True if it's a custom right, otherwise False
        :type custom: bool
        :param resource: variable where store realm rights
        :type resource: dict
        :param resource_list: list of all resources of the backend
        :type resource_list: list
        :param parents: variable where store parents realms (required only for read right)
        :type parents: dict or None
        :return: None
        """
        # pylint: disable=too-many-arguments
        search_field = right
        if custom:
            search_field = 'custom'
        if data['resource'] == '*':
            my_resources = resource_list
        else:
            my_resources = [data['resource']]
        if search_field in data['crud']:
            for my_resource in my_resources:
                if my_resource not in resource:
                    resource[my_resource] = []
                if right == 'read' and not custom and my_resource not in parents:
                    parents[my_resource] = []
                resource[my_resource].append(data['realm'])
                if right == 'read' and not custom:
                    parents[my_resource].extend(self.parent_realms[data['realm']])
                if data['sub_realm']:
                    resource[my_resource].extend(self.children_realms[data['realm']])


class MyValidator(Validator):
    """Specific validator for data model fields types extension"""
    # pylint: disable=unused-argument
    def _validate_skill_level(self, skill_level, field, value):
        """Validate 'skill_level' field (always valid)"""
        return

    # pylint: disable=unused-argument
    def _validate_title(self, title, field, value):
        """Validate 'title' field (always valid)"""
        return

    # pylint: disable=unused-argument
    def _validate_comment(self, comment, field, value):
        """Validate 'comment' field (always valid)"""
        return

    # pylint: disable=unused-argument
    def _validate_schema_version(self, schema_version, field, value):
        """Validate 'schema_version' field (always valid)"""
        return


def notify_alignak(event=None, parameters=None, notification=None):
    """Send a notification to the Alignak arbiter if configured"""
    if not settings['ALIGNAK_URL'] or not event:
        return

    try:
        current_app.logger.info("Logging an Alignak notification: %s / %s (%s)"
                                % (event, parameters, notification))
        data = {'event': event}
        if parameters:
            data['parameters'] = parameters
        if notification:
            data['notification'] = notification
        response, _, _, _, _ = post_internal('alignak_notifications', data, True)
        current_app.logger.debug("Notification: %s" % response)
    except Exception as exp:
        current_app.logger.error("Alignak notification log failed: %s" % str(exp))


# Hooks used to check user's rights
def pre_get(resource, user_request, lookup):
    """Hook before get data. Add filter depend on roles of user

    :param resource: name of the resource requested by user
    :type resource: str
    :param user_request: request of the user
    :type user_request: object
    :param lookup: values to get (filter in the request)
    :type lookup: dict
    :return: None
    """
    # pylint: disable=unused-argument
    if g.get('back_role_super_admin', False):
        return

    # Only if not super-admin
    if resource not in ['user']:
        # Get all resources we can have rights for reading
        resources_get = g.get('resources_get', {})
        resources_get_parents = g.get('resources_get_parents', {})
        resources_get_custom = g.get('resources_get_custom', {})
        users_id = g.get('users_id', {})

        if resource not in resources_get and resource not in resources_get_custom:
            lookup["_id"] = ''
        else:
            if resource not in resources_get:
                resources_get[resource] = []
            if resource not in resources_get_parents:
                resources_get_parents[resource] = []
            if resource not in resources_get_custom:
                resources_get_custom[resource] = []
            if resource in ['realm']:
                lookup['$or'] = [{'_id': {'$in': resources_get[resource]}}]
            else:
                lookup['$or'] = [{'_realm': {'$in': resources_get[resource]}},
                                 {'$and': [{'_sub_realm': True},
                                           {'_realm': {'$in': resources_get_parents[resource]}}]},
                                 {'$and': [{'_users_read': users_id},
                                           {'_realm': {'$in': resources_get_custom[resource]}}]}]


def pre_post(resource, user_request):
    """Hook before posting data.

    Check if the user restrictions match the request

    :param resource: name of the resource requested by user
    :type resource: str
    :param user_request: request of the user
    :type user_request: object
    :return: None
    """
    # pylint: disable=unused-argument
    if g.get('back_role_super_admin', False):
        return

    # Only for some resources ...
    if resource not in ['user', 'actionacknowledge', 'actiondowntime', 'actionforcecheck']:
        # Get all resources we can have rights for creation
        resources_post = g.get('resources_post', {})
        resources_post_custom = g.get('resources_post_custom', {})

        if resource not in resources_post and resource not in resources_post_custom:
            abort(401, description='Not allowed to POST on this endpoint / resource.')


def pre_patch(resource, user_request, lookup):
    """Hook before updating data.

    Check if the user restrictions match the request

    :param resource: name of the resource requested by user
    :type resource: str
    :param user_request: request of the user
    :type user_request: object
    :param lookup: values to get (filter in the request)
    :type lookup: dict
    :return: None
    """
    # pylint: disable=unused-argument
    if g.get('back_role_super_admin', False):
        return

    # Only for some resources ...
    if resource not in ['user', 'actionacknowledge', 'actiondowntime', 'actionforcecheck']:
        # Get all resources we can have rights for updating
        resources_patch = g.get('resources_patch', {})
        resources_patch_parents = g.get('resources_patch_parents', {})
        resources_patch_custom = g.get('resources_patch_custom', {})
        users_id = g.get('users_id', {})

        if resource not in resources_patch and resource not in resources_patch_custom:
            abort(401, description='Not allowed to PATCH on this endpoint / resource.')
        else:
            if resource not in resources_patch:
                resources_patch[resource] = []
            if resource not in resources_patch_parents:
                resources_patch_parents[resource] = []
            if resource not in resources_patch_custom:
                resources_patch_custom[resource] = []
            if resource in ['realm']:
                lookup['$or'] = [{'_id': {'$in': resources_patch[resource]}}]
            else:
                lookup['$or'] = [{'_realm': {'$in': resources_patch[resource]}},
                                 {'$and': [{'_sub_realm': True},
                                           {'_realm': {'$in': resources_patch_parents[resource]}}]},
                                 {'$and': [{'_users_update': users_id},
                                           {'_realm': {'$in': resources_patch_custom[resource]}}]}]


def pre_delete(resource, user_request, lookup):
    """Hook before deleting data.

    Check if the user restrictions match the request

    :param resource: name of the resource requested by user
    :type resource: str
    :param user_request: request of the user
    :type user_request: object
    :param lookup: values to get (filter in the request)
    :type lookup: dict
    :return: None
    """
    # pylint: disable=unused-argument
    if g.get('back_role_super_admin', False):
        return

    # Only if not super-admin
    if resource not in ['user']:
        # Get all resources we can have rights for delation
        resources_delete = g.get('resources_delete', {})
        resources_delete_parents = g.get('resources_delete_parents', {})
        resources_delete_custom = g.get('resources_delete_custom', {})
        users_id = g.get('users_id', {})

        if resource not in resources_delete and resource not in resources_delete_custom:
            abort(401, description='Not allowed to DELETE on this endpoint / resource.')
        else:
            if resource not in resources_delete:
                resources_delete[resource] = []
            if resource not in resources_delete_parents:
                resources_delete_parents[resource] = []
            if resource not in resources_delete_custom:
                resources_delete_custom[resource] = []
            if resource in ['realm']:
                lookup['$or'] = [{'_id': {'$in': resources_delete[resource]}}]
            else:
                lookup['$or'] = [{'_realm': {'$in': resources_delete[resource]}},
                                 {'$and': [{'_sub_realm': True},
                                           {'_realm': {
                                               '$in': resources_delete_parents[resource]}}]},
                                 {'$and': [{'_users_delete': users_id},
                                           {'_realm': {
                                               '$in': resources_delete_custom[resource]}}]}]


# Escalations
def pre_hostescalation_post(items):
    """Hook before adding new serviceescalation element

    If no escalation_period is provided then the 24x7 default TP will be used.

    :param items: provided serviceescalation elements
    :type items: list of dict
    :return: None
    """
    for dummy, item in enumerate(items):
        if 'escalation_period' not in item:
            tps = app.data.driver.db['timeperiod']
            tp_always = tps.find_one({'name': '24x7'})
            item['escalation_period'] = tp_always['_id']


def pre_serviceescalation_post(items):
    """Hook before adding new serviceescalation element

    If no escalation_period is provided then the 24x7 default TP will be used.

    :param items: provided serviceescalation elements
    :type items: list of dict
    :return: None
    """
    for dummy, item in enumerate(items):
        if 'escalation_period' not in item:
            tps = app.data.driver.db['timeperiod']
            tp_always = tps.find_one({'name': '24x7'})
            item['escalation_period'] = tp_always['_id']


# History
def pre_history_post(items):
    """
    Hook before adding new history element

    If host _id is not provided, search for an host with host_name. Same for service and user.

    :param items: history fields
    :type items: dict
    :return: None
    """
    hosts_drv = current_app.data.driver.db['host']
    services_drv = current_app.data.driver.db['service']
    users_drv = current_app.data.driver.db['user']
    for dummy, item in enumerate(items):
        if 'host' in item and item['host']:
            host = hosts_drv.find_one({'_id': item['host']})
            if host:
                item['host_name'] = host['name']
            else:
                continue
        elif 'host_name' in item and item['host_name']:
            host = hosts_drv.find_one({'name': item['host_name']})
            if host:
                item['host'] = host['_id']
            else:
                continue
        else:
            continue

        host = hosts_drv.find_one({'_id': item['host']})
        # Set _realm as host's _realm
        item['_realm'] = host['_realm']
        item['_sub_realm'] = host['_sub_realm']

        # Find service and service_name
        if 'service' in item and item['service']:
            service = services_drv.find_one({'_id': item['service']})
            if service:
                item['service_name'] = service['name']
        elif 'service_name' in item and item['service_name']:
            service = services_drv.find_one({'host': item['host'], 'name': item['service_name']})
            if service:
                item['service'] = service['_id']

        # Find user and user_name
        if 'user' in item and item['user']:
            user = users_drv.find_one({'_id': item['user']})
            if user:
                item['user_name'] = user['name']
        elif 'user_name' in item and item['user_name']:
            user = users_drv.find_one({'name': item['user_name']})
            if user:
                item['user'] = user['_id']
        else:
            item['user_name'] = 'Alignak'
            item['user'] = None


# Log checks results
def pre_logcheckresult_post(items):
    """
    Hook before adding new logcheckresult

    :param items: logcheckresult fields
    :type items: dict
    :return: None
    """
    hosts_drv = current_app.data.driver.db['host']
    services_drv = current_app.data.driver.db['service']
    for dummy, item in enumerate(items):
        current_app.logger.debug("LCR - got a check result: %s" % item)

        if not item.get('host') and not item.get('host_name'):
            abort(make_response("Posting LCR without host information is not accepted.", 412))

        # Find the concerned host
        if not item.get('host'):
            host = hosts_drv.find_one({'name': item['host_name']})
            item['host'] = host['_id']
        else:
            host = hosts_drv.find_one({'_id': item['host']})
            item['host_name'] = host['name']
        item_last_check = host['ls_last_check']

        if not item.get('service') and not item.get('service_name'):
            # This is valid for an host check result
            item['service'] = None
            item['service_name'] = ''
        else:
            # We got a service check result
            if item.get('service_name') and not item.get('service'):
                service = services_drv.find_one(
                    {'host': item['host'], 'name': item['service_name']})
                item['service'] = service['_id']

            if item.get('service') and not item.get('service_name'):
                service = services_drv.find_one({'_id': item['service']})
                item['service_name'] = service['name']
            item_last_check = service['ls_last_check']

        # Set _realm as host's _realm
        item['_realm'] = host['_realm']

        g.updateLivestate = True
        # If the log check result is older than the item last check, do not update the livestate
        if item_last_check and item['last_check'] < item_last_check:
            current_app.logger.debug("LCR - will not update the livestate: %s / %s",
                                     item['last_check'], item_last_check)
            g.updateLivestate = False

        current_app.logger.debug("LCR - inserting an LCR for %s/%s...",
                                 item['host_name'], item['service_name'])


def after_insert_logcheckresult(items):
    """
    Hook after logcheckresult inserted.

    :param items: realm fields
    :type items: dict
    :return: None
    """
    for dummy, item in enumerate(items):
        current_app.logger.debug("LCR - inserted an LCR for %s/%s...",
                                 item['host_name'], item['service_name'])
        current_app.logger.debug("    -> %s..." % item)

        if g.updateLivestate:
            # Update the livestate...
            if item['service']:
                # ...for a service
                lookup = {"_id": item['service']}
                data = {
                    'ls_state': item['state'],
                    'ls_state_type': item['state_type'],
                    'ls_state_id': item['state_id'],
                    'ls_acknowledged': item['acknowledged'],
                    'ls_acknowledgement_type': item['acknowledgement_type'],
                    'ls_downtimed': item['downtimed'],
                    'ls_last_check': item['last_check'],
                    'ls_last_state': item['last_state'],
                    'ls_last_state_type': item['last_state_type'],
                    'ls_output': item['output'],
                    'ls_long_output': item['long_output'],
                    'ls_perf_data': item['perf_data'],
                    'ls_current_attempt': item['current_attempt'],
                    'ls_latency': item['latency'],
                    'ls_execution_time': item['execution_time'],
                    'ls_passive_check': item['passive_check'],
                    'ls_state_changed': item.get('state_changed'),
                    'ls_last_state_changed': item['last_state_changed'],
                    'ls_last_hard_state_changed': item['last_hard_state_changed'],
                    'ls_last_time_ok': item['last_time_0'],
                    'ls_last_time_warning': item['last_time_1'],
                    'ls_last_time_critical': item['last_time_2'],
                    'ls_last_time_unknown': item['last_time_3'],
                    'ls_last_time_unreachable': item['last_time_4']
                }
                (pi_a, pi_b, pi_c, pi_d) = patch_internal('service', data, False, False, **lookup)
            else:
                # ...for an host
                lookup = {"_id": item['host']}
                data = {
                    'ls_state': item['state'],
                    'ls_state_type': item['state_type'],
                    'ls_state_id': item['state_id'],
                    'ls_acknowledged': item['acknowledged'],
                    'ls_acknowledgement_type': item['acknowledgement_type'],
                    'ls_downtimed': item['downtimed'],
                    'ls_last_check': item['last_check'],
                    'ls_last_state': item['last_state'],
                    'ls_last_state_type': item['last_state_type'],
                    'ls_output': item['output'],
                    'ls_long_output': item['long_output'],
                    'ls_perf_data': item['perf_data'],
                    'ls_current_attempt': item['current_attempt'],
                    'ls_latency': item['latency'],
                    'ls_execution_time': item['execution_time'],
                    'ls_passive_check': item['passive_check'],
                    'ls_state_changed': item.get('state_changed'),
                    'ls_last_state_changed': item['last_state_changed'],
                    'ls_last_hard_state_changed': item['last_hard_state_changed'],
                    'ls_last_time_up': item['last_time_0'],
                    'ls_last_time_down': item['last_time_1'],

                    'ls_last_time_unreachable': item['last_time_4']
                }
                (pi_a, pi_b, pi_c, pi_d) = patch_internal('host', data, False, False, **lookup)

            current_app.logger.debug("LCR - updated the livestate: %s, %s, %s, %s",
                                     pi_a, pi_b, pi_c, pi_d)

        # Create an history event for the new logcheckresult
        message = "%s[%s] (%s/%s): %s" % (item['state'], item['state_type'],
                                          item['acknowledged'], item['downtimed'],
                                          item['output'])
        data = {
            'host': item['host'],
            'host_name': item['host_name'],
            'service': item['service'],
            'service_name': item['service_name'],
            'user': None,
            'type': 'check.result',
            'message': message,
            'logcheckresult': item['_id']
        }
        post_internal("history", data, True)


# Actions
def pre_post_action_right(actrequestp):
    """Deny post on action* endpoint if the logged-in user do not have can_submit_commands

    :param actrequestp:
    :return:
    """
    # pylint: disable=unused-argument
    if not g.get('can_submit_commands', False):
        abort(403)


def pre_submit_action_right(actrequest, lookup):
    # pylint: disable=unused-argument
    """Deny patch or delete action* endpoint if the logged-in user do not have can_submit_commands

    :param actrequest:
    :param lookup:
    :return:
    """
    if not g.get('can_submit_commands', False):
        abort(403)


# Actions acknowledge
def pre_actionacknowledge_post(items):
    """
    Hook before adding new acknowledge

    :param items: actionacknowledge fields
    :type items: dict
    :return: None
    """
    hosts_drv = current_app.data.driver.db['host']
    for dummy, item in enumerate(items):
        # Set _realm as host's _realm
        host = hosts_drv.find_one({'_id': item['host']})
        item['_realm'] = host['_realm']
        item['_sub_realm'] = host['_sub_realm']


def after_insert_actionacknowledge(items):
    """
    Hook after action acknowledge inserted.

    :param items: realm fields
    :type items: dict
    :return: None
    """
    hosts_drv = current_app.data.driver.db['host']
    services_drv = current_app.data.driver.db['service']
    for dummy, item in enumerate(items):
        # Get concerned host
        host = hosts_drv.find_one({'_id': item['host']})
        service_name = ''
        if item['service']:
            service = services_drv.find_one({'_id': item['service']})
            service_name = service['name']

        # Create an history event for the new acknowledge
        data = {
            'host': item['host'],
            'host_name': host['name'],
            'service': item['service'],
            'service_name': service_name,
            'user': item['user'],
            'type': 'ack.' + item['action'],
            'message': item['comment']
        }
        post_internal("history", data, True)


def after_update_actionacknowledge(updated, original):
    """
    Hook update on actionacknowledge

    :param updated: modified fields
    :type updated: dict
    :param original: original fields
    :type original: dict
    :return: None
    """
    if 'processed' in updated and updated['processed']:
        hosts_drv = current_app.data.driver.db['host']
        services_drv = current_app.data.driver.db['service']

        # Get concerned host
        host = hosts_drv.find_one({'_id': original['host']})
        service_name = ''
        if original['service']:
            service = services_drv.find_one({'_id': original['service']})
            service_name = service['name']

        # Create an history event for the changed acknowledge
        data = {
            'host': original['host'],
            'host_name': host['name'],
            'service': original['service'],
            'service_name': service_name,
            'user': original['user'],
            'type': 'ack.processed',
            'message': original['comment'],
            'content': {
            }
        }
        post_internal("history", data, True)


# Actions downtime
def pre_actiondowntime_post(items):
    """
    Hook before adding new downtime

    :param items: actiondowntime fields
    :type items: dict
    :return: None
    """
    hosts_drv = current_app.data.driver.db['host']
    for dummy, item in enumerate(items):
        # Set _realm as host's _realm
        host = hosts_drv.find_one({'_id': item['host']})
        item['_realm'] = host['_realm']
        item['_sub_realm'] = host['_sub_realm']


def after_insert_actiondowntime(items):
    """
    Hook after action downtime inserted.

    :param items: realm fields
    :type items: dict
    :return: None
    """
    hosts_drv = current_app.data.driver.db['host']
    services_drv = current_app.data.driver.db['service']
    for dummy, item in enumerate(items):
        # Get concerned host
        host = hosts_drv.find_one({'_id': item['host']})
        service_name = ''
        if item['service']:
            service = services_drv.find_one({'_id': item['service']})
            service_name = service['name']

        # Create an history event for the new downtime
        data = {
            'host': item['host'],
            'host_name': host['name'],
            'service': item['service'],
            'service_name': service_name,
            'user': item['user'],
            'type': 'downtime.' + item['action'],
            'message': item['comment']
        }
        post_internal("history", data, True)


def after_update_actiondowntime(updated, original):
    """
    Hook update on actiondowntime

    :param updated: modified fields
    :type updated: dict
    :param original: original fields
    :type original: dict
    :return: None
    """
    if 'processed' in updated and updated['processed']:
        hosts_drv = current_app.data.driver.db['host']
        services_drv = current_app.data.driver.db['service']

        # Get concerned host
        host = hosts_drv.find_one({'_id': original['host']})
        service_name = ''
        if original['service']:
            service = services_drv.find_one({'_id': original['service']})
            service_name = service['name']

        # Create an history event for the changed downtime
        data = {
            'host': original['host'],
            'host_name': host['name'],
            'service': original['service'],
            'service_name': service_name,
            'user': original['user'],
            'type': 'downtime.processed',
            'message': original['comment'],
            'content': {
            }
        }
        post_internal("history", data, True)


# Actions forcecheck
def pre_actionforcecheck_post(items):
    """
    Hook before adding new forcecheck

    :param items: actionforcecheck fields
    :type items: dict
    :return: None
    """
    hosts_drv = current_app.data.driver.db['host']
    for dummy, item in enumerate(items):
        # Set _realm as host's _realm
        host = hosts_drv.find_one({'_id': item['host']})
        item['_realm'] = host['_realm']
        item['_sub_realm'] = host['_sub_realm']


def after_insert_actionforcecheck(items):
    """
    Hook after action forcecheck inserted.

    :param items: realm fields
    :type items: dict
    :return: None
    """
    hosts_drv = current_app.data.driver.db['host']
    services_drv = current_app.data.driver.db['service']
    for dummy, item in enumerate(items):
        # Get concerned host
        host = hosts_drv.find_one({'_id': item['host']})
        service_name = ''
        if item['service']:
            service = services_drv.find_one({'_id': item['service']})
            service_name = service['name']

        # Create an history event for the new forcecheck
        data = {
            'host': item['host'],
            'host_name': host['name'],
            'service': item['service'],
            'service_name': service_name,
            'user': item['user'],
            'type': 'check.request',
            'message': item['comment']
        }
        post_internal("history", data, True)


def after_update_actionforcecheck(updated, original):
    """
    Hook update on actionforcecheck

    :param updated: modified fields
    :type updated: dict
    :param original: original fields
    :type original: dict
    :return: None
    """
    if 'processed' in updated and updated['processed']:
        hosts_drv = current_app.data.driver.db['host']
        services_drv = current_app.data.driver.db['service']

        # Get concerned host
        host = hosts_drv.find_one({'_id': original['host']})
        service_name = ''
        if original['service']:
            service = services_drv.find_one({'_id': original['service']})
            service_name = service['name']

        # Create an history event for the changed forcecheck
        data = {
            'host': original['host'],
            'host_name': host['name'],
            'service': original['service'],
            'service_name': service_name,
            'user': original['user'],
            'type': 'check.requested',
            'message': original['comment'],
            'content': {
            }
        }
        post_internal("history", data, True)


# Hosts groups
def pre_hostgroup_post(items):
    """
    Hook before adding a new hostgroup

    Manage hostgroup level and parents tree.

    :param items: hostgroup fields
    :type items: dict
    :return: None
    """
    hgs_drv = current_app.data.driver.db['hostgroup']
    for dummy, item in enumerate(items):
        # Default parent
        if '_parent' not in item or not item['_parent']:
            # Use default hostgroup as a parent
            def_hg = hgs_drv.find_one({'name': 'All'})
            if def_hg:
                item['_parent'] = def_hg['_id']

        # Make sure hosts and hostgroups are a unique list (avoid duplicates)
        if 'hosts' in item:
            item['hosts'] = list(set(item['hosts']))

        if 'hostgroups' in item:
            item['hostgroups'] = list(set(item['hostgroups']))

        # Compute _level
        parent_hg = hgs_drv.find_one({'_id': item['_parent']})
        item['_level'] = parent_hg['_level'] + 1

        # Add parent in _tree_parents
        item['_tree_parents'] = parent_hg['_tree_parents']
        item['_tree_parents'].append(parent_hg['_id'])


def pre_hostgroup_patch(updates, original):
    """
    Hook before updating existing hostgroup

    :param updates: modified fields
    :type updates: dict
    :param original: original fields
    :type original: dict
    :return: None
    """
    if not g.updateGroup:
        if '_tree_parents' in updates:
            abort(make_response("Updating _tree_parents is forbidden", 412))

    # Make sure hosts and hostgroups are a unique list (avoid duplicates)
    if 'hosts' in updates:
        updates['hosts'] = list(set(updates['hosts']))

    if 'hostgroups' in updates:
        updates['hostgroups'] = list(set(updates['hostgroups']))

    if '_parent' in updates and updates['_parent'] != original['_parent']:
        hgs_drv = current_app.data.driver.db['hostgroup']

        # Find parent
        parent_hg = hgs_drv.find_one({'_id': updates['_parent']})
        if not parent_hg:
            abort(make_response("Error: parent not found: %s" % updates['_parent'], 412))

        # Compute _level
        updates['_level'] = parent_hg['_level'] + 1

        # Add parent in _tree_parents
        updates['_tree_parents'] = parent_hg['_tree_parents']
        updates['_tree_parents'].append(parent_hg['_id'])


# Services groups
def pre_servicegroup_post(items):
    """
    Hook before adding a new servicegroup

    Manage servicegroup level and parents tree.

    :param items: servicegroup fields
    :type items: dict
    :return: None
    """
    sgs_drv = current_app.data.driver.db['servicegroup']
    for dummy, item in enumerate(items):
        # Default parent
        if '_parent' not in item or not item['_parent']:
            # Use default servicegroup as a parent
            def_sg = sgs_drv.find_one({'name': 'All'})
            if def_sg:
                item['_parent'] = def_sg['_id']

        # Make sure services and servicegroups are a unique list (avoid duplicates)
        if 'services' in item:
            item['services'] = list(set(item['services']))

        if 'servicegroups' in item:
            item['servicegroups'] = list(set(item['servicegroups']))

        # Compute _level
        parent_sg = sgs_drv.find_one({'_id': item['_parent']})
        item['_level'] = parent_sg['_level'] + 1

        # Add parent in _tree_parents
        item['_tree_parents'] = parent_sg['_tree_parents']
        item['_tree_parents'].append(parent_sg['_id'])


def pre_servicegroup_patch(updates, original):
    """
    Hook before updating existing servicegroup

    :param updates: modified fields
    :type updates: dict
    :param original: original fields
    :type original: dict
    :return: None
    """
    if not g.updateGroup:
        if '_tree_parents' in updates:
            abort(make_response("Updating _tree_parents is forbidden", 412))

    # Make sure services and servicegroups are a unique list (avoid duplicates)
    if 'services' in updates:
        updates['services'] = list(set(updates['services']))

    if 'servicegroups' in updates:
        updates['servicegroups'] = list(set(updates['servicegroups']))

    if '_parent' in updates and updates['_parent'] != original['_parent']:
        sgs_drv = current_app.data.driver.db['servicegroup']

        # Find parent
        parent_sg = sgs_drv.find_one({'_id': updates['_parent']})
        if not parent_sg:
            abort(make_response("Error: parent not found: %s" % updates['_parent'], 412))

        # Compute _level
        updates['_level'] = parent_sg['_level'] + 1

        # Add parent in _tree_parents
        updates['_tree_parents'] = parent_sg['_tree_parents']
        updates['_tree_parents'].append(parent_sg['_id'])


# Users groups
def pre_usergroup_post(items):
    """
    Hook before adding a new usergroup

    Manage usergroup level and parents tree.

    :param items: usergroup fields
    :type items: dict
    :return: None
    """
    ugs_drv = current_app.data.driver.db['usergroup']
    for dummy, item in enumerate(items):
        # Default parent
        if '_parent' not in item or not item['_parent']:
            # Use default usergroup as a parent
            def_ug = ugs_drv.find_one({'name': 'All'})
            if def_ug:
                item['_parent'] = def_ug['_id']

        # Make sure users and usergroups are a unique list (avoid duplicates)
        if 'users' in item:
            item['users'] = list(set(item['users']))

        if 'usergroups' in item:
            item['usergroups'] = list(set(item['usergroups']))

        # Compute _level
        parent_ug = ugs_drv.find_one({'_id': item['_parent']})
        item['_level'] = parent_ug['_level'] + 1

        # Add parent in _tree_parents
        item['_tree_parents'] = parent_ug['_tree_parents']
        item['_tree_parents'].append(parent_ug['_id'])


def pre_usergroup_patch(updates, original):
    """
    Hook before updating existing usergroup

    :param updates: modified fields
    :type updates: dict
    :param original: original fields
    :type original: dict
    :return: None
    """
    if not g.updateGroup:
        if '_tree_parents' in updates:
            abort(make_response("Updating _tree_parents is forbidden", 412))

    # Make sure users and usergroups are a unique list (avoid duplicates)
    if 'users' in updates:
        updates['users'] = list(set(updates['users']))

    if 'usergroups' in updates:
        updates['usergroups'] = list(set(updates['usergroups']))

    if '_parent' in updates and updates['_parent'] != original['_parent']:
        ugs_drv = current_app.data.driver.db['usergroup']

        # Find parent
        parent_ug = ugs_drv.find_one({'_id': updates['_parent']})
        if not parent_ug:
            abort(make_response("Error: parent not found: %s" % updates['_parent'], 412))

        # Compute _level
        updates['_level'] = parent_ug['_level'] + 1

        # Add parent in _tree_parents
        updates['_tree_parents'] = parent_ug['_tree_parents']
        updates['_tree_parents'].append(parent_ug['_id'])


# Time series
def pre_timeseries_post(items):
    """
    We can't have more than 1 timeseries database (graphite, influx) linked to the same
    grafana in the same realm

    :param items:
    :type items: dict
    :return: None
    """
    graphite_drv = current_app.data.driver.db['graphite']
    influxdb_drv = current_app.data.driver.db['influxdb']
    realm_drv = current_app.data.driver.db['realm']
    for dummy, item in enumerate(items):
        if 'grafana' in item and item['grafana'] is not None:
            # search graphite with grafana id in this realm
            if graphite_drv.count(
                    {'_realm': item['_realm'], 'grafana': item['grafana']}) > 0:
                abort(make_response("A timeserie is yet attached to grafana in this realm", 412))
            # search influxdb with grafana id in this realm
            if influxdb_drv.count(
                    {'_realm': item['_realm'], 'grafana': item['grafana']}) > 0:
                abort(make_response("A timeserie is yet attached to grafana in this realm", 412))
            # get parent realms
            tsrealms = realm_drv.find_one({'_id': item['_realm']})
            if graphite_drv.count(
                    {'_realm': {'$in': tsrealms['_tree_parents']}, 'grafana': item['grafana'],
                     '_sub_realm': True}) > 0:
                abort(make_response("A timeserie is yet attached to grafana in parent realm", 412))
            if influxdb_drv.count(
                    {'_realm': {'$in': tsrealms['_tree_parents']}, 'grafana': item['grafana'],
                     '_sub_realm': True}) > 0:
                abort(make_response("A timeserie is yet attached to grafana in parent realm", 412))


# Realms
def pre_realm_post(items):
    """
    Hook before adding new realm

    :param items: realm fields
    :type items: dict
    :return: None
    """
    realmsdrv = current_app.data.driver.db['realm']
    for dummy, item in enumerate(items):
        # Default parent
        if '_parent' not in item or not item['_parent']:
            # Use default realm as a parent
            dr = realmsdrv.find_one({'name': 'All'})
            item['_parent'] = dr['_id']

        # Compute _level
        parent_realm = realmsdrv.find_one({'_id': item['_parent']})
        item['_level'] = parent_realm['_level'] + 1

        # Add parent in _tree_parents
        item['_tree_parents'] = parent_realm['_tree_parents']
        item['_tree_parents'].append(parent_realm['_id'])


def pre_realm_patch(updates, original):
    """
    Hook before updating existing realm

    :param updates: modified fields
    :type updates: dict
    :param original: original fields
    :type original: dict
    :return: None
    """
    if not g.updateRealm:
        if '_tree_parents' in updates:
            abort(make_response("Updating _tree_parents is forbidden", 412))
        if '_children' in updates:
            abort(make_response("Updating _children is forbidden", 412))
        if '_all_children' in updates:
            abort(make_response("Updating _all_children is forbidden", 412))

    if '_parent' in updates and updates['_parent'] != original['_parent']:
        realmsdrv = current_app.data.driver.db['realm']

        # Add self reference in new parent children tree
        parent = realmsdrv.find_one({'_id': updates['_parent']})
        if original['_id'] not in parent['_children']:
            parent['_children'].append(original['_id'])
        lookup = {"_id": parent['_id']}
        g.updateRealm = True
        patch_internal('realm', {"_children": parent['_children']}, False, False,
                       **lookup)
        g.updateRealm = False

        # Delete self reference in former parent children tree
        if original['_tree_parents']:
            parent = realmsdrv.find_one({'_id': original['_tree_parents'][-1]})
            if original['_id'] in parent['_children']:
                parent['_children'].remove(original['_id'])
            lookup = {"_id": parent['_id']}
            g.updateRealm = True
            patch_internal('realm', {"_children": parent['_children']}, False, False,
                           **lookup)
            g.updateRealm = False

        updates['_level'] = parent['_level'] + 1
        updates['_tree_parents'] = original['_tree_parents']
        if original['_parent'] in original['_tree_parents']:
            updates['_tree_parents'].remove(original['_parent'])
        if updates['_parent'] not in original['_tree_parents']:
            updates['_tree_parents'].append(updates['_parent'])


def after_insert_realm(items):
    """
    Hook after realm inserted. It calculate/update tree parents and children

    :param items: realm fields
    :type items: dict
    :return: None
    """
    # pylint: disable=unused-argument
    for dummy, item in enumerate(items):
        # update _children fields on all parents
        realmsdrv = current_app.data.driver.db['realm']
        parent = realmsdrv.find_one({'_id': item['_parent']})
        parent['_children'].append(item['_id'])
        parent['_all_children'].append(item['_id'])
        lookup = {"_id": parent['_id']}
        g.updateRealm = True
        patch_internal('realm', {
            "_children": parent['_children'],
            "_all_children": parent['_all_children']
        }, False, False, **lookup)
        g.updateRealm = False

        # Notify Alignak
        notify_alignak(event='creation', parameters='realm:%s' % item['name'])


def after_update_realm(updated, original):
    """
    Hook update tree children on realm parent after update tree children realm

    :param updated: modified fields
    :type updated: dict
    :param original: original fields
    :type original: dict
    :return: None
    """
    if g.updateRealm:
        if '_all_children' in updated and updated['_all_children'] != original['_all_children']:
            s = set(original['_all_children'])
            diff = [x for x in updated['_all_children'] if x not in s]
            added_children = (diff != [])
            if not added_children:
                s = set(updated['_all_children'])
                diff = [x for x in original['_all_children'] if x not in s]

            realmsdrv = current_app.data.driver.db['realm']
            parent = realmsdrv.find_one({'_id': original['_parent']})
            if not parent:
                return

            for d in diff:
                if added_children:
                    if d not in parent['_all_children']:
                        parent['_all_children'].append(d)
                else:
                    if d in parent['_all_children']:
                        parent['_all_children'].remove(d)
            lookup = {"_id": parent['_id']}
            g.updateRealm = True
            patch_internal('realm', {
                "_all_children": parent['_all_children']
            }, False, False, **lookup)
            g.updateRealm = False


def pre_delete_realm(item):
    """
    Hook before deleting a realm. Denies deletion if realm has child / children

    :param item: fields of the item / record
    :type item: dict
    :return: None
    """
    if item['_children']:
        abort(409, description=debug_error_message("Item have children, so can't delete it"))


def after_delete_realm(item):
    """
    Hook after realm deletion. Update tree children of parent realm

    :param item: fields of the item / record
    :type item: dict
    :return: None
    """
    realmsdrv = current_app.data.driver.db['realm']
    if item['_tree_parents']:
        parent = realmsdrv.find_one({'_id': item['_tree_parents'][-1]})
        if item['_id'] in parent['_children']:
            parent['_children'].remove(item['_id'])
        if item['_id'] in parent['_all_children']:
            parent['_all_children'].remove(item['_id'])
        lookup = {"_id": parent['_id']}
        g.updateRealm = True
        patch_internal('realm', {
            "_children": parent['_children'],
            "_all_children": parent['_children']
        }, False, False, **lookup)
        g.updateRealm = False

    # Notify Alignak
    notify_alignak(event='deletion', parameters='realm:%s' % item['name'])


def after_delete_resource_realm():
    """
    We deleted all resource realm, so define _children and _all_children of realm All to []

    :return: None
    """
    realmsdrv = current_app.data.driver.db['realm']
    realmall = realmsdrv.find_one({'_level': 0})
    lookup = {"_id": realmall['_id']}
    g.updateRealm = True
    patch_internal('realm', {
        '_children': [],
        '_all_children': []
    }, False, False, **lookup)
    g.updateRealm = False


# Hosts deletion
def pre_delete_host(item):
    """Hook before deleting an host.
    Searches for the host services and deletes them

    :param item: fields of the item / record
    :type item: dict
    :return: None
    """
    current_app.logger.debug("Deleting host: %s", item['name'])
    services_drv = current_app.data.driver.db['service']
    services = services_drv.find({'host': item['_id']})
    for service in services:
        current_app.logger.debug("Deleting service: %s/%s", item['name'], service['name'])
        lookup = {"_id": service['_id']}
        deleteitem_internal('service', False, False, **lookup)


def after_delete_host(item):
    """Hook after host deletion. Update tree children of parent host

    :param item: fields of the item / record
    :type item: dict
    :return: None
    """
    current_app.logger.debug("Deleted host: %s", item['name'])

    # Notify Alignak
    notify_alignak(event='deletion', parameters='host:%s' % item['name'])


# Alignak
def pre_alignak_patch(updates, original):
    # pylint: disable=unused-argument
    """Hook before updating an alignak element.

    When updating an alignak, if only the running data are updated, do not change the
    _updated field.

    :param updates: list of alignak fields to update
    :type updates: dict
    :param original: list of original fields
    :type original: dict
    :return: None
    """
    for key in updates:
        if key not in ['_updated', 'last_alive', 'last_command_check', 'last_log_rotation']:
            break
    else:
        # Only the running fields were updated, do not change _updated field
        del updates['_updated']


# Hosts/ services
def pre_host_patch(updates, original):
    # pylint: disable=too-many-nested-blocks
    """
    Hook before updating an host element.

    If the host realm changed, set its services realm according...

    When updating an host, if only the customs and live state is updated, do not change the
    _updated field and compute the new host overall state..

    Compute the host overall state identifier, including:
    - the acknowledged state
    - the downtime state

    The worst state is (prioritized):
    - an host down (4)
    - an host unreachable (3)
    - an host downtimed (2)
    - an host acknowledged (1)
    - an host up (0)

    If the host overall state is <= 2, then the host overall state is the maximum value
    of the host overall state and all the host services overall states.

    The overall state of an host is:
    - 0 if the host is UP and all its services are OK
    - 1 if the host is DOWN or UNREACHABLE and acknowledged or
        at least one of its services is acknowledged and
        no other services are WARNING or CRITICAL
    - 2 if the host is DOWN or UNREACHABLE and in a scheduled downtime or
        at least one of its services is in a scheduled downtime and no
        other services are WARNING or CRITICAL
    - 3 if the host is UNREACHABLE or
        at least one of its services is WARNING
    - 4 if the host is DOWN or
        at least one of its services is CRITICAL
    - 5 if the host is not monitored

    The _updated field is used by the Alignak arbiter to reload the configuration and we need to
    avoid reloading when the live state is updated.

    :param updates: list of host fields to update
    :type updates: dict
    :param original: list of original fields
    :type original: dict
    :return: None
    """
    for key in updates:
        if key in ['_realm']:
            # If host realm changed, set its services realm according...
            services_drv = current_app.data.driver.db['service']
            services = services_drv.find({'host': original['_id']})
            for service in services:
                lookup = {"_id": service['_id']}
                patch_internal('service', {"_realm": updates['_realm']}, False, False, **lookup)

        if key not in ['_overall_state_id', '_updated', '_realm', 'customs'] \
                and not key.startswith('ls_'):
            break
    else:
        # We updated the host live state, compute the new overall state, or
        # We updated some host services live state, compute the new overall state
        if ('_overall_state_id' in updates and updates['_overall_state_id'] == -1) or \
                ('ls_state_type' in updates and updates['ls_state_type'] == 'HARD'):

            overall_state = 0

            active_checked = original['active_checks_enabled']
            if 'ls_active_checked' in updates:
                active_checked = updates['active_checks_enabled']

            passive_checked = original['passive_checks_enabled']
            if 'ls_passive_checked' in updates:
                passive_checked = updates['passive_checks_enabled']

            acknowledged = original['ls_acknowledged']
            if 'ls_acknowledged' in updates:
                acknowledged = updates['ls_acknowledged']

            downtimed = original['ls_downtimed']
            if 'ls_downtimed' in updates:
                downtimed = updates['ls_downtimed']

            state = original['ls_state']
            if 'ls_state' in updates:
                state = updates['ls_state']
            state = state.upper()

            if acknowledged:
                overall_state = 1
            elif downtimed:
                overall_state = 2
            else:
                if state == 'UNREACHABLE':
                    overall_state = 3
                elif state == 'DOWN':
                    overall_state = 4

            if not active_checked and not passive_checked:
                overall_state = 5
            else:
                if overall_state <= 2:
                    services_drv = current_app.data.driver.db['service']
                    services = services_drv.find({'host': original['_id']})
                    for service in services:
                        # Only for HARD states and monitored services
                        if service['ls_state_type'] == 'HARD' and service['_overall_state_id'] < 5:
                            overall_state = max(overall_state, service['_overall_state_id'])

            # Get the host services overall states
            updates['_overall_state_id'] = overall_state

        # Only some live state fields, do not change _updated field
        del updates['_updated']


def after_insert_host(items):
    """
    Hook after host inserted.

    :param items: host fields
    :type items: dict
    :return: None
    """
    etags = {}
    for dummy, item in enumerate(items):
        if item['_is_template']:
            continue

        overall_state = 0

        active_checked = item['active_checks_enabled']
        passive_checked = item['passive_checks_enabled']
        acknowledged = item['ls_acknowledged']
        downtimed = item['ls_downtimed']
        state = item['ls_state']
        state = state.upper()

        if not active_checked and not passive_checked:
            overall_state = 5
        elif acknowledged:
            overall_state = 1
        elif downtimed:
            overall_state = 2
        else:
            if state == 'UNREACHABLE':
                overall_state = 3
            elif state == 'DOWN':
                overall_state = 4

        # Do not care about services... when inserting an host,
        # services are not yet existing for this host!

        # Host overall was computed, update the host overall state
        lookup = {"_id": item['_id']}
        (_, _, etag, _) = patch_internal('host', {"_overall_state_id": overall_state},
                                         False, False, **lookup)
        etags[item['_etag']] = etag

        # Notify Alignak
        notify_alignak(event='creation', parameters='host:%s' % item['name'])

    if etags:
        g.replace_etags = etags


def pre_service_patch(updates, original):
    """
    Hook before updating a service element.

    When updating a service, if only the customs and live state is updated, do not change the
    _updated field and compute the new service overall state..

    Compute the service overall state identifier, including:
    - the acknowledged state
    - the downtime state

    The worst state is (prioritized):
    - a service is not monitored (5)
    - a service critical or unreachable (4)
    - a service warning or unknown (3)
    - a service downtimed (2)
    - a service acknowledged (1)
    - a service ok (0)

    *Note* that services in unknown state are considered as warning, and unreachable ones
    are considered as critical!

    The _updated field is used by the Alignak arbiter to reload the configuration and we need to
    avoid reloading when the live state is updated.

    :param updates: list of host fields to update
    :type updates: dict
    :param original: list of original fields
    :type original: dict
    :return: None
    """
    # Allow update because it must be done when inserting a service
    # if '_overall_state_id' in updates:
    #     abort(make_response("Updating _overall_state_id for a service is forbidden", 412))

    for key in updates:
        if key not in ['_overall_state_id', '_updated', '_realm', 'customs'] \
                and not key.startswith('ls_'):
            break
    else:
        # pylint: disable=too-many-boolean-expressions
        if 'ls_state_type' in updates and updates['ls_state_type'] == 'HARD':
            # We updated the service live state, compute the new overall state
            if 'ls_state' in updates or 'ls_acknowledged' in updates or 'ls_downtimed' in updates:
                overall_state = 0

                active_checked = original['active_checks_enabled']
                if 'ls_active_checked' in updates:
                    active_checked = updates['active_checks_enabled']

                passive_checked = original['passive_checks_enabled']
                if 'ls_passive_checked' in updates:
                    passive_checked = updates['passive_checks_enabled']

                acknowledged = original['ls_acknowledged']
                if 'ls_acknowledged' in updates:
                    acknowledged = updates['ls_acknowledged']

                downtimed = original['ls_downtimed']
                if 'ls_downtimed' in updates:
                    downtimed = updates['ls_downtimed']

                state = original['ls_state']
                if 'ls_state' in updates:
                    state = updates['ls_state']
                state = state.upper()

                if not active_checked and not passive_checked:
                    overall_state = 5
                elif acknowledged:
                    overall_state = 1
                elif downtimed:
                    overall_state = 2
                else:
                    if state == 'WARNING':
                        overall_state = 3
                    elif state == 'CRITICAL':
                        overall_state = 4
                    elif state == 'UNKNOWN':
                        overall_state = 3
                    elif state == 'UNREACHABLE':
                        overall_state = 4

                updates['_overall_state_id'] = overall_state

        # Only updated some live state fields, do not change _updated field
        del updates['_updated']


def after_insert_service(items):
    """
    Hook after service inserted.

    :param items: host fields
    :type items: dict
    :return: None
    """
    etags = {}
    for dummy, item in enumerate(items):
        overall_state = 0

        active_checked = item['active_checks_enabled']
        passive_checked = item['passive_checks_enabled']
        acknowledged = item['ls_acknowledged']
        downtimed = item['ls_downtimed']
        state = item['ls_state']
        state = state.upper()

        if not active_checked and not passive_checked:
            overall_state = 5
        elif acknowledged:
            overall_state = 1
        elif downtimed:
            overall_state = 2
        else:
            if state == 'WARNING':
                overall_state = 3
            elif state == 'CRITICAL':
                overall_state = 4
            elif state == 'UNKNOWN':
                overall_state = 3
            elif state == 'UNREACHABLE':
                overall_state = 4

        # Service overall was computed, update the service overall state
        lookup = {"_id": item['_id']}
        (_, _, etag, _) = patch_internal('service', {"_overall_state_id": overall_state}, False,
                                         False, **lookup)
        etags[item['_etag']] = etag
    if etags:
        g.replace_etags = etags


def update_etag(myrequest, payload):
    """In case POST item database hook use patch_internal, we update the new _etag in the
    response

    :param myrequest:
    :param payload:
    :return: None
    """
    # pylint: disable=unused-argument
    if not g.get('replace_etags', {}):
        return
    else:
        for idx, resp in enumerate(payload.response):
            resp = resp.decode('UTF-8')
            for old_etag, new_etag in iteritems(g.replace_etags):
                resp = resp.replace(old_etag, new_etag)
            payload.response[idx] = resp
        del g.replace_etags


def after_updated_service(updated, original):
    """
    Hook called after a service got updated

    :param updated: updated fields
    :type updated: dict
    :param original: original fields
    :type original: dict
    :return: None
    """
    if '_overall_state_id' in updated:
        # Service overall was updated, we should update its host overall state
        lookup = {"_id": original['host']}
        patch_internal('host', {"_overall_state_id": -1}, False, False, **lookup)


# Users
def pre_user_post(items):
    """
    Hook before insert.
    When add user, hash the backend password of the user and generate a token
    If no host/service notification periods are provided, use the default 'Never' TP

    :param items: list of items (list because can use bulk)
    :type items: list
    :return: None
    """
    for key, item in enumerate(items):
        if 'password' in item:
            items[key]['password'] = generate_password_hash(item['password'])
        if 'token' in item:
            items[key]['token'] = generate_token()


def pre_user_patch(updates, original):
    """
    Hook before update.

    When updating user:
    - hash the backend password of the user if one tries to change it
    - generate the user token if a token (even empty) is provided

    If only the user preferences are updated do not change the _updated field (see comment in the
    pre_host_patch).

    :param updates: list of user fields to update
    :type updates: dict
    :param original: list of original fields
    :type original: dict
    :return: None
    """
    # pylint: disable=unused-argument
    if 'password' in updates:
        updates['password'] = generate_password_hash(updates['password'])
    if 'token' in updates:
        updates['token'] = generate_token()
    # Special case, we don't want update _updated field when update ui_preferences field
    if len(updates) == 2 and 'ui_preferences' in updates:
        del updates['_updated']


def after_insert_user(items):
    """
    Hook after a user was inserted.

    :param items: user fields
    :type items: dict
    :return: None
    """
    for dummy, item in enumerate(items):
        if 'back_role_super_admin' in item and item['back_role_super_admin']:
            # Allow full rights for the user on its realm
            post_internal("userrestrictrole", {
                "user": item['_id'],
                "realm": item['_realm'],
                "sub_realm": item['_sub_realm'],
                "resource": '*',
                "crud": ['create', 'read', 'update', 'delete']
            }, True)
        else:
            # Allow read right for the user on its realm
            post_internal("userrestrictrole", {
                "user": item['_id'],
                "realm": item['_realm'],
                "sub_realm": item['_sub_realm'],
                "resource": '*',
                "crud": ['read']
            }, True)


def pre_service_post(items):
    """Checks before adding a service.
    We deny in case:
     - try adding a service (not template) on a template host
     - try adding a service with the same name as an existing service on the same host

    :param items: list of items (list because can use bulk)
    :type items: list
    :return: None
    """
    hostdb = current_app.data.driver.db['host']
    servicedb = current_app.data.driver.db['service']
    for key, _ in enumerate(items):
        # return error if try adding a service (not template) on an host template
        if '_is_template' not in items[key] or not items[key]['_is_template']:
            the_host = hostdb.find_one({'_id': ObjectId(items[key]['host'])})
            if the_host['_is_template']:
                abort(make_response("Adding a non template service on a template host is forbidden",
                                    412))
        # return error if try adding a service with the same name as an existing service
        if 'host' in items[key] and 'name' in items[key]:
            same_service = servicedb.find_one({'host': ObjectId(items[key]['host']),
                                               'name': items[key]['name']})
            if same_service:
                abort(make_response("Adding a service with the same name "
                                    "as an existing one is forbidden", 412))


def keep_default_items_resource(resource, delete_request, lookup):
    """
    Keep default items, so do not delete them...

    :return: None
    """
    # pylint: disable=unused-argument
    if '_id' not in lookup:
        if resource == 'timeperiod':
            lookup['name'] = {'$nin': ['24x7', 'Never']}
        elif resource in ['realm', 'usergroup', 'hostgroup', 'servicegroup', ]:
            lookup['name'] = {'$nin': ['All']}
        elif resource == 'command':
            lookup['name'] = {'$nin': ['_internal_host_up', '_echo']}
        elif resource == 'host':
            lookup['name'] = {'$nin': ['_dummy']}
        elif resource == 'user':
            lookup['_id'] = {'$nin': [g.users_id]}
            lookup['name'] = {'$nin': ['admin']}


def keep_default_items_item(resource, item):
    """
    Before deleting an item, we check if it's a default item, if yes return 412 error, otherwise
    Eve will delete the item

    :param resource: name of the resource
    :type resource: str
    :param item: all fields / values of the item to delete
    :type item: dict
    :return:
    """
    if resource == 'timeperiod':
        if item['name'] in ['24x7', 'Never']:
            abort(make_response("This item is a default item and is protected", 412))
    elif resource in ['realm', 'usergroup', 'hostgroup', 'servicegroup', ]:
        if item['name'] == 'All':
            abort(make_response("This item is a default item and is protected", 412))
    elif resource == 'command':
        if item['name'] in ['_internal_host_up', '_echo']:
            abort(make_response("This item is a default item and is protected", 412))
    elif resource == 'host':
        if item['name'] == '_dummy':
            abort(make_response("This item is a default item and is protected", 412))
    elif resource == 'user':
        if item['name'] == 'admin':
            abort(make_response("This item is a default item and is protected", 412))
        if item['_id'] == g.users_id:
            abort(make_response("You cannot delete the user your are logged with!", 412))


def on_fetched_resource_tree(resource_name, response):
    """
    Update _parent and _tree_parents of tree resources when have restricted rights.
    Here we have the answer when get all items of a resource

    :param resource_name: name of the resource
    :type resource_name: string
    :param response: response of the get
    :type response: dict
    :return: None
    """
    if resource_name not in ['realm', 'usergroup', 'hostgroup', 'servicegroup']:
        return
    if g.get('back_role_super_admin', False):
        return
    for resp in response['_items']:
        on_fetched_item_tree(resource_name, resp)


def on_fetched_item_tree(resource_name, itemresp):
    """
    Update _parent and _tree_parents of tree resources when have restricted rights.
    Here we have the answer when get an item of a resource

    :param resource_name: name of the resource
    :type resource_name: string
    :param itemresp: response of the get
    :type itemresp: dict
    :return: None
    """
    if resource_name not in ['realm', 'usergroup', 'hostgroup', 'servicegroup']:
        return
    if g.get('back_role_super_admin', False):
        return
    resources_get = g.get('resources_get', {})

    # check _parent
    if '_parent' not in itemresp or not itemresp['_parent'] in resources_get['realm']:
        itemresp['_parent'] = None
    # check _tree_parents
    if '_tree_parents' not in itemresp:
        itemresp['_tree_parents'] = []

    for realm_id in itemresp['_tree_parents']:
        if realm_id not in resources_get['realm']:
            itemresp['_tree_parents'].remove(realm_id)


def pre_post_alias(resource_name, items):
    """
    Hook before insert.
    If `alias` field not filled, we fill it with the `name` field

    :param items: list of items (list because can use bulk)
    :type items: list
    :return: None
    """
    resource_list = current_app.config['DOMAIN']
    if 'alias' in resource_list[resource_name]['schema']:
        for key, item in enumerate(items):
            if 'alias' not in item or item['alias'] == '':
                items[key]['alias'] = items[key]['name']


def generate_token():
    """
    Generate a user token

    :return: user token
    """
    t = int(time.time() * 1000)
    return str(t) + '-' + str(uuid.uuid4())


# Backend configuration
def get_settings(prev_settings):
    """
    Get settings of application from config file to update/complete previously existing settings

    :param prev_settings: previous settings
    :type prev_settings: dict
    :return: None
    """
    settings_filenames = [
        '/usr/local/etc/alignak-backend/settings.json',
        '/etc/alignak-backend/settings.json',
        os.path.abspath('./etc/alignak-backend/settings.json'),
        os.path.abspath('./etc/settings.json'),
        os.path.abspath('../etc/settings.json'),
        os.path.abspath('./settings.json')
    ]

    # Configuration file name in environment
    if os.environ.get('ALIGNAK_BACKEND_CONFIGURATION_FILE'):
        settings_filenames = [os.path.abspath(os.environ.get('ALIGNAK_BACKEND_CONFIGURATION_FILE'))]

    for name in settings_filenames:
        if not os.path.isfile(name):
            continue

        with open(name) as json_file:
            minified = jsmin(json_file.read())
            conf = json.loads(minified)
            for key, value in iteritems(conf):
                if key.startswith('RATE_LIMIT_') and value is not None:
                    prev_settings[key] = tuple(value)
                else:
                    prev_settings[key] = value
            print("Using settings file: %s" % name)
            return name


print("--------------------------------------------------------------------------------")
print("%s, version %s" % (manifest['name'], manifest['version']))
print("Copyright %s" % manifest['copyright'])
print("License %s" % manifest['license'])
print("--------------------------------------------------------------------------------")

print("Doc: %s" % manifest['doc'])
print("Release notes: %s" % manifest['release'])
print("--------------------------------------------------------------------------------")

# Application configuration
settings = {}
settings['X_DOMAINS'] = '*'
settings['X_HEADERS'] = (
    'Authorization, If-Match, X-HTTP-Method-Override, Content-Type, Cache-Control, Pragma, Options'
)
settings['PAGINATION_LIMIT'] = 50
settings['PAGINATION_DEFAULT'] = 25
settings['AUTH_FIELD'] = None

# Use MONGO_URI to overpass the MONGO_HOST, MONGO_PORT...
# settings['MONGO_URI'] = 'mongodb://[username:password@]host1[:port1][,host2[:port2],...[,
# hostN[:portN]]][/[database][?options]]'
# settings['MONGO_URI'] = "mongodb://localhost:27017/alignak-backend"
settings['MONGO_HOST'] = 'localhost'
settings['MONGO_PORT'] = 27017
settings['MONGO_DBNAME'] = 'alignak-backend'

settings['RESOURCE_METHODS'] = ['GET', 'POST', 'DELETE']
settings['ITEM_METHODS'] = ['GET', 'PATCH', 'DELETE']
# settings['XML'] = False
settings['JSON'] = True
# Allow $regex in filtering ...
# Default is ['$where', '$regex']
settings['MONGO_QUERY_BLACKLIST'] = ['$where']

# Flask specific options; default is to listen only on locahost ...
settings['HOST'] = '127.0.0.1'
settings['PORT'] = 5000
settings['SERVER_NAME'] = None
settings['DEBUG'] = False

settings['SCHEDULER_ALIGNAK_ACTIVE'] = True
settings['SCHEDULER_ALIGNAK_PERIOD'] = 300
settings['SCHEDULER_TIMESERIES_ACTIVE'] = False
settings['SCHEDULER_TIMESERIES_PERIOD'] = 10
settings['SCHEDULER_TIMESERIES_LIMIT'] = 100
settings['SCHEDULER_GRAFANA_ACTIVE'] = False
settings['SCHEDULER_GRAFANA_PERIOD'] = 120
settings['SCHEDULER_LIVESYNTHESIS_HISTORY'] = 0
settings['SCHEDULER_TIMEZONE'] = 'Etc/GMT'
settings['JOBS'] = []

settings['ALIGNAK_URL'] = ''

# Read configuration file to update/complete the configuration
configuration_file = get_settings(settings)
print("Application configuration file: %s" % configuration_file)

if settings.get('MONGO_URI', None) is None:
    settings['MONGO_URI'] = "mongodb://%s:%s/%s" \
                            % (settings['MONGO_HOST'], settings['MONGO_PORT'],
                               settings['MONGO_DBNAME'])

if os.getenv('ALIGNAK_BACKEND_LOGGER_CONFIGURATION', None):
    settings['LOGGER'] = os.getenv('ALIGNAK_BACKEND_LOGGER_CONFIGURATION')

if os.environ.get('ALIGNAK_BACKEND_MONGO_URI'):
    settings['MONGO_URI'] = os.environ.get('ALIGNAK_BACKEND_MONGO_URI')
else:
    if os.environ.get('ALIGNAK_BACKEND_MONGO_DBNAME'):
        parsed_url = urlparse(settings['MONGO_URI'], 'mongodb:')
        settings['MONGO_URI'] = "%s://%s/%s" \
                                % (parsed_url.scheme, parsed_url.netloc,
                                   os.environ.get('ALIGNAK_BACKEND_MONGO_DBNAME'))
        if parsed_url.params:
            settings['MONGO_URI'] = "%s?%s" \
                                    % (settings['MONGO_URI'], parsed_url.params)

# scheduler config
jobs = []

if settings['SCHEDULER_TIMESERIES_ACTIVE']:
    jobs.append(
        {
            'id': 'cron_cache',
            'func': 'alignak_backend.scheduler:cron_cache',
            'args': (),
            'trigger': 'interval',
            'seconds': settings['SCHEDULER_TIMESERIES_PERIOD']
        }
    )
if settings['SCHEDULER_GRAFANA_ACTIVE']:
    jobs.append(
        {
            'id': 'cron_grafana',
            'func': 'alignak_backend.scheduler:cron_grafana',
            'args': (),
            'trigger': 'interval',
            'seconds': settings['SCHEDULER_GRAFANA_PERIOD']
        }
    )
if settings['SCHEDULER_LIVESYNTHESIS_HISTORY'] > 0:
    jobs.append(
        {
            'id': 'cron_livesynthesis_history',
            'func': 'alignak_backend.scheduler:cron_livesynthesis_history',
            'args': (),
            'trigger': 'interval',
            'seconds': settings['SCHEDULER_LIVESYNTHESIS_HISTORY']
        }
    )
if settings['SCHEDULER_ALIGNAK_ACTIVE']:
    jobs.append(
        {
            'id': 'cron_alignak',
            'func': 'alignak_backend.scheduler:cron_alignak',
            'args': (),
            'trigger': 'interval',
            'seconds': settings['SCHEDULER_ALIGNAK_PERIOD']
        }
    )

settings['JOBS'] = jobs

print("Application settings: %s" % settings)
print('MongoDB connection string: %s' % settings['MONGO_URI'])

# Add model schema to the configuration
settings['DOMAIN'] = register_models()

base_path = os.path.dirname(os.path.abspath(alignak_backend.__file__))
# print("Application base path: %s" % base_path)

app = Eve(
    settings=settings,
    validator=MyValidator,
    auth=MyTokenAuth,
    static_folder=base_path
)

if settings.get('LOGGER', None):
    # Alignak backend logging feature
    def log_endpoint(_resource, _request, _payload):  # pylint: disable=unused-argument
        """Log information about the former responded request"""
        if _request.args:
            app.logger.info('Req args: %s', _request.args.to_dict(False))
        if _request.form:
            app.logger.info('Req form: %s', _request.form.to_dict(False))
        if _request.data:
            app.logger.info('Req data: %s', _request.data)
        if _payload:
            app.logger.debug('Response: %s', _payload.response)
            if 'Exception on /' in _payload.response:
                app.logger.error('Response exception: %s', _payload.response)
    app.on_post_GET += log_endpoint
    app.on_post_POST += log_endpoint
    app.on_post_PUT += log_endpoint
    app.on_post_PATCH += log_endpoint

    # Prepare log file directory
    log_dirs = ['/var/log/alignak-backend', '/usr/local/var/log/alignak-backend',
                '/var/log/alignak', '/usr/local/var/log/alignak',
                '/var/log', '/usr/local/var/log']
    for log_dir in log_dirs:
        # Directory exists and is writable
        if os.path.isdir(log_dir) and os.access(log_dir, os.W_OK):
            print("Backend log directory: %s" % (log_dir))
            break
    else:
        log_dir = '/tmp'

    process_name = "%s_%s" % (settings['SERVER_NAME'] if settings['SERVER_NAME']
                              else 'alignak-backend',
                              settings['MONGO_DBNAME'])

    # Alignak logger configuration file
    if settings['LOGGER'] != os.path.abspath(settings['LOGGER']):
        settings['LOGGER'] = os.path.join(os.path.dirname(configuration_file), settings['LOGGER'])
    print("Backend logger configuration file: %s" % (settings['LOGGER']))

    with open(settings['LOGGER'], 'rt') as _file:
        config = json.load(_file)

        # Update the declared formats with the process name
        for formatter in config['formatters']:
            if 'format' not in config['formatters'][formatter]:
                continue
            config['formatters'][formatter]['format'] = \
                config['formatters'][formatter]['format'].replace("%(daemon)s", process_name)

        # Update the declared log file names with the log directory
        for hdlr in config['handlers']:
            if 'filename' not in config['handlers'][hdlr]:
                continue
            config['handlers'][hdlr]['filename'] = \
                config['handlers'][hdlr]['filename'].replace("%(logdir)s", log_dir)
            config['handlers'][hdlr]['filename'] = \
                config['handlers'][hdlr]['filename'].replace("%(daemon)s", process_name)
            print("Backend log file: %s" % (config['handlers'][hdlr]['filename']))

    # Configure the logger, any error will raise an exception
    logger_dictConfig(config)

app.logger.info(
    "--------------------------------------------------------------------------------")
app.logger.info("%s, version %s", manifest['name'], manifest['version'])
app.logger.info("Copyright %s", manifest['copyright'])
app.logger.info("License %s", manifest['license'])
app.logger.info(
    "--------------------------------------------------------------------------------")

app.logger.info("Doc: %s", manifest['doc'])
app.logger.info("Release notes: %s", manifest['release'])
app.logger.info(
    "--------------------------------------------------------------------------------")
# hooks pre-init
app.on_pre_GET += pre_get
app.on_pre_POST += pre_post
app.on_pre_PATCH += pre_patch
app.on_pre_DELETE += pre_delete
app.on_insert_user += pre_user_post

# Manage alias when insert
app.on_insert += pre_post_alias

app.on_update_user += pre_user_patch
app.on_inserted_user += after_insert_user
app.on_inserted_host += after_insert_host
app.on_post_POST_host += update_etag
app.on_inserted_service += after_insert_service
app.on_post_POST_service += update_etag
app.on_update_host += pre_host_patch
app.on_update_service += pre_service_patch
app.on_updated_service += after_updated_service
app.on_delete_item_host += pre_delete_host
app.on_deleted_item_host += after_delete_host
app.on_delete_item_realm += pre_delete_realm
app.on_deleted_item_realm += after_delete_realm
app.on_deleted_resource_realm += after_delete_resource_realm
app.on_update_realm += pre_realm_patch
app.on_update_usergroup += pre_usergroup_patch
app.on_update_hostgroup += pre_hostgroup_patch
app.on_update_servicegroup += pre_servicegroup_patch
app.on_insert_graphite += pre_timeseries_post
app.on_insert_influxdb += pre_timeseries_post
app.on_update_alignak += pre_alignak_patch
# check right on submit actions
app.on_pre_POST_actionacknowledge += pre_post_action_right
app.on_pre_POST_actiondowntime += pre_post_action_right
app.on_pre_POST_actionforcecheck += pre_post_action_right
app.on_pre_PATCH_actionacknowledge += pre_submit_action_right
app.on_pre_PATCH_actiondowntime += pre_submit_action_right
app.on_pre_PATCH_actionforcecheck += pre_submit_action_right
app.on_pre_DELETE_actionacknowledge += pre_submit_action_right
app.on_pre_DELETE_actiondowntime += pre_submit_action_right
app.on_pre_DELETE_actionforcecheck += pre_submit_action_right

# docs api
Bootstrap(app)
app.register_blueprint(swagger)
app.config['SWAGGER_INFO'] = {
    'title': manifest['name'],
    'version': manifest['version'],
    'description': manifest['description'],
    'contact': {
        'name': manifest['author']
    },
    'license': {
        'name': manifest['license']
    }
}
app.config['ENABLE_HOOK_DESCRIPTION'] = True

# Create default backend elements
with app.test_request_context():
    # Create default realm if not defined
    realms = app.data.driver.db['realm']
    default_realm = realms.find_one({'name': 'All'})
    if not default_realm:
        post_internal("realm", {"name": "All", "_parent": None, "_level": 0, 'default': True},
                      True)
        default_realm = realms.find_one({'name': 'All'})
        app.logger.info("Created top level realm: %s", default_realm)
    # Create default usergroup if not defined
    ugs = app.data.driver.db['usergroup']
    default_ug = ugs.find_one({'name': 'All'})
    if not default_ug:
        post_internal("usergroup", {
            "name": "All", "alias": "All users", "_parent": None, "_level": 0,
            "_realm": default_realm['_id'], "_sub_realm": True
        }, True)
        default_ug = ugs.find_one({'name': 'All'})
        app.logger.info("Created top level usergroup: %s", default_ug)
    # Create default hostgroup if not defined
    hgs = app.data.driver.db['hostgroup']
    default_hg = hgs.find_one({'name': 'All'})
    if not default_hg:
        post_internal("hostgroup", {
            "name": "All", "alias": "All hosts", "_parent": None, "_level": 0,
            "_realm": default_realm['_id'], "_sub_realm": True
        }, True)
        default_hg = hgs.find_one({'name': 'All'})
        app.logger.info("Created top level hostgroup: %s", default_hg)
    # Create default servicegroup if not defined
    sgs = app.data.driver.db['servicegroup']
    default_sg = sgs.find_one({'name': 'All'})
    if not default_sg:
        post_internal("servicegroup", {
            "name": "All", "alias": "All services", "_parent": None, "_level": 0,
            "_realm": default_realm['_id'], "_sub_realm": True
        }, True)
        default_sg = sgs.find_one({'name': 'All'})
        app.logger.info("Created top level servicegroup: %s", default_sg)
    # Create default timeperiods if not defined
    timeperiods = app.data.driver.db['timeperiod']
    always = timeperiods.find_one({'name': '24x7'})
    if not always:
        post_internal("timeperiod", {"name": "24x7",
                                     "alias": "All time default 24x7",
                                     "_realm": default_realm['_id'], "_sub_realm": True,
                                     "is_active": True,
                                     "dateranges": [{u'monday': u'00:00-24:00'},
                                                    {u'tuesday': u'00:00-24:00'},
                                                    {u'wednesday': u'00:00-24:00'},
                                                    {u'thursday': u'00:00-24:00'},
                                                    {u'friday': u'00:00-24:00'},
                                                    {u'saturday': u'00:00-24:00'},
                                                    {u'sunday': u'00:00-24:00'}]}, True)
        always = timeperiods.find_one({'name': '24x7'})
        app.logger.info("Created default Always timeperiod: %s", always)
    never = timeperiods.find_one({'name': 'Never'})
    if not never:
        post_internal("timeperiod", {"name": "Never",
                                     "alias": "No time is a good time",
                                     "_realm": default_realm['_id'], "_sub_realm": True,
                                     "is_active": True}, True)
        never = timeperiods.find_one({'name': 'Never'})
        app.logger.info("Created default Never timeperiod: %s", never)

    # Create default commands if not defined
    commands = app.data.driver.db['command']
    internal_host_up_command = commands.find_one({'name': '_internal_host_up'})
    if not internal_host_up_command:
        post_internal("command", {
            "name": "_internal_host_up",
            "alias": "Host/service is always UP/OK",
            "command_line": "_internal_host_up",
            "_realm": default_realm['_id'],
            "_sub_realm": True
        }, True)
        internal_host_up_command = commands.find_one({'name': '_internal_host_up'})
        app.logger.info("Created default Always UP command: %s", internal_host_up_command)
    echo_command = commands.find_one({'name': '_echo'})
    if not echo_command:
        post_internal("command", {
            "name": "_echo",
            "alias": "Host/service is always UP/OK",
            "command_line": "_echo",
            "_realm": default_realm['_id'],
            "_sub_realm": True
        }, True)
        echo_command = commands.find_one({'name': '_echo'})
        app.logger.info("Created default Echo command: %s", echo_command)

    # Create dummy host if not defined
    hs = app.data.driver.db['host']
    dummy_host = hs.find_one({'name': '_dummy'})
    if not dummy_host:
        post_internal("host", {
            "name": "_dummy",
            "alias": "Dummy host for services templates",
            "check_command": internal_host_up_command['_id'],
            "_realm": default_realm['_id'],
            "_is_template": True,
            '_templates_with_services': False,
            "_sub_realm": True
        }, True)
        dummy_host = hs.find_one({'name': '_dummy'})
        app.logger.info("Created dummy host: %s", dummy_host)

    # Create default username/user if not defined
    try:
        users = app.data.driver.db['user']
    except Exception as e:
        sys.exit("[ERROR] Impossible to connect to MongoDB (%s)" % e)
    super_admin_user = users.find_one({'back_role_super_admin': True})
    if not super_admin_user:
        post_internal("user", {"name": "admin", "alias": "Administrator",
                               "password": "admin",
                               "back_role_super_admin": True,
                               "is_admin": True,
                               "can_update_livestate": True,
                               "can_submit_commands": True,
                               "skill_level": 2,
                               "host_notifications_enabled": False,
                               "host_notification_period": always["_id"],
                               "service_notifications_enabled": False,
                               "service_notification_period": always["_id"],
                               "_realm": default_realm["_id"], "_sub_realm": True}, True)
        app.logger.info("Created super admin user")
        app.logger.info(
            "===============================================================================")
        app.logger.info(
            r"/!\ WARNING /!\ Change the default password according to the documentation: "
            r"http://alignak-backend.readthedocs.io/en/latest/run.html"
            r"#change-default-admin-password")
        app.logger.info(
            "===============================================================================")

    # Live synthesis management
    app.on_inserted_host += Livesynthesis.on_inserted_host
    app.on_inserted_service += Livesynthesis.on_inserted_service
    app.on_updated_host += Livesynthesis.on_updated_host
    app.on_updated_service += Livesynthesis.on_updated_service
    app.on_deleted_item_host += Livesynthesis.on_deleted_host
    app.on_deleted_item_service += Livesynthesis.on_deleted_service
    app.on_deleted_resource_host += Livesynthesis.on_deleted_resource_host
    app.on_deleted_resource_host += Livesynthesis.on_deleted_resource_service
    app.on_fetched_item_livesynthesis += Livesynthesis.on_fetched_item_history

    # Templates management
    app.on_pre_POST_host += Template.pre_post_host
    app.on_update_host += Template.on_update_host
    app.on_updated_host += Template.on_updated_host

    app.on_inserted_host += Template.on_inserted_host
    app.on_inserted_service += Template.on_inserted_service
    app.on_deleted_item_service += Template.on_deleted_item_service

    app.on_pre_POST_service += Template.pre_post_service
    app.on_update_service += Template.on_update_service
    app.on_updated_service += Template.on_updated_service

    app.on_pre_POST_user += Template.pre_post_user
    app.on_update_user += Template.on_update_user
    app.on_updated_user += Template.on_updated_user

    # Initial livesynthesis
    Livesynthesis.recalculate()

# hooks post-init
app.on_insert_realm += pre_realm_post
app.on_inserted_realm += after_insert_realm
app.on_updated_realm += after_update_realm

app.on_insert_usergroup += pre_usergroup_post
app.on_insert_hostgroup += pre_hostgroup_post
app.on_insert_servicegroup += pre_servicegroup_post

app.on_insert_actionacknowledge += pre_actionacknowledge_post
app.on_inserted_actionacknowledge += after_insert_actionacknowledge
app.on_updated_actionacknowledge += after_update_actionacknowledge

app.on_insert_actiondowntime += pre_actiondowntime_post
app.on_inserted_actiondowntime += after_insert_actiondowntime
app.on_updated_actiondowntime += after_update_actiondowntime

app.on_insert_actionforcecheck += pre_actionforcecheck_post
app.on_inserted_actionforcecheck += after_insert_actionforcecheck
app.on_updated_actionforcecheck += after_update_actionforcecheck

app.on_insert_history += pre_history_post

app.on_insert_hostescalation += pre_hostescalation_post
app.on_insert_serviceescalation += pre_serviceescalation_post

app.on_insert_logcheckresult += pre_logcheckresult_post
app.on_inserted_logcheckresult += after_insert_logcheckresult
app.on_inserted_logcheckresult += Timeseries.after_inserted_logcheckresult

app.on_pre_DELETE += keep_default_items_resource
app.on_delete_item += keep_default_items_item

app.on_insert_service += pre_service_post

# hook for tree resources
app.on_fetched_resource += on_fetched_resource_tree
app.on_fetched_item += on_fetched_item_tree

# Start scheduler (internal cron)
if settings['JOBS']:
    with app.test_request_context():
        scheduler = APScheduler()
        scheduler.init_app(app)
        scheduler.start()


@app.route("/login", methods=['POST'])
def login_app():  # pylint: disable=inconsistent-return-statements
    """
    Log in to backend
    """
    posted_data = None
    if request.form:
        posted_data = request.form
    else:
        if request.json:
            posted_data = request.json
    if not posted_data:
        abort(401, description='No data provided in the login request')

    if 'username' not in posted_data or 'password' not in posted_data:
        abort(
            401,
            description='Missing credentials in posted data (username and password are mandatory)'
        )
    elif not posted_data['username'] or not posted_data['password']:
        abort(
            401,
            description='Username and password must be provided as credentials for login.'
        )
    else:
        _users = app.data.driver.db['user']
        user = _users.find_one({'name': posted_data['username']})
        if user:
            if check_password_hash(user['password'], posted_data['password']):
                if 'action' in posted_data:
                    if posted_data['action'] == 'generate' or not user['token']:
                        token = generate_token()
                        _users.update({'_id': user['_id']}, {'$set': {'token': token}})
                        return jsonify({'token': token})
                elif not user['token']:
                    token = generate_token()
                    _users.update({'_id': user['_id']}, {'$set': {'token': token}})
                    return jsonify({'token': token})
                return jsonify({'token': user['token']})
        abort(401, description='Please provide proper credentials')


@app.route("/logout", methods=['POST'])
def logout_app():
    """
    Log out from backend
    """
    return 'ok'


@app.route("/backendconfig")
def backend_config():
    """
    Offer route to get the backend config
    """
    my_config = {"PAGINATION_LIMIT": settings['PAGINATION_LIMIT'],
                 "PAGINATION_DEFAULT": settings['PAGINATION_DEFAULT']}
    return jsonify(my_config)


@app.route("/version")
def backend_version():
    """
    Offer route to get the backend config
    """
    my_version = {"version": manifest['version']}
    return jsonify(my_version)


@app.route("/cron_alignak")
def cron_alignak():
    """
    Cron used to notify Alignak about some events: configuration reload, ...

    :return: None
    """
    with app.test_request_context():
        alignak_notifications_db = app.data.driver.db['alignak_notifications']
        if not alignak_notifications_db.count():
            return

        current_app.logger.warning("[cron_alignak]: %d notifications"
                                   % alignak_notifications_db.count())

        sent = set()
        notifications = alignak_notifications_db.find()
        for data in notifications:
            current_app.logger.warning("[cron_alignak]: %s" % data)
            headers = {'Content-Type': 'application/json'}
            params = {
                "event": data['event'],
                "parameters": data['parameters']
            }
            url = "%s/%s" % (settings['ALIGNAK_URL'], data['notification'])

            try:
                if data['notification'] not in sent:
                    current_app.logger.warning("[cron_alignak]: Notifying Alignak: %s / %s"
                                               % (url, params))
                    response = requests.post(url=url, headers=headers, json=params, timeout=10)
                    current_app.logger.warning("[cron_alignak]: Notified, response: %s"
                                               % response.json())
            # except NewConnectionError:
            #     current_app.logger.warning("Alignak is not available for notification")
            except Exception as exp:
                current_app.logger.warning("[cron_alignak]: Alignak notification failed: %s..."
                                           % str(exp))
            finally:
                # Delete
                lookup = {"_id": data['_id']}
                deleteitem_internal('alignak_notifications', False, False, **lookup)
                current_app.logger.warning("[cron_alignak]: Deleted notification: %s" % data['_id'])
                # Sent!
                sent.add(data['notification'])


@app.route("/cron_timeseries")
def cron_timeseries():
    """
    Cron used to add perfdata from retention to timeseries databases

    :return: None
    """
    with app.test_request_context():
        timeseriesretention_db = current_app.data.driver.db['timeseriesretention']
        graphite_db = current_app.data.driver.db['graphite']
        influxdb_db = current_app.data.driver.db['influxdb']
        if timeseriesretention_db.count() > 0:
            tsc = timeseriesretention_db.find({'graphite': {'$ne': None}})\
                .sort('_id')\
                .limit(settings['SCHEDULER_TIMESERIES_LIMIT'])
            if tsc.count():
                current_app.logger.warning("[cron_timeseries]: "
                                           "flushing %d Graphite metrics" % tsc.count())
            for data in tsc:
                graphite = graphite_db.find_one({'_id': data['graphite']})
                if not Timeseries.send_to_timeseries_graphite([data], graphite):
                    break
                lookup = {"_id": data['_id']}
                deleteitem_internal('timeseriesretention', False, False, **lookup)

            tsc = timeseriesretention_db.find({'influxdb': {'$ne': None}})\
                .sort('_id')\
                .limit(settings['SCHEDULER_TIMESERIES_LIMIT'])
            if tsc.count():
                current_app.logger.warning("[cron_timeseries]: "
                                           "flushing %d InfluxDB metrics" % tsc.count())
            for data in tsc:
                influxdb = influxdb_db.find_one({'_id': data['influxdb']})
                if not Timeseries.send_to_timeseries_influxdb([data], influxdb):
                    break
                lookup = {"_id": data['_id']}
                deleteitem_internal('timeseriesretention', False, False, **lookup)


if settings.get('GRAFANA_DATASOURCE', True):
    def get_grafana_configuration(cfg_file_name, queries):
        """
        Get the configured target queries

        :param cfg_file_name: short filenam for the queries configuration (eg. grafana_queries.json)
        :type cfg_file_name: string
        :param queries: previous settings
        :type queries: dict
        :return: None
        """
        filenames = []
        if os.path.isfile(os.path.abspath(cfg_file_name)):
            filenames = [os.path.abspath(cfg_file_name)]
        elif isinstance(cfg_file_name, list):
            filenames = cfg_file_name
        else:
            filenames = [
                '/usr/local/etc/alignak-backend/%s' % cfg_file_name,
                '/etc/alignak-backend/%s' % cfg_file_name,
                'etc/alignak-backend/%s' % cfg_file_name,
                os.path.abspath('./etc/%s' % cfg_file_name),
                os.path.abspath('../etc/%s' % cfg_file_name),
                os.path.abspath('./%s' % cfg_file_name)
            ]

        for name in filenames:
            if os.path.isfile(name):
                with open(name) as json_file:
                    minified = jsmin(json_file.read())
                    conf = json.loads(minified)
                    for key, value in iteritems(conf):
                        queries[key] = value
                    print("Using Grafana configuration file: %s" % name)
                    return
    # The default minimum target queries...
    target_queries = {
        "Hosts": {
            'endpoint': "host",
            'query': {"_is_template": False}
        },
        "Services": {
            'endpoint': "service",
            'query': {"_is_template": False},
            'join': ('host', 'host', 'name')
        }
    }
    with app.app_context():
        filename = settings.get('GRAFANA_DATASOURCE_QUERIES', 'grafana_queries.json')
        if os.environ.get('ALIGNAK_BACKEND_GRAFANA_DATASOURCE_QUERIES'):
            filename = os.environ.get('ALIGNAK_BACKEND_GRAFANA_DATASOURCE_QUERIES')
        get_grafana_configuration(filename, target_queries)
        current_app.logger.info("Grafana - queries: %s", target_queries)

        # The default minimum table configuration...
        table_fields = {
            "host": ["name"]
        }
        filename = settings.get('GRAFANA_DATASOURCE_TABLES', 'grafana_tables.json')
        if os.environ.get('ALIGNAK_BACKEND_GRAFANA_DATASOURCE_TABLES'):
            filename = os.environ.get('ALIGNAK_BACKEND_GRAFANA_DATASOURCE_TABLES')
        get_grafana_configuration(filename, table_fields)
        current_app.logger.info("Grafana - tables: %s", table_fields)

    @app.route("/search", methods=['OPTIONS', 'POST'])
    def grafana_search(engine='jsonify'):
        # pylint: disable=too-many-locals
        """
        Request available queries

        Posted data: {u'target': u''}

        Return the list of available target queries

        :return: See upper comment
        :rtype: list
        """
        target = None
        try:
            target = request.json.get("target")
        except Exception as e:
            abort(404, description='Bad format for posted data: %s' % str(e))

        with app.app_context():
            resp = []
            if not target:
                resp = sorted(target_queries.keys())

            if engine == 'jsonify':
                return jsonify(resp)
            return json.dumps(resp)

    @app.route("/query", methods=['OPTIONS', 'POST'])
    def grafana_query(engine='jsonify'):
        # pylint: disable=too-many-locals
        """
        Request object passed to datasource.query function:

        {
          "range": { "from": "2015-12-22T03:06:13.851Z", "to": "2015-12-22T06:48:24.137Z" },
          "interval": "5s",
          "targets": [
            { "refId": "B", "target": "target 1" },
            { "refId": "A", "target": "target 2" }
          ],
          "format": "json",
          "maxDataPoints": 2495 //decided by the panel
        }

        Only the first target is considered. If several targets are required, an error is raised.

        The target is a string that is searched in the target_queries dictionary. If found
        the corresponding query is executed and the result is returned.

        Table response from datasource.query. An array of:

        [
          {
            "type": "table",
            "columns": [
              {
                "text": "Time",
                "type": "time",
                "sort": true,
                "desc": true,
              },
              {
                "text": "mean",
              },
              {
                "text": "sum",
              }
            ],
            "rows": [
              [
                1457425380000,
                null,
                null
              ],
              [
                1457425370000,
                1002.76215352,
                1002.76215352
              ],
            ]
          }
        ]
        :return: See upper comment
        :rtype: list
        """
        posted_data = request.json
        targets = None
        target = None
        try:
            targets = posted_data.get("targets")
            assert targets
            assert len(targets) == 1
            target = targets[0]
            target = target.get("target")
        except AssertionError:
            abort(404, description='Only one target is supported by this datasource.')
        except Exception as e:
            abort(404, description='Bad format for posted data: %s' % str(e))

        with app.app_context():
            join = None
            if target in target_queries.keys():
                endpoint = target_queries[target]['endpoint']
                schema = settings['DOMAIN'][endpoint]['schema']
                search = target_queries[target]['query']
                if 'join' in target_queries[target]:
                    join = target_queries[target]['join']
                field = None
                current_app.logger.debug("Grafana - query found in the configured queries: %s",
                                         endpoint, search)
            else:
                query = target.split(':')
                if len(query) < 3:
                    abort(404, description='Bad format for query: %s. Query must be '
                                           'something like endpoint:field:value.' % targets)

                # Get and check valid endpoint
                endpoint = query[0]
                if endpoint not in settings['DOMAIN'].keys():
                    abort(404, description='Bad endpoint for query: %s.' % endpoint)
                schema = settings['DOMAIN'][endpoint]['schema']

                # Get and check valid field name in the endpoint
                field = query[1]
                if field not in schema:
                    abort(404, description='Bad field name (%s) for the endpoint: '
                                           '%s.' % (field, endpoint))

                embedded = []
                # Get and convert value according to the field type
                value = query[2]
                field_type = schema[field]['type']
                regex = False
                if '/' in value and value[0] == '/':
                    regex = True
                    value = value[1:]
                if field_type == 'float':
                    value = float(value)
                if field_type == 'integer':
                    value = int(value)
                if field_type == 'boolean':
                    value = bool(value)
                if field_type == 'list':
                    value = value
                if field_type == 'dict':
                    value = value
                if field_type == 'objectid':
                    embedded.append({
                        'resource': schema[field]['data_relation']['resource'], '_id': value})

                current_app.logger.debug("Grafana - built a query: %s - %s (%s) = %s",
                                         endpoint, field, field_type, value)

                search = {
                    "_is_template": False,
                    field: value if not regex else {"$regex": ".*%s.*" % value}
                }

            resp = [
                {
                    "type": "table",
                    "columns": [],
                    "rows": []
                }
            ]
            fields_list = table_fields[endpoint]
            if field and field not in fields_list:
                fields_list.append(field)

            for field_name in fields_list:
                field_type = schema[field_name]['type']
                field_title = schema[field_name]['title']
                resp[0]["columns"].append({"text": field_title, "type": field_type})

            db_collection = current_app.data.driver.db[endpoint]
            current_app.logger.debug("Grafana - DB query: %s", json.dumps(search))
            got = db_collection.find(search)
            for element in got:
                if join:
                    current_app.logger.debug("Grafana - join query: %s / %s / %s",
                                             join[0], join[1], join[2])
                    # Second join field is the collection to search in
                    db_join = current_app.data.driver.db[join[1]]
                    # First join field is the _id to search for
                    joined = db_join.find_one(element[join[0]])
                    # Third join field is the field to get
                    element[join[0]] = joined[join[2]]

                item = []
                for field_name in fields_list:
                    if isinstance(element[field_name], list):
                        item.append(','.join(element[field_name]))
                    elif field_name in ['ls_last_check', 'ls_next_check', 'ls_last_state_changed',
                                        'ls_last_hard_state_changed', 'ls_last_time_up',
                                        'ls_last_time_down', 'ls_last_time_unknown',
                                        'ls_last_time_unreachable', 'ls_last_time_ok',
                                        'ls_last_time_warning', 'ls_last_time_critical']:
                        value = datetime.utcfromtimestamp(float(element[field_name]))
                        value = value.strftime('%a, %d %b %Y %H:%M:%S GMT')
                        item.append(value)
                    elif isinstance(element[field_name], datetime):
                        value = datetime.utcfromtimestamp(float(element[field_name]))
                        value = value.strftime('%a, %d %b %Y %H:%M:%S GMT')
                        item.append(value)
                    else:
                        item.append(element[field_name])
                current_app.logger.debug("Grafana - found: %s", item)
                resp[0]["rows"].append(item)

            current_app.logger.debug("Grafana - response: %s", resp)

            if engine == 'jsonify':
                return jsonify(resp)

            return json.dumps(resp)

    @app.after_request
    def after_request(response):
        """Send correct headers for CORS because Eve do not manage the headers
        for the endpoints that are not part of the inner API"""
        origin = request.headers.get('Origin')
        response.headers.set('Access-Control-Allow-Origin', origin)
        response.headers.set('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.set('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        # response.headers.set('Access-Control-Allow-Credentials', 'true')
        return response

    @app.route("/annotations", methods=['OPTIONS', 'POST'])
    def grafana_annotations(engine='jsonify'):
        # pylint: disable=too-many-locals
        """
        The annotation request from the Simple JSON Datasource is a POST request to the /annotations
        endpoint in your datasource. The JSON request body looks like this:

        {
          "range": {
            "from": "2016-04-15T13:44:39.070Z",
            "to": "2016-04-15T14:44:39.070Z"
          },
          "rangeRaw": {
            "from": "now-1h",
            "to": "now"
          },
          "annotation": {
            "name": "deploy",
            "datasource": "Simple JSON Datasource",
            "iconColor": "rgba(255, 96, 96, 1)",
            "enable": true,
            "query": "#deploy"
          }
        }

        Grafana expects a response containing an array of annotation objects
        in the following format:
        [
          {
            annotation: annotation, // The original annotation sent from Grafana.
            time: time, // Time since UNIX Epoch in milliseconds. (required)
            title: title, // The title for the annotation tooltip. (required)
            tags: tags, // Tags for the annotation. (optional)
            text: text // Text for the annotation. (optional)
          }
        ]

        :return: See upper comment
        :rtype: list
        """
        posted_data = request.json
        annotation = None
        annotation_query = None
        try:
            annotation = posted_data.get("annotation")
            annotation_query = annotation.get("query")
            time_frame = posted_data.get("range")
            range_from = time_frame.get("from")
            range_from_date = parser.parse(range_from)
            range_to = time_frame.get("to")
            range_to_date = parser.parse(range_to)
        except Exception as e:
            abort(404, description='Bad format for posted data: %s' % str(e))

        with app.app_context():
            resp = []
            hosts = []
            services = []

            query = annotation_query.split(':')
            if len(query) < 3:
                abort(404,
                      description='Bad format for query: %s. Query must be '
                                  'something like endpoint:type:target.' % annotation_query)

            endpoint = query[0]
            if endpoint not in ['history', 'livestate']:
                abort(404,
                      description='Bad endpoint for query: %s. '
                                  'Only history and livestate are available.' % annotation_query)

            event_type = query[1]
            hosts = query[2]
            hosts = hosts.replace("{", "")
            hosts = hosts.replace("}", "")
            hosts = hosts.split(",")
            if len(query) > 3:
                services = query[3]
                services = services.replace("{", "")
                services = services.replace("}", "")
                services = services.split(",")

            if endpoint == 'history':
                history_db = current_app.data.driver.db['history']
                search = {
                    "type": event_type,
                    "host_name": {"$in": hosts},
                    "_created": {"$gte": range_from_date, "$lte": range_to_date},
                }
                if services:
                    search["service_name"] = {"$in": services}

                history = history_db.find(search)

                for event in history:
                    title = event['message']
                    if "host_name" in event and event["host_name"]:
                        if "service_name" in event and event["service_name"]:
                            title = "%s/%s - %s" \
                                    % (event["host_name"], event["service_name"], event["message"])
                        else:
                            title = "%s - %s" \
                                    % (event["host_name"], event["message"])
                    item = {
                        "annotation": annotation,
                        "time": event['_updated'],
                        "title": title,
                        "tags": [event["type"]],
                        "text": event['message']
                    }
                    resp.append(item)

            if endpoint == 'livestate':
                host_db = current_app.data.driver.db['host']
                search = {
                    "name": {"$in": hosts}, "_is_template": False
                }
                if services:
                    search["name"] = {"$in": services}

                hosts = host_db.find(search)
                for host in hosts:
                    text = "%s: %s (%s) - %s" % (host['name'],
                                                 host['ls_state'], host['ls_state_type'],
                                                 host['ls_output'])
                    item = {
                        "annotation": annotation,
                        "time": host['_updated'],
                        "title": host['alias'],
                        "tags": host['tags'],
                        "text": text
                    }
                    resp.append(item)

            if engine == 'jsonify':
                return jsonify(resp)

            return json.dumps(resp)


@app.route("/cron_grafana", methods=['GET'])
def cron_grafana(engine='jsonify'):
    """
    Cron used to add / update grafana dashboards

    :return: Number of dashboard created
    :rtype: dict
    """
    # pylint: disable=too-many-nested-blocks
    # pylint: disable=too-many-locals
    try:
        forcegenerate = request.args.get('forcegenerate')
        if request.remote_addr not in settings['IP_CRON']:
            print('Access denied for %s' % request.remote_addr)
            with app.app_context():
                app.logger.warning('Access denied for %s', request.remote_addr)
            return make_response("Access denied from remote host %s" % request.remote_addr, 412)
    except Exception:
        forcegenerate = None

    with app.test_request_context():
        resp = {}
        hosts_db = current_app.data.driver.db['host']
        services_db = current_app.data.driver.db['service']
        grafana_db = current_app.data.driver.db['grafana']

        for grafana in grafana_db.find():
            # Create a grafana instance
            graf = Grafana(grafana)
            resp[grafana['name']] = {
                "connection": graf.connection,
                "created_dashboards": []
            }
            if not graf.connection:
                app.logger.warning("[cron_grafana] %s has no connection", grafana['name'])
                continue

            app.logger.info("[cron_grafana] Grafana: %s", grafana['name'])

            search = {'_is_template': False}
            search['_realm'] = {"$in": graf.realms}
            if len(graf.realms) == 1:
                search['_realm'] = graf.realms[0]

            if forcegenerate is not None:
                app.logger.info("[cron_grafana] Force regeneration of '%s' dashboards",
                                grafana['name'])
            else:
                search['ls_grafana'] = False
                search['ls_perf_data'] = {"$ne": ""}
                search['ls_last_check'] = {"$ne": 0}

            hosts = hosts_db.find(search)
            for host in hosts:
                app.logger.info("[cron_grafana] host: %s", host['name'])

                # if this host do not have a TS datasource (influxdb, graphite) for grafana,
                # do not try to create a dashboard (test before trying to create...)
                if host['_realm'] not in graf.timeseries:
                    app.logger.info("[cron_grafana] Host '%s' is not in a timeseries enabled realm",
                                    host['name'])
                    app.logger.info("[cron_grafana] - host realm: %s", host['_realm'])
                    app.logger.info("[cron_grafana] - Grafana TS realms: %s",
                                    graf.timeseries)
                    continue

                created = graf.create_dashboard(host)
                if created:
                    app.logger.info("[cron_grafana] created a dashboard for '%s'...",
                                    host['name'])
                    if host['name'] not in resp[grafana['name']]['created_dashboards']:
                        resp[grafana['name']]['created_dashboards'].append(host['name'])
                else:
                    app.logger.info("[cron_grafana] dashboard creation failed for '%s'...",
                                    host['name'])

            if forcegenerate is not None:
                continue

            # manage the cases hosts have new services or hosts that do not have ls_perf_data
            hosts_dashboards = {}
            search = {'ls_grafana': False, '_is_template': False,
                      'ls_perf_data': {"$ne": ""}, 'ls_last_check': {"$ne": 0},
                      '_realm': {"$in": graf.realms}}
            if len(graf.realms) == 1:
                search['_realm'] = graf.realms[0]

            services = services_db.find(search)
            for service in services:
                if service['host'] in hosts_dashboards:
                    continue

                host = hosts_db.find_one({'_id': service['host']})
                if host['_is_template']:
                    continue

                created = graf.create_dashboard(host)
                if created:
                    app.logger.info("[cron_grafana] created a dashboard for '%s/%s'",
                                    host['name'], service['name'])
                    resp[grafana['name']]['created_dashboards'].append("%s/%s"
                                                                       % (host['name'],
                                                                          service['name']))
                else:
                    app.logger.info("[cron_grafana] dashboard creation failed for '%s/%s'",
                                    host['name'], service['name'])
                hosts_dashboards[service['host']] = True

        if engine == 'jsonify':
            return jsonify(resp)

        return json.dumps(resp)


@app.route('/cron_livesynthesis_history')
def cron_livesynthesis_history():
    """
    Cron used to generate new history line for livesynthesis (+ delete too old entries)

    :return: empty dictionary
    :rtype: dict
    """
    minutes = settings['SCHEDULER_LIVESYNTHESIS_HISTORY']
    with app.test_request_context():
        # for each livesynthesis, add into internal livesynthesisretention endpoint
        livesynthesis_db = current_app.data.driver.db['livesynthesis']
        livesynthesisretention_db = current_app.data.driver.db['livesynthesisretention']
        livesynthesis = livesynthesis_db.find()
        for livesynth in livesynthesis:
            livesynth['livesynthesis'] = livesynth['_id']
            for prop in ['_id', '_created', '_updated', '_realm', '_users_read']:
                if prop in livesynth:
                    del livesynth[prop]
            post_internal("livesynthesisretention", livesynth, True)
            # delete older data
            if minutes > 0:
                items = livesynthesisretention_db.find(
                    {"_created": {"$lt": (datetime.utcnow() - timedelta(seconds=60 * minutes))}})
                for item in items:
                    lookup = {"_id": item['_id']}
                    deleteitem_internal('livesynthesisretention', False, False, **lookup)
        return jsonify({})


@app.route('/docs')
def redir_index():
    """
    Redirect /docs to /docs/index.html

    :return: redirect to endpoint /docs/index.html
    """
    return redirect('/docs/index.html')


@app.route('/docs/<path:path>')
def index(path):
    """
    Deliver static files of swagger-ui folder

    :param path: path + files of swagger-ui to load
    :type path: string
    :return:
    """
    return send_from_directory(base_path, 'swagger-ui/' + path)


def main():
    """Called when this module is started from Python shell"""
    print("--------------------------------------------------------------------------------")
    print("Running `python app.py` is no more supported. Use 'alignak-backend' shell script.")
    print("--------------------------------------------------------------------------------")
    sys.exit(1)


if __name__ == "__main__":
    main()
