#! /usr/bin/env python
# -*- coding: utf-8 -*-

#from optparse import OptionParser
from argparse import ArgumentParser
from ConfigParser import ConfigParser
import sys
import os
import subprocess
import md5
import datetime
try:
    import cherrypy
except ImportError:
    app_path = "/opt/local/Library/Frameworks/Python.framework/Versions/"
    app_path += "2.7/lib/python2.7/site-packages/"
    sys.path.append(app_path)
    import cherrypy

PIN_MODES = {
    '0': 'off',
    '1': 'time',
    '2': 'manual',
    '3': 'sun',
}


class ArgParameter(object):
    """
    """
    def __init__(self):
        """
        Parameterhandling
        """
        self.parser = ArgumentParser()
        self.default()
        # copy over all class.attributes
        args = self.parser.parse_args()
        for item in args:
            print item

    def default(self):
        """
        """
        help_msg = "Increase output verbosity(-d:1, -ddd:3)"
        self.parser.add_argument("-d", action="count",
                                 dest="debug", help=help_msg)
        help_msg = "dry run on !raspi creating gpio-path in `pwd`"
        self.parser.add_argument("--dry-run", dest="dryrun",
                                 default=False, action="store_true",
                                 help=help_msg)
        help_msg = "Root dir for config, lock-files, etc (def:/)"
        self.parser.add_argument("-r", dest="root",
                                 default="/", action="store",
                                 help=help_msg)
