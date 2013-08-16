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
    '0':'off',
    '1':'time',
    '2':'manual',
    '3':'sun'
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

    def default(self):
        """
        """
        help_msg = "Increase output verbosity(-d:1, -ddd:3)"
        self.parser.add_argument("-d", action="count",
                                 dest="debug", help=help_msg)
        help_msg = "dry run on !raspi creating gpio-path in `pwd`"
        self.parser.add_argument("--dry-run", dest="dry_run",
                                 default=False, action="store_true",
                                 help=help_msg)
        help_msg = "Root dir for config, lock-files, etc (def:/)"
        self.parser.add_argument("-r", dest="root",
                                 default="/", action="store",
                                 help=help_msg)


""" Old Parameter
    def default(self):
        self.parser.add_option("-d", dest="debug",
                               default=0, action="count",
                               help="Erhoehe Debug-Level (-d:1, -ddd:3)")
        self.parser.add_option("-w", dest="run_webserver",
                default=False, action="store_true",
                help="Spawn (not yet) webserver")
        self.parser.add_option("--dry-run", dest="dry_run",
                default=False, action="store_true",
                help="dry run on !raspi creating gpio-path in `pwd`")
        self.parser.add_option("-c", dest="create_cfg",
            default=False, action="store_true",
            help="create config 'raspi_gpio.cfg' with example setup")
        self.parser.add_option("-j", dest="run_cronjob",
            default=False, action="store_true", help="Run cronjob and exit")
        self.parser.add_option("-p", dest="web_port",
            default="8080", action="store",
            help="Webserver port (def:%default)")
        self.parser.add_option("-r", dest="root",
            default="/", action="store",
            help="Current root dir (def:%default)")
        
        # copy over all class.attributes
        (self.options, self.args) = self.parser.parse_args()
"""
