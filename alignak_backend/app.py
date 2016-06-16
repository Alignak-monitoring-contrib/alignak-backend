#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    ``alignak_backend.app`` module

    This module manages the backend, its configuration and starts the backend
"""

import sys
import traceback
import os
import time
import uuid
import json
import re
from collections import OrderedDict
from datetime import timedelta
from configparser import ConfigParser

from eve import Eve
from eve.auth import TokenAuth
from eve.io.mongo import Validator
from eve.methods.post import post_internal
from eve.methods.patch import patch_internal
from eve.methods.delete import deleteitem_internal
from eve.utils import debug_error_message
from werkzeug.security import check_password_hash, generate_password_hash
from flask_bootstrap import Bootstrap
from flask_apscheduler import APScheduler
from eve_docs import eve_docs
from flask import current_app, g, request, abort, jsonify, make_response

from alignak_backend.models import register_models
from alignak_backend import manifest
from alignak_backend.log import Log
from alignak_backend.livesynthesis import Livesynthesis
from alignak_backend.livestate import Livestate
from alignak_backend.template import Template
from alignak_backend.timeseries import Timeseries

_subcommands = OrderedDict()


def register_command(description):
    """Register commands usable from command line"""
    def decorate(f):
        """Create decorator to be used for functions"""
        _subcommands[f.__name__] = (description, f)
        return f
    return decorate


class MyTokenAuth(TokenAuth):
    """
    Class to manage authentication
    """
    children_realms = {}
    parent_realms = {}

    """Authentication token class"""
    def check_auth(self, token, allowed_roles, resource, method):
        """
        Check if account exist and get roles for this user

        :param token: token for auth
        :type username: str
        :param allowed_roles:
        :type allowed_roles:
        :param resource: name of the resource requested by user
        :type resource: str
        :param method: method used: GET | POST | PATCH | DELETE
        :type method: str
        :return: True if user exist and password is ok or if no roles defined, otherwise False
        :rtype: bool
        """
        _users = current_app.data.driver.db['user']
        user = _users.find_one({'token': token})
        if user:
            g.updateRealm = False
            # get children of realms for rights
            realmsdrv = current_app.data.driver.db['realm']
            allrealms = realmsdrv.find()
            self.children_realms = {}
            self.parent_realms = {}
            for realm in allrealms:
                self.children_realms[realm['_id']] = realm['_all_children']
                self.parent_realms[realm['_id']] = realm['_tree_parents']

            g.back_role_super_admin = user['back_role_super_admin']
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
                self.add_resources_realms('read', rights, False, g.resources_get, get_parents)
                self.add_resources_realms('read', rights, True, g.resources_get_custom)
                self.add_resources_realms('create', rights, False, g.resources_post)
                self.add_resources_realms('update', rights, False, g.resources_patch)
                self.add_resources_realms('update', rights, True, g.resources_patch_custom)
                self.add_resources_realms('delete', rights, False, g.resources_delete)
                self.add_resources_realms('delete', rights, True, g.resources_delete_custom)
            for resource in g.resources_get:
                g.resources_get[resource] = list(set(g.resources_get[resource]))
                if resource in g.resources_get_custom:
                    g.resources_get_custom[resource] = list(set(g.resources_get_custom[resource]))
                g.resources_get_parents[resource] = [item for item in get_parents[resource]
                                                     if item not in g.resources_get[resource]]
            for resource in g.resources_post:
                g.resources_post[resource] = list(set(g.resources_post[resource]))
            for resource in g.resources_patch:
                g.resources_patch[resource] = list(set(g.resources_patch[resource]))
            for resource in g.resources_delete:
                g.resources_delete[resource] = list(set(g.resources_delete[resource]))
            g.users_id = user['_id']
        return user

    def add_resources_realms(self, right, data, custom, resource, parents=None):
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
        :param parents: variable where store parents realms (required only for read right)
        :type parents: dict or None
        :return: None
        """
        # pylint: disable=too-many-arguments
        search_field = right
        if custom:
            search_field = 'custom'
        if data['crud'] == search_field:
            if data['resource'] not in resource:
                resource[data['resource']] = []
            if right == 'read' and not custom and data['resource'] not in parents:
                parents[data['resource']] = []
            resource[data['resource']].append(data['realm'])
            if right == 'read' and not custom:
                parents[data['resource']].extend(self.parent_realms[data['realm']])
            if data['sub_realm']:
                resource[data['resource']].extend(self.children_realms[data['realm']])


