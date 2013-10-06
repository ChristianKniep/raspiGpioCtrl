#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Library to handle the gpio and the webserver
"""

import logging
import os

PREFIX = os.environ.get("WORKSPACE", "/")
if not PREFIX.endswith("/"):
    PREFIX += "/"

_LOGGER = logging.getLogger(__name__)

class PinError(Exception):
    def __init__(self, value):
        """
        init exception
        """
        self.value = value

    def __str__(self):
        """
        string representation
        """
        return repr(self.value)

