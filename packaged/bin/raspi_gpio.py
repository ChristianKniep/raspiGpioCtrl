#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Bibliotheken laden
import re
#import os
#import web
from pprint import pprint
import sys
#import datetime
#import time
import argparse
#from libgpio import GpioCtrl, Parameter
from raspi import Web, ArgParameter
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
    options = ArgParameter()
    options = argparse.Namespace(debug=1, root="./", dry_run=True)
    if options.dry_run:
        print "dry-run!"
    #    srv = GpioCtrl(options)
    #    srv.run_cronjob()
    #if options.get("run_webserver"):
    #    cherrypy.config.update(
    #        {'server.socket_port': int(options.get("web_port")),}
    #        )
    #    cherrypy.quickstart(Web(options))


# ein Aufruf von main() ganz unten
if __name__ == "__main__":
    main()