class MyValidator(Validator):
    """Specific validator for data model fields types extension"""
    # pylint: disable=unused-argument
    def _validate_title(self, title, field, value):
        """Validate 'title' field (always valid)"""
        return


def pre_get(resource, user_request, lookup):
    """
    Hook before get data. Add filter depend on roles of user

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
    # Only in case not super-admin
    if resource != 'user':
        # get all resources we can have rights in read
        resources_get = g.get('resources_get', {})
        resources_get_parents = g.get('resources_get_parents', {})
        resources_get_custom = g.get('resources_get_custom', {})
        users_id = g.get('users_id', {})
        if resource not in resources_get and resource not in resources_get_custom:
            lookup["_id"] = 0
        else:
            # add search on realms
            if 'realm' in app.settings['DOMAIN'][resource]['schema']:
                lookup['realm'] = {'$in': resources_get[resource]}
            else:
                if resource not in resources_get:
                    resources_get[resource] = []
                if resource not in resources_get_parents:
                    resources_get_parents[resource] = []
                if resource not in resources_get_custom:
                    resources_get_custom[resource] = []
                lookup['$or'] = [{'_realm': {'$in': resources_get[resource]}},
                                 {'$and': [{'_sub_realm': True},
                                           {'_realm': {'$in': resources_get_parents[resource]}}]},
                                 {'$and': [{'_users_read': users_id},
                                           {'_realm': {'$in': resources_get_custom[resource]}}]}]


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
        if '_parent' not in item:
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
        if len(original['_tree_parents']) > 0:
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


def after_update_realm(updated, original):
    """
    Hook update tree children on realm parent after update tree children realm

    :param updates: modified fields
    :type updates: dict
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
            if parent:
                if added_children:
                    for d in diff:
                        parent['_all_children'].append(d)
                else:
                    for d in diff:
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
    if len(item['_children']) > 0:
        abort(409, description=debug_error_message("Item have children, so can't delete it"))


def after_delete_realm(item):
    """
    Hook after realm deletion. Update tree children of parent realm

    :param item: fields of the item / record
    :type item: dict
    :return: None
    """
    realmsdrv = current_app.data.driver.db['realm']
    if len(item['_tree_parents']) > 0:
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


def pre_user_post(items):
    """
    Hook before insert.
    When add user, hash the backend password of the user

    :param items: list of items (list because can use bulk)
    :type items: list
    :return: None
    """
    for index, item in enumerate(items):
        if 'password' in item:
            items[index]['password'] = generate_password_hash(item['password'])


def pre_user_patch(updates, original):
    """
    Hook before update.
    When update user, hash the backend password of the user if try to change it

    :param updates: list of fields user try to update
    :type updates: dict
    :param original: list of original fields
    :type original: dict
    :return: None
    """
    # pylint: disable=unused-argument
    if 'password' in updates:
        updates['password'] = generate_password_hash(updates['password'])


def generate_token():
    """
    Generate a user token

    :return: user token
    """
    t = int(time.time() * 1000)
    return str(t) + '-' + str(uuid.uuid4())


def get_settings(prev_settings):
    """
    Get settings of application from config file to update/complete previously existing settings

    :param prev_settings: previous settings
    :type prev_settings: dict
    :return: None
    """
    settings_filenames = [
        '/usr/local/etc/alignak_backend/settings.json',
        '/etc/alignak_backend/settings.json',
        os.path.abspath('./etc/settings.json'),
        os.path.abspath('../etc/settings.json'),
        os.path.abspath('./settings.json')
    ]

    # pylint: disable=anomalous-backslash-in-string
    comment_re = re.compile(
        '(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
        re.DOTALL | re.MULTILINE
    )
    for filename in settings_filenames:
        if os.path.isfile(filename):
            with open(filename) as stream:
                content = ''.join(stream.readlines())
                # Looking for comments
                match = comment_re.search(content)
                while match:
                    # single line comment
                    content = content[:match.start()] + content[match.end():]
                    match = comment_re.search(content)

                conf = json.loads(content)
                for key, value in conf.iteritems():
                    if key.startswith('RATE_LIMIT_') and value is not None:
                        prev_settings[key] = tuple(value)
                    else:
                        prev_settings[key] = value
                return


print "--------------------------------------------------------------------------------"
print "%s, version %s" % (manifest['name'], manifest['version'])
print "Copyright %s" % manifest['copyright']
print "License %s" % manifest['license']
print "--------------------------------------------------------------------------------"

