#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    ``alignak_backend.app`` module

    This module manages the backend, its configuration and starts the backend
"""

import sys
import os
from docopt import docopt
from collections import OrderedDict
import logging
from textwrap import dedent
from configparser import ConfigParser
from pprint import pformat
import time
import uuid

from eve import Eve
from eve.auth import TokenAuth
from eve.io.mongo import Validator
from werkzeug.security import check_password_hash, generate_password_hash
from flask_bootstrap import Bootstrap
from eve_docs import eve_docs
from flask import current_app, g, request, abort, jsonify

from alignak_backend.models import register_models
from alignak_backend import __version__, __copyright__, __releasenotes__, __license__, __doc_url__
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

        contacts = current_app.data.driver.db['contact']
        contact = contacts.find_one({'token': token})
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


def pre_get(resource, request, lookup):
    """
    Hook before get data. Add filter depend on roles of user

    :param resource: name of the resource requested by user
    :type resource: str
    :param request: request of the user
    :type request: object
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
                        if request.environ['REQUEST_METHOD'] == 'POST':
                            field = '_users_create'
                        if request.environ['REQUEST_METHOD'] == 'PATCH':
                            field = '_users_update'
                        if request.environ['REQUEST_METHOD'] == 'DELETE':
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
        if 'back_password' in item:
            items[index]['back_password'] = generate_password_hash(item['back_password'])


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
    if 'back_password' in updates:
        updates['back_password'] = generate_password_hash(updates['back_password'])


def generate_token():
    t = int(time.time() * 1000)
    return str(t)+'-'+str(uuid.uuid4())


def get_settings(settings):
    """
    Get settings of application from config file

    :param settings: default settings
    :type settings: dict
    :return: None
    """
    settings_filenames = [
        '/usr/local/etc/alignak_backend/settings.ini',
        '/etc/alignak_backend/settings.ini',
        os.path.abspath('./settings.ini')
    ]

    # Define some variables available
    defaults = {
        '_cwd': os.getcwd()
    }
    config = ConfigParser(defaults=defaults)
    config.read(settings_filenames)
    for key, value in config.items('DEFAULT'):
        if not key.startswith('_'):
            settings[key.upper()] = value


# Application configuration
# Read configuration file
settings = {}
settings['DOMAIN'] = register_models()
settings['RESOURCE_METHODS'] = ['GET', 'POST', 'DELETE']
settings['ITEM_METHODS'] = ['GET', 'PATCH', 'DELETE']
settings['XML'] = False
settings['X_DOMAINS'] = '*'
settings['X_HEADERS'] = (
    'Authorization, If-Match,'
    ' X-HTTP-Method-Override, Content-Type'
)
settings['PAGINATION_LIMIT'] = 200

settings['MONGO_HOST'] = 'localhost'
settings['MONGO_PORT'] = 27017
# self.settings['MONGO_USERNAME'] = 'user'
# self.settings['MONGO_PASSWORD'] = 'user'
settings['MONGO_DBNAME'] = 'alignak-backend'

# Allow $regex in filtering ...
# Default is ['$where', '$regex']
settings['MONGO_QUERY_BLACKLIST'] = ['$where']

get_settings(settings)
print(settings)
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
with app.app_context():
    contacts = app.data.driver.db['contact']
    super_admin_contact = contacts.find_one({'back_role_super_admin': True})
    if not super_admin_contact:
        contacts.insert({"contact_name": "admin",
                         "name": "Big Brother",
                         "back_password": generate_password_hash("admin"),
                         "back_role_super_admin": True,
                         "back_role_admin": []})
    app.on_updated_livestate += Livesynthesis.on_updated_livestate
    app.on_inserted_livestate += Livesynthesis.on_inserted_livestate
    app.on_inserted_host += Livestate.on_inserted_host
    app.on_inserted_service += Livestate.on_inserted_service
with app.test_request_context():
    Livestate.recalculate()
    Livesynthesis.recalculate()


@app.route("/login", methods=['POST'])
def login_app():
    post_data = request.get_json()
    if 'username' not in post_data or 'password' not in post_data:
        abort(401, description='Please provide proper credentials')
    elif post_data['username'] == '' or post_data['password'] == '':
        abort(401, description='Please provide proper credentials')
    else:
        contacts = app.data.driver.db['contact']
        contact = contacts.find_one({'contact_name': post_data['username']})
        if contact:
            if check_password_hash(contact['back_password'], post_data['password']):
                if 'action' in post_data:
                    if post_data['action'] == 'generate':
                        token = generate_token()
                        contacts.update({'_id': contact['_id']}, {'$set': {'token': token}})
                        return jsonify({'token': token})
                return jsonify({'token': contact['token']})
        abort(401, description='Please provide proper credentials')


@app.route("/logout", methods=['POST'])
def logout_app():
    return 'ok'

if __name__ == '__main__':
    app.run()
