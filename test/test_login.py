#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest2
import requests
import time
import subprocess
import json
from alignak_backend_client.client import Backend


class Test_0_LoginCreation(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        print ("")
        print ("start backend")
        cls.p = subprocess.Popen(['uwsgi', '-w', 'alignakbackend:app', '--socket', '0.0.0.0:5000', '--protocol=http', '--enable-threads'])
        time.sleep(1)
        cls.backend = Backend('http://127.0.0.1:5000')

    def test_0(self):
        print ""

        # Login and delete defined contacts ...
        self.backend.login("admin", "admin")
        self.backend.delete("contact", {})

        # No login possible ...
        assert not self.backend.login("admin", "admin")

        # Stop and restart backend ...
        print ("")
        print ("stop backend")
        self.p.kill()
        print ("")
        print ("start backend")
        self.p = subprocess.Popen(['uwsgi', '-w', 'alignakbackend:app', '--socket', '0.0.0.0:5000', '--protocol=http', '--enable-threads'])
        time.sleep(1)
        self.backend = Backend('http://127.0.0.1:5000')

        # Login is now possible because backend recreated super admin user
        assert self.backend.login("admin", "admin")
        print "Super admin is now defined in backend ..."
        token = self.backend.token
        assert token

        print ("")
        print ("stop backend")
        self.p.kill()


class Test_1_Login(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        print ("")
        print ("start backend")
        cls.p = subprocess.Popen(['uwsgi', '-w', 'alignakbackend:app', '--socket', '0.0.0.0:5000', '--protocol=http', '--enable-threads'])
        time.sleep(3)
        cls.backend = Backend('http://127.0.0.1:5000')

    @classmethod
    def tearDownClass(cls):
        print ("")
        print ("stop backend")
        cls.p.kill()

    @classmethod
    def setUp(cls):
        print "..."

    @classmethod
    def tearDown(cls):
        print "..."

    def test_0(self):
        print ""

        # generate parameter may have following values:
        # - enabled:    require current token (default)
        # - force:      force new token generation
        # - disabled    not to used actually !!!!!!!!!!!!!!!!!!!!!

        assert self.backend.login("admin", "admin")
        token = self.backend.token
        assert self.backend.authenticated
        print token

        assert self.backend.login("admin", "admin")
        assert token == self.backend.token
        assert self.backend.authenticated
        token = self.backend.token
        print token

        assert self.backend.login("admin", "admin", "force")
        assert token != self.backend.token
        assert self.backend.authenticated
        token = self.backend.token
        print token
        assert token

        assert self.backend.logout()
        assert not self.backend.token
        assert not self.backend.authenticated

    def test_1(self):
        print ""

        assert self.backend.login("admin", "admin")
        assert self.backend.token
        token = self.backend.token
        print token

        # Not yet implemented in backend ...
        # assert self.backend.login("guest", "guest")
        # assert self.backend.token
        # assert token != self.backend.token
        # token = self.backend.token
        # print token

        assert self.backend.logout()
        assert not self.backend.token
