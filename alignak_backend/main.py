#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main
"""

from alignak_backend.app import Application


def main():
    """Application entry point"""
    # Create application
    appli = Application()

    # Process command line parameters
    appli.process_args()

if __name__ == "__main__":  # pragma: no cover
    main()
