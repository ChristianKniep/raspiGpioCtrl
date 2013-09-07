#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Usage:
    raspi_gpio.py [options]

Options:
  -h  --help  show this help message and exit
  -d          Debug
  --dry-run   dry run on !raspi creating gpio-path in `pwd`
  -r=<root>   Root dir for config, lock-files, etc (def:/)
"""

# Bibliotheken laden
import re
#import os
#import web
from pprint import pprint
import sys
#import datetime
#import time
#from libgpio import GpioCtrl, Parameter
from raspi.web import Web
from docopt import docopt
try:
    import cherrypy
except ImportError:
    app_path = "/opt/local/Library/Frameworks/Python.framework/Versions/"
    app_path += "2.7/lib/python2.7/site-packages/"
    sys.path.append(app_path)
    import cherrypy
#


def main():
    """ main function """
    # Parameter
    options =  docopt(__doc__, version='0.1')
    if options['--dry-run']:
        print "dry-run!"
    #    srv = GpioCtrl(options)
    #    srv.run_cronjob()
    #if options.get("run_webserver"):
    cherrypy.config.update(
        {'server.socket_port': 8888 ,} 
        )
    cherrypy.quickstart(Web(options))


# ein Aufruf von main() ganz unten
if __name__ == "__main__":
    main()
