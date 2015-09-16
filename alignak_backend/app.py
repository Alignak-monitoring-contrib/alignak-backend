import sys
import os
import bcrypt
from docopt import docopt
from collections import OrderedDict
import logging
from pprint import pprint, pformat  # noqa
from textwrap import dedent
from configparser import ConfigParser

from eve import Eve
from eve.auth import BasicAuth
from werkzeug.security import check_password_hash, generate_password_hash
from flask.ext.bootstrap import Bootstrap
from eve_docs import eve_docs
from flask import current_app, g

from alignak_backend.models import register_models
from alignak_backend.log import Log

_subcommands = OrderedDict()


def register_command(description):
    def decorate(f):
        _subcommands[f.__name__] = (description, f)
        return f
    return decorate


class Sha1Auth(BasicAuth):
    def check_auth(self, username, password, allowed_roles, resource, method):
        # use Eve's own db driver; no additional connections/resources are used
        contacts = current_app.data.driver.db['contact']
        contact = contacts.find_one({'contact_name': username})
        if contact:
            #if not contact['back_role_super_admin']:
            #    if contact['back_role_admin'] == [] and contact['back_role_restricted'] == []:
                    # no rights
            #        return False
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
        return contact and check_password_hash(contact['back_password'], password)


class Application(Log):
    """
    Usage:
        {command} [-d|-v] <subcommand>

    Options:
        -d, --debug     Debug mode
        -v, --verbose   Verbose mode

    Subcommands:
    {subcommands}
    """
    settings = {}

    def __init__(self):
        Log.__init__(self)
        # super().__init__()
        command = os.path.basename(sys.argv[0])
        self.__doc__ = dedent(self.__doc__).format(
            command=command,
            subcommands=self.format_subcommands()
        )

    def pre_get(self, resource, request, lookup):
        if not g.get('back_role_super_admin', False):
            # Only in case not super-admin
            if resource != 'contact':
                if admin != []:
                    if not "_brotherhood" in lookup:
                        lookup["_brotherhood"] = {"$in": admin}
                    else:
                        if not lookup["_brotherhood"] in admin:
                            lookup["_id"] = 0
                else:
                    restrict = g.get('back_role_restricted', {})
                    if not "_brotherhood" in lookup:
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

    def pre_contact_post(self, items):
        for index, item in enumerate(items):
            if 'back_password' in item:
                items[index]['back_password'] = generate_password_hash(item['back_password'])

    def pre_contact_patch(self, updates, original):
        if 'back_password' in updates:
            updates['back_password'] = generate_password_hash(updates['back_password'])

    def initialize(self, debug=False, subcommand='run'):
        self.log.setLevel(debug)
        self.get_settings_from_ini()
        self.settings['DOMAIN'] = register_models()
        self.settings['RESOURCE_METHODS'] = ['GET', 'POST', 'DELETE']
        self.settings['ITEM_METHODS'] = ['GET', 'PATCH', 'DELETE']
        self.settings['XML'] = False
        self.settings['X_DOMAINS'] = '*'
        self.settings['X_HEADERS'] = (
            'Authorization, If-Match,'
            ' X-HTTP-Method-Override, Content-Type'
        )
        self.settings['PAGINATION_LIMIT'] = 200

        self.settings['MONGO_HOST'] = 'localhost'
        self.settings['MONGO_PORT'] = 27017
        # self.settings['MONGO_USERNAME'] = 'user'
        # self.settings['MONGO_PASSWORD'] = 'user'
        self.settings['MONGO_DBNAME'] = 'alignak-backend'
        self.app = Eve(
            settings=self.settings,
            auth=Sha1Auth
        )
        # hooks
        self.app.on_pre_GET += self.pre_get
        self.app.on_insert_contact += self.pre_contact_post
        self.app.on_update_contact += self.pre_contact_patch

        # docs api
        Bootstrap(self.app)
        self.app.register_blueprint(eve_docs, url_prefix='/docs')

        self.log.debug(pformat(self.app.settings))
        self.app.debug = debug
        # Create default account when have no contact.
        with self.app.app_context():
            contacts = self.app.data.driver.db['contact']
            nb_contact = contacts.count()
            if nb_contact == 0:
                contacts.insert({"contact_name": "admin",
                                 "back_password": generate_password_hash("admin"),
                                 "back_role_super_admin": True,
                                 "back_role_admin": []})

    def get_settings_from_ini(self):
        settings = {}
        settings_filenames = [
            '/etc/alignak_backend/settings.ini',
            os.path.abspath('./settings.ini')
        ]
        self.log.debug(settings_filenames)

        # Define some variables available
        defaults = {
            '_cwd': os.getcwd()
        }
        config = ConfigParser(defaults=defaults)
        config.read(settings_filenames)
        self.log.debug(
            "Config file settings\n" +
            pformat(dict(config.items()))
        )
        for k, v in config.items('DEFAULT'):
            if not k.startswith('_'):
                settings[k.upper()] = v
        self.log.debug((
            settings,
            self.settings
        ))
        self.settings.update(settings)

    def format_subcommands(self):
        subcommands_text = []
        for cmd, data in _subcommands.items():
            subcommands_text.append(
                "    {name:{width}}{desc}".format(
                    name=cmd, width=12, desc=data[0]
                )
            )
        return "\n".join(subcommands_text)

    def process_args(self):
        args = docopt(self.__doc__, help=True, options_first=True)
        # Get logging option earlier in the process
        rootlog = logging.getLogger()
        if args['--debug']:
            rootlog.setLevel(logging.DEBUG)
        elif args['--verbose']:
            rootlog.setLevel(logging.INFO)
            self.app.debug = False
        self.log.debug(args)
        self.initialize(args['--debug'], args['<subcommand>'])
        self.log.debug("\n" + pformat(self.settings))
        try:
            _subcommands[args['<subcommand>']][1](self)
        except:
            self.log.exception(
                "Failed to load command '{cmd}'".format(
                    cmd=args['<subcommand>']
                )
            )

    # @register_command("Populate database with random data")
    # def populate(self):
    #     self.install()
    #     alignak_backend.models.assets.populate_db(self.db)

    @register_command("Start serving")
    def run(self):
        self.app.run(use_reloader=False, threaded=True)
