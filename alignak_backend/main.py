#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main
"""
from alignak_backend.app import app


def main():
    # Process command line parameters
    # appli.process_args()
    app.run()

if __name__ == "__main__":  # pragma: no cover
    main()
