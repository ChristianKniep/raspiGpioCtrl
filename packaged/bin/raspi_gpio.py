#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Usage:
    raspi_gpio.py [options]

Options:
  -h  --help     show this help message and exit
  -d             Debug
  --cron         Run cronjob to trigger pins
  -p <web_port>  Webserver port [default: 8888]
  --dry-run      dry run on !raspi creating gpio-path in `pwd`
  --no-read      Do not read cfg files within etc/...
  -r=<root>      Root dir for config, lock-files, etc [default: /]
  --test=<scen>  Run test-scenario [default: None]
"""

# Bibliotheken laden
import re
#import os
#import web
from pprint import pprint
import sys
from netifaces import ifaddresses as ifaddr
#import datetime
#import time
try:
    from raspi.ctrl import GpioCtrl
except ImportError:
    sys.path.append("/root/raspiGpioCtrl/packaged/lib/")
    from raspi.ctrl import GpioCtrl
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
    
    if options['--cron']:
        print "## Run cronjob check and exit..."
        gctrl = GpioCtrl(options)
        gctrl.run_cron()
    else:
        tree_cfg = {
            '/': {}
        }
        global_cfg = {
            'server.socket_port': int(options['-p']) ,
            'server.socket_host': '0.0.0.0',
        }
        cherrypy.tree.mount(Web(options), "/", tree_cfg)
        cherrypy.config.update(global_cfg)
        cherrypy.engine.start()
        cherrypy.engine.block()


# ein Aufruf von main() ganz unten
if __name__ == "__main__":
    main()