print "Doc: %s" % manifest['doc']
print "Release notes: %s" % manifest['release']
print "--------------------------------------------------------------------------------"

# Application configuration
settings = {}
settings['X_DOMAINS'] = '*'
settings['X_HEADERS'] = (
    'Authorization, If-Match,'
    ' X-HTTP-Method-Override, Content-Type'
)
settings['PAGINATION_LIMIT'] = 50
settings['PAGINATION_DEFAULT'] = 25

settings['MONGO_HOST'] = 'localhost'
settings['MONGO_PORT'] = 27017
settings['MONGO_DBNAME'] = 'alignak-backend'

settings['RESOURCE_METHODS'] = ['GET', 'POST', 'DELETE']
settings['ITEM_METHODS'] = ['GET', 'PATCH', 'DELETE']
settings['XML'] = False
# Allow $regex in filtering ...
# Default is ['$where', '$regex']
settings['MONGO_QUERY_BLACKLIST'] = ['$where']

# Flask specific options; default is to listen only on locahost ...
settings['HOST'] = '127.0.0.1'
settings['PORT'] = 5000
settings['SERVER_NAME'] = None
settings['DEBUG'] = False

settings['SCHEDULER_ACTIVE'] = False

settings['GRAPHITE_HOST'] = ''
settings['GRAPHITE_PORT'] = 2004

settings['INFLUXDB_HOST'] = ''
settings['INFLUXDB_PORT'] = 8086
settings['INFLUXDB_LOGIN'] = 'root'
settings['INFLUXDB_PASSWORD'] = 'root'
settings['INFLUXDB_DATABASE'] = 'alignak'

# Read configuration file to update/complete the configuration
get_settings(settings)

# scheduler config
if settings['SCHEDULER_ACTIVE']:
    settings['JOBS'] = [
        {
            'id': 'cron_cache',
            'func': 'alignak_backend.scheduler:cron_cache',
            'args': (),
            'trigger': 'interval',
            'seconds': 60
        }
    ]
    settings['SCHEDULER_TIMEZONE'] = 'Etc/GMT'


print "Application settings: %s" % settings

# Add model schema to the configuration
settings['DOMAIN'] = register_models()

app = Eve(
    settings=settings,
    validator=MyValidator,
    auth=MyTokenAuth
)
# hooks pre-init
app.on_pre_GET += pre_get
app.on_insert_user += pre_user_post
app.on_update_user += pre_user_patch
app.on_delete_item_realm += pre_delete_realm
app.on_deleted_item_realm += after_delete_realm
app.on_update_realm += pre_realm_patch

# docs api
Bootstrap(app)
app.register_blueprint(eve_docs, url_prefix='/docs')

# Create default account when have no user.
with app.test_request_context():
    # Create default realm if not defined
    realms = app.data.driver.db['realm']
    default_realm = realms.find_one({'name': 'All'})
    if not default_realm:
        post_internal("realm", {"name": "All", "_parent": None, "_level": 0, 'default': True},
                      True)
        default_realm = realms.find_one({'name': 'All'})
        print "Created top level realm:", default_realm
    # Create default timeperiod if not defined
    timeperiods = app.data.driver.db['timeperiod']
    default_timeperiod = timeperiods.find_one({'name': '24x7'})
    if not default_timeperiod:
        post_internal("timeperiod", {"name": "24x7",
                                     "alias": "All time default 24x7",
                                     "_realm": default_realm['_id'],
                                     "is_active": True,
                                     "dateranges": [{u'monday': u'00:00-24:00'},
                                                    {u'tuesday': u'00:00-24:00'},
                                                    {u'wednesday': u'00:00-24:00'},
                                                    {u'thursday': u'00:00-24:00'},
                                                    {u'friday': u'00:00-24:00'},
                                                    {u'saturday': u'00:00-24:00'},
                                                    {u'sunday': u'00:00-24:00'}]}, True)
        print "Created default timeperiod"
        default_timeperiod = timeperiods.find_one({'name': '24x7'})
    # Create default username/user if not defined
    try:
        users = app.data.driver.db['user']
    except Exception as e:
        sys.exit("[ERROR] Impossible to connect to MongoDB (%s)" % e)
    super_admin_user = users.find_one({'back_role_super_admin': True})
    if not super_admin_user:
        post_internal("user", {"name": "admin",
                               "password": "admin",
                               "back_role_super_admin": True,
                               "host_notification_period": default_timeperiod['_id'],
                               "service_notification_period": default_timeperiod['_id'],
                               "_realm": default_realm['_id']})
        print "Created Super admin"
    app.on_updated_livestate += Livesynthesis.on_updated_livestate
    app.on_inserted_livestate += Livesynthesis.on_inserted_livestate
    app.on_inserted_host += Livestate.on_inserted_host
    app.on_inserted_service += Livestate.on_inserted_service
    app.on_updated_host += Livestate.on_updated_host
    app.on_updated_service += Livestate.on_updated_service

    # template management
    app.on_pre_POST_host += Template.pre_post_host
    app.on_update_host += Template.on_update_host
    app.on_updated_host += Template.on_updated_host

    app.on_inserted_host += Template.on_inserted_host
    app.on_inserted_service += Template.on_inserted_service
    app.on_deleted_item_service += Template.on_deleted_item_service

    app.on_pre_POST_service += Template.pre_post_service
    app.on_update_service += Template.on_update_service
    app.on_updated_service += Template.on_updated_service

