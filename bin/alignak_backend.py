#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    This file is used to run the Alignak backend in production environment with WSGI server.

    With uWSGI:
        uwsgi --wsgi-file alignak_backend.py --callable app --socket 0.0.0.0:5000 --protocol=http --enable-threads
"""
from alignak_backend.app import app
