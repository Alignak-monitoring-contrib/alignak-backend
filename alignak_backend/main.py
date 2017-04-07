#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main
"""
from __future__ import print_function

from alignak_backend.app import app, manifest


def main():  # pragma: no cover - tested but not covered
    """Main function to run the alignak backend

    This function is used by the `alignak-backend` script installed with setup.py.
    It is intended to run the backend in a single process mode. This mode is not
    recommended for production but may be useful in development to avoid setting-up
    an uWSGI server.
    """
    try:
        host = app.config.get('HOST', '127.0.0.1')
        if not host:
            host = '0.0.0.0'
        port = app.config.get('PORT', 5000)
        url = "http://%s:%d" % (host, port)
        print("--------------------------------------------------------------------------------")
        print("%s, listening on %s" % (manifest['name'], url))
        print("--------------------------------------------------------------------------------")
        app.run(host=host, port=port, debug=app.config.get('DEBUG', False))
    except Exception as e:
        print("Application run failed, exception: %s / %s" % (type(e), str(e)))

if __name__ == "__main__":  # pragma: no cover
    main()
