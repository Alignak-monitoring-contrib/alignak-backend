#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    ``alignak_backend.app`` module

    This module manages the backend, its configuration and starts the backend
"""

import sys
import traceback
import os
from docopt import docopt
from collections import OrderedDict
import logging
from textwrap import dedent
from configparser import ConfigParser
from pprint import pformat
import time
import uuid
from datetime import timedelta

from eve import Eve
from eve.auth import TokenAuth
from eve.io.mongo import Validator
from werkzeug.security import check_password_hash, generate_password_hash
from flask_bootstrap import Bootstrap
from eve_docs import eve_docs
from eve.methods.post import post_internal
from flask import current_app, g, request, abort, jsonify

from alignak_backend.models import register_models
from alignak_backend import manifest
from alignak_backend.log import Log
from alignak_backend.livesynthesis import Livesynthesis
from alignak_backend.livestate import Livestate

_subcommands = OrderedDict()


def register_command(description):
    """Register commands usable from command line"""
    def decorate(f):
        """Create decorator to be used for functions"""
        _subcommands[f.__name__] = (description, f)
        return f
    return decorate


class MyTokenAuth(TokenAuth):
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
        :return: True if contact exist and password is ok or if no roles defined, otherwise False
        :rtype: bool
        """

        _contacts = current_app.data.driver.db['contact']
        contact = _contacts.find_one({'token': token})
        if contact:
            g.back_role_super_admin = contact['back_role_super_admin']
            g.back_role_admin = contact['back_role_admin']
            # get restricted
            contactrestrictroles = current_app.data.driver.db['contactrestrictrole']
            contactrestrictrole = contactrestrictroles.find({'contact': contact['_id']})
            g.back_role_restricted = {}
            for role in contactrestrictrole:
                if not role['brotherhood'] in g.back_role_restricted:
                    g.back_role_restricted[str(role['brotherhood'])] = []
                g.back_role_restricted[str(role['brotherhood'])].extend(role['resource'])
            g.users_id = contact['_id']
            if not contact['back_role_super_admin']:
                if contact['back_role_admin'] == [] and g.back_role_restricted == {}:
                    # no rights
                    return False
        return contact


class MyValidator(Validator):
    """Specific validator for data model fields types extension"""
    def _validate_title(self, title, field, value):
        """Validate 'title' field (always valid)"""
        return

    def _validate_ui(self, title, field, value):
        """Validate 'ui' field (always valid)"""
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
    if not g.get('back_role_super_admin', False):
        # Only in case not super-admin
        if resource != 'contact':
            admin = g.get('back_role_admin', [])
            if admin != []:
                if "_brotherhood" not in lookup:
                    lookup["_brotherhood"] = {"$in": admin}
                else:
                    if not lookup["_brotherhood"] in admin:
                        lookup["_id"] = 0
            else:
                restrict = g.get('back_role_restricted', {})
                if "_brotherhood" not in lookup:
                    broth = []
                    for brotherhood, resources in restrict.items():
                        if resource in resources:
                            broth.append(brotherhood)
                    if broth == []:
                        lookup["_id"] = 0
                    else:
                        lookup["_brotherhood"] = {"$in": broth}
                        field = '_users_read'
                        if user_request.environ['REQUEST_METHOD'] == 'POST':
                            field = '_users_create'
                        if user_request.environ['REQUEST_METHOD'] == 'PATCH':
                            field = '_users_update'
                        if user_request.environ['REQUEST_METHOD'] == 'DELETE':
                            field = '_users_delete'
                        lookup[field] = {"$in": [g.get('users_id')]}
                else:
                    for brotherhood, resources in restrict.items():
                        if resource in resources and lookup["_brotherhood"] == brotherhood:
                            return
                    lookup["_id"] = 0


def pre_contact_post(items):
    """
    Hook before insert.
    When add contact, hash the backend password of the user

    :param items: list of items (list because can use bulk)
    :type items: list
    :return: None
    """
    for index, item in enumerate(items):
        if 'password' in item:
            items[index]['password'] = generate_password_hash(item['password'])


def pre_contact_patch(updates, original):
    """
    Hook before update.
    When update contact, hash the backend password of the user if try to change it

    :param updates: list of fields user try to update
    :type updates: dict
    :param original: list of original fields
    :type original: dict
    :return: None
    """
    if 'password' in updates:
        updates['password'] = generate_password_hash(updates['password'])