with app.test_request_context():
    Livestate.recalculate()
    Livesynthesis.recalculate()

# hooks post-init
app.on_insert_realm += pre_realm_post
app.on_inserted_realm += after_insert_realm
app.on_updated_realm += after_update_realm

with app.test_request_context():
    app.on_inserted_loghost += Timeseries.after_inserted_loghost
    app.on_inserted_logservice += Timeseries.after_inserted_logservice

# Start scheduler (internal cron)
if settings['SCHEDULER_ACTIVE']:
    with app.test_request_context():
        scheduler = APScheduler()
        scheduler.init_app(app)
        scheduler.start()


@app.route("/login", methods=['POST'])
def login_app():
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
    Offer toute to get the backend config
    """
    my_config = {"PAGINATION_LIMIT": settings['PAGINATION_LIMIT'],
                 "PAGINATION_DEFAULT": settings['PAGINATION_DEFAULT'],
                 'metrics': []}
    if settings['GRAPHITE_HOST'] is not None:
        my_config['metrics'].append('graphite')
    if settings['INFLUXDB_HOST'] is not None:
        my_config['metrics'].append('influxdb')
    return jsonify(my_config)


@app.route("/cron_timeseries")
def cron_timeseries():
    """
    Cron used to add perfdata from retention to timeseries databases

    :return: None
    """
    with app.test_request_context():
        timeseriesretention_db = current_app.data.driver.db['timeseriesretention']
        if timeseriesretention_db.find().count() > 0:
            tsc = timeseriesretention_db.find({'for_graphite': True, 'for_influxdb': False})
            for data in tsc:
                if not Timeseries.send_to_timeseries_graphite([data]):
                    break
                lookup = {"_id": data['_id']}
                deleteitem_internal('timeseriesretention', False, False, **lookup)
            tsc = timeseriesretention_db.find({'for_graphite': False, 'for_influxdb': True})
            for data in tsc:
                if not Timeseries.send_to_timeseries_influxdb([data]):
                    break
                lookup = {"_id": data['_id']}
                deleteitem_internal('timeseriesretention', False, False, **lookup)
            tsc = timeseriesretention_db.find({'for_graphite': True, 'for_influxdb': True})
            for data in tsc:
                graphite_serv = True
                influxdb_serv = True
                if not Timeseries.send_to_timeseries_graphite([data]):
                    graphite_serv = False
                if not Timeseries.send_to_timeseries_influxdb([data]):
                    influxdb_serv = False
                lookup = {"_id": data['_id']}
                if graphite_serv and influxdb_serv:
                    deleteitem_internal('timeseriesretention', False, False, **lookup)
                elif graphite_serv and not influxdb_serv:
                    patch_internal('timeseriesretention', {"for_graphite": False}, False, False,
                                   **lookup)
                elif influxdb_serv and not graphite_serv:
                    patch_internal('timeseriesretention', {"for_influxdb": False}, False, False,
                                   **lookup)


def main():
    """
        Called when this module is started from shell
    """
    try:
        print "--------------------------------------------------------------------------------"
        print "%s, listening on %s:%d" % (
            manifest['name'], app.config.get('HOST', '127.0.0.1'), app.config.get('PORT', 8090)
        )
        print "--------------------------------------------------------------------------------"
        app.run(
            host=settings.get('HOST', '127.0.0.1'),
            port=settings.get('PORT', 5000),
            debug=settings.get('DEBUG', False)
        )
    except Exception as e:
        print "Application run failed, exception: %s / %s" % (type(e), str(e))
        print "Back trace of this kill: %s" % traceback.format_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
