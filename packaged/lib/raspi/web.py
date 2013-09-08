#! /usr/bin/env python
# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser
import sys
from pprint import pprint
from raspi.ctrl import GpioCtrl
from raspi.pin import get_mode_id

import re
try:
    import cherrypy
except ImportError:
    app_path = "/opt/local/Library/Frameworks/Python.framework/Versions/"
    app_path += "2.7/lib/python2.7/site-packages/"
    sys.path.append(app_path)
    import cherrypy


class Web(object):
    """
    Webside modeled as an cherrypy class
    """
    def __init__(self, opt):
        self.opt = opt
        self.gctrl = GpioCtrl(opt)
        self.gctrl.read_cfg()
        self.gpio_pins = self.gctrl.gpio_pins
        self.form = {}

    def create_row(self, gpio):
        """ Erstellt Zeile fuer gpio-pin in Form eines Formulars
        """
        pin_json = self.gpio_pins[gpio].get_json()
        pin_json['pinid'] = gpio
        self.html += """
            <tr>
            <form method="POST">
                <td><b>%(pin_nr)s</b></td>
                <td><b>%(pinid)s</b></td>""" % pin_json
        self.html += "<input type='hidden' name='gpio' value='%s'>" % gpio
        if pin_json['state'] == "0":
            state_col = 'red'
        else:
            state_col = 'green'
        self.html += "<td style='background-color:%s'>" % state_col
        self.html += "<input name='send' type='submit' value='flip'></td>"
        self.html += """
                <td>"""
        for mode in ['time', 'sun', 'man']:
            if pin_json['mode'] == mode:
                checked = " checked"
            else:
                checked = ""
            arg = (mode, checked, mode)
            self.html += """
                    <input type="radio" name="mode" value="%s"%s>%s""" % arg
        self.html += "<td><select name='prio'>"
        for prio in range(0,5):
            self.html += "<option value='%s'" % prio
            if pin_json['prio'] == str(prio):
                self.html += "selected"
            self.html += ">%s</option>" % prio
        self.html += "</select></td>"
        self.html += """
                </td>"""
        self.html += """
                <td><input type="text" name="start" value="%(start)s" size="6">o'clock (24h)</td>
                <td>""" % pin_json
        for dow in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
            checked = ""
            if 'dow' in pin_json.keys() and \
               re.match(".*%s.*" % dow, pin_json['dow'], re.I):
                checked = " checked"
            self.html += "<input type='checkbox' name='dow_%s' value='%s'%s>%s" % (dow, dow, checked, dow)
        self.html += "</td>"
        self.html += """
                <td><input type="text" name="duration" value="%(duration)s" size="5">min</td>
                <td><input type="text" name="sun_delay" value="%(sun_delay)s" size="5">min</td>
                <td><input name="send" type="submit" value="change"></td>
            </form>
            </tr>""" % pin_json

    def create_tab(self):
        """ Creates table to show the different gpiopins
        """
        for gpio in self.gpio_pins.keys():
            self.create_row(gpio)

    @cherrypy.expose
    def index(self, gpio=None, start=None, dow_Wed=None, dow_Sun=None, prio=None,
              dow_Sat=None, dow_Tue=None, sun_delay=None, dow_Mon=None,
              send=None, duration=None, dow_Thu=None, dow_Fri=None, mode=None):
        """
        Creates the list of gpio pins and handles changes
        """
        if gpio is not None:
            self.form = {
            'gpio': gpio,
            'start': start,
            'prio': prio,
            'dow': {
                'mon': dow_Mon,
                'tue': dow_Tue,
                'wed': dow_Wed,
                'thu': dow_Thu,
                'fri': dow_Fri,
                'sat': dow_Sat,
                'sun': dow_Sun,
            },
            'sun_delay': sun_delay,
            'send': send,
            'duration': duration,
            'mode': mode,
        }
            self.change()
        self.html = """
        <html><head>
                <title>web.py</title>
        </head><body><table border="1">
            <tr align="center">
                <td>GpioNr</td>
                <td>PinID</td>
                <td>Prio</td>
                <td>Status</td>
                <td>Modus</td>
                <td>An um</td>
                <td>Wochentage</td>
                <td>Dauer</td>
                <td>Sonnenverzoegerung</td>
            </tr>
        """
        self.create_tab()
        self.html += """
        </table>
        </body></html>
        """
        return self.html

    def change(self):
        """
        Triggered if Web-GUI wants to change a pin
        """
        #print "%s! %s" % (self.form['send'], self.form)
        if self.form['send'] == "flip":
            self.gctrl.flip(self.form['gpio'])
        elif self.form['send'] == "change":
            if self.form['mode'] == "sun":
                self.gpio_ctrl.set_sunset(self.form['gpio'])
            elif self.form['mode'] == "time":
                dow = []
                for key,val in self.form['dow'].items():
                    if val is not None:
                        dow.append(key)
                pin_cfg = {'groups':'a',
                      'start': self.form['start'],
                      'prio': self.form['prio'],
                      'duration': self.form['duration'],
                      'dow': ",".join(dow),
                      }
                self.gctrl.set_pin_cfg(self.form['gpio'], pin_cfg)
                self.gctrl.arrange_pins()
                self.gpio_pins[self.form['gpio']].write_cfg()
