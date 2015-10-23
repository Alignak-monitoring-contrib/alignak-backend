#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest2
import requests
import time
import subprocess
import json
from alignak_backend_client.client import Backend


class Test_0_Login(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p = subprocess.Popen(['uwsgi', '-w', 'alignakbackend:app', '--socket', '0.0.0.0:5000', '--protocol=http', '--enable-threads'])
        time.sleep(3)
        cls.backend = Backend('http://127.0.0.1:5000')

    @classmethod
    def tearDownClass(cls):
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
        print "Super admin is defined in backend ..."
        token = self.backend.token
        print token

        assert self.backend.login("admin", "admin")
        assert token == self.backend.token
        token = self.backend.token
        print token

        assert self.backend.login("admin", "admin", "force")
        assert token != self.backend.token
        token = self.backend.token
        print token


class Test_1_Login(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p = subprocess.Popen(['uwsgi', '-w', 'alignakbackend:app', '--socket', '0.0.0.0:5000', '--protocol=http', '--enable-threads'])
        time.sleep(3)
        cls.backend = Backend('http://127.0.0.1:5000')
        # Login and delete defined contacts ...
        cls.backend.login("admin", "admin")
        cls.backend.delete("contact", {})

    @classmethod
    def tearDownClass(cls):
        cls.p.kill()

    @classmethod
    def setUp(cls):
        print "..."

    @classmethod
    def tearDown(cls):
        print "..."

    def test_0(self):
        print ""

        # No login possible ...
        assert not self.backend.login("admin", "admin")

        print ("")
        print ("populate backend content")

        q = subprocess.Popen(['../alignak_backend/tools/cfg_to_backend.py', '--delete', 'cfg/default/shinken.cfg'])
        q.communicate() #now wait
        time.sleep(1)

        assert self.backend.login("admin", "admin")
        print "Super admin is now defined in backend ..."
        token = self.backend.token
        print token