def generate_token():
    """
    Generate a user token

    :return: user token
    """
    t = int(time.time() * 1000)
    return str(t)+'-'+str(uuid.uuid4())


def get_settings(prev_settings):
    """
    Get settings of application from config file to update/complete previously existing gsettings

    :param prev_settings: previous settings
    :type prev_settings: dict
    :return: None
    """
    settings_filenames = [
        '/usr/local/etc/alignak_backend/settings.cfg',
        '/etc/alignak_backend/settings.cfg',
        os.path.abspath('./etc/settings.cfg'),
        os.path.abspath('../etc/settings.cfg'),
        os.path.abspath('./settings.cfg')
    ]

    # Define some variables available
    defaults = {
        '_cwd': os.getcwd()
    }
    config = ConfigParser(defaults=defaults)
    cfg_file = config.read(settings_filenames)
    if not cfg_file:
        print "No configuration file found, using default configuration"
    else:
        print "Configuration read from file(s): %s" % cfg_file
    for key, value in config.items('DEFAULT'):
        if key.startswith('_'):
            continue
        if key.upper() in prev_settings:
            app_default = prev_settings[key.upper()]
            if isinstance(app_default, timedelta):
                prev_settings[key.upper()] = timedelta(value)
            elif isinstance(app_default, bool):
                prev_settings[key.upper()] = True if value in [
                    'true', 'True', 'on', 'On', 'y', 'yes', '1'
                ] else False
            elif isinstance(app_default, float):
                prev_settings[key.upper()] = float(value)
            elif isinstance(app_default, int):
                prev_settings[key.upper()] = int(value)
            else:
                # All the string keys need to be coerced into str()
                # because Flask expects some of them not to be unicode
                prev_settings[key.upper()] = str(value)
        else:
            if value.isdigit():
                prev_settings[key.upper()] = int(value)
            else:
                prev_settings[key.upper()] = str(value)
        if key.lower() == "server_name":
            if prev_settings[key.upper()].lower() == 'none':
                prev_settings[key.upper()] = None


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

# Read configuration file to update/completethe configuration
get_settings(settings)

print "Application settings: %s" % settings

# Add model schema to the configuration
settings['DOMAIN'] = register_models()

app = Eve(
    settings=settings,
    validator=MyValidator,
    auth=MyTokenAuth
)
# hooks
app.on_pre_GET += pre_get
app.on_insert_contact += pre_contact_post
app.on_update_contact += pre_contact_patch

# docs api
Bootstrap(app)
app.register_blueprint(eve_docs, url_prefix='/docs')

# Create default account when have no contact.
with app.test_request_context():
    try:
       contacts = app.data.driver.db['contact']
    except:
        sys.exit("[ERROR] Impossible to connect to MongoDB")
    super_admin_contact = contacts.find_one({'back_role_super_admin': True})
    if not super_admin_contact:
        post_internal("contact", {"contact_name": "admin",
                                  "name": "Big Brother",
                                  "password": "admin",
                                  "back_role_super_admin": True,
                                  "back_role_admin": []})
        print "Created Super admin"
    app.on_updated_livestate += Livesynthesis.on_updated_livestate
    app.on_inserted_livestate += Livesynthesis.on_inserted_livestate
    app.on_inserted_host += Livestate.on_inserted_host
    app.on_inserted_service += Livestate.on_inserted_service
    app.on_updated_host += Livestate.on_updated_host
    app.on_updated_service += Livestate.on_updated_service
with app.test_request_context():
    Livestate.recalculate()
    Livesynthesis.recalculate()


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
        _contacts = app.data.driver.db['contact']
        contact = _contacts.find_one({'contact_name': posted_data['username']})
        if contact:
            if check_password_hash(contact['password'], posted_data['password']):
                if 'action' in posted_data:
                    if posted_data['action'] == 'generate' or not contact['token']:
                        token = generate_token()
                        _contacts.update({'_id': contact['_id']}, {'$set': {'token': token}})
                        return jsonify({'token': token})
                elif not contact['token']:
                    token = generate_token()
                    _contacts.update({'_id': contact['_id']}, {'$set': {'token': token}})
                    return jsonify({'token': token})
                return jsonify({'token': contact['token']})
        abort(401, description='Please provide proper credentials')


@app.route("/logout", methods=['POST'])
def logout_app():
    """
    Log out from backend
    """
    return 'ok'


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
