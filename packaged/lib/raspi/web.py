#! /usr/bin/env python
# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser
import sys
from pprint import pprint
from raspi.ctrl import GpioCtrl
from raspi.pin import get_mode_id

import re
import cherrypy


class Web(object):
    """
    Webside modeled as an cherrypy class
    """
    def __init__(self, opt):
        self.opt = opt
        self.gctrl = GpioCtrl(opt)
        if not self.opt['--no-read']:
            self.gctrl.read_cfg()
        self.gpio_pins = self.gctrl.gpio_pins
        self.form = {}
        self.html = []

    def add_pin(self, pin):
        """
        Add pin to GpioCtrl
        """
        self.gctrl.add_pin(pin)

    def create_row(self, gpio):
        """
        Global function to create row for pin
        """
        pin_json = self.gpio_pins[gpio].get_json()
        if pin_json['groups'] == "main":
            self.create_row_main(gpio)
        else:
            self.create_row_slave(gpio)

    def create_row_main(self, gpio):
        """
        create row for normal rain switch
        """
        pin_json = self.gpio_pins[gpio].get_json()
        pin_json['pinid'] = gpio
        self.html.extend([
            "<tr>",
            '<form method="POST">',
            "<td><b>%(pin_nr)s</b></td>" % pin_json,
            "<td><b>%(name)s</b></td>" % pin_json,
            '<td>group</td>',  #group
        ])
        self.html.append("<input type='hidden' name='gpio' value='%s'>" % gpio)
        if pin_json['state'] == "0":
            state_col = 'red'
        else:
            state_col = 'green'
        self.html.append("<td style='background-color:%s'>" % state_col)
        self.html.append("<input name='send' type='submit' value='flip'></td>")
        if pin_json['mode'] == "off":
            state_col = 'red'
        else:
            state_col = 'green'
        self.html.append("<td style='background-color:%s'>" % state_col)
        html_line = "<input name='send' type='submit' value='OFF'>"
        html_line += "<input name='send' type='submit' value='ON'></td>"
        self.html.extend([
            html_line,
            '<td></td>',  #prio
            '<td></td>',  # on
            '<td></td>',  # dow
            '<td></td>',  # duration
            '<td></td>',  # sun
            ])
        html_line = "<td><input name='send' type='submit' value='change'></td>"
        self.html.extend([
            html_line,
            "</form>",
            "</tr>",
            ])

    def create_row_slave(self, gpio):
        """
        create row for normal rain switch
        """
        pin_json = self.gpio_pins[gpio].get_json()
        pin_json['pinid'] = gpio
        self.html.extend(["<tr>",
            '<form method="POST">',
            "<td><b>%(pin_nr)s</b></td>" % pin_json,
            "<td><b>%(name)s</b></td>" % pin_json,
            ])
        html_line = "<td><input type='text' name='groups' "
        html_line += "value='%(groups)s' size='10'></td>" % pin_json
        self.html.append(html_line)
        self.html.append("<input type='hidden' name='gpio' value='%s'>" % gpio)
        if pin_json['state'] == "0":
            state_col = 'red'
        else:
            state_col = 'green'
        self.html.append("<td style='background-color:%s'>" % state_col)
        self.html.append("<input name='send' type='submit' value='flip'></td>")
        self.html.append("<td>")
        for mode in ['time', 'sun', 'man']:
            if pin_json['mode'] == mode:
                checked = " checked"
            else:
                checked = ""
            arg = (mode, checked, mode)
            self.html.append("<input type='radio' name='mode' value='%s'%s>%s" % arg)
        self.html.append("<td><select name='prio'>")
        for prio in range(0,5):
            html = "<option value='%s'" % prio
            if pin_json['prio'] == str(prio):
                html += "selected"
            html += ">%s</option>" % prio
            self.html.append(html)
        self.html.append("</select></td>")
        self.html.append("</td>")
        html_line = "<td><input type='text' name='start' "
        html_line += "value='%(start)s' size='5'>(24h)</td>" % pin_json
        self.html.extend([
            html_line,
            "<td>",
            ])
        for dow in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
            checked = ""
            if 'dow' in pin_json.keys() and \
               re.match(".*%s.*" % dow, pin_json['dow'], re.I):
                checked = " checked"
            html_line = "<input type='checkbox' name='dow_"
            html_line += "%s' value='%s'%s>%s" % (dow, dow, checked, dow)
            self.html.append(html_line)
        self.html.append("</td>")
        
        html_line = "<td><input type='text' name='duration' "
        html_line += "value='%(duration)s' size='5'>min</td>" % pin_json
        self.html.append(html_line)
        html_line = "<td><input type='text' name='sun_delay' "
        html_line += "value='%(sun_delay)s' size='5'>min</td>" % pin_json
        self.html.append(html_line)
        html_line = "<td><input name='send' type='submit' value='change'></td>"
        self.html.extend([
            html_line,
            "</form>",
            "</tr>",
            ])

    def create_tab(self):
        """ Creates table to show the different gpiopins
        """
        for gpio in self.gpio_pins.keys():
            print gpio
            self.create_row(gpio)

    @cherrypy.expose
    def index(self, gpio=None, start=None, dow_Wed=None, dow_Sun=None, prio=None,
              dow_Sat=None, dow_Tue=None, sun_delay=None, dow_Mon=None, groups=None,
              send=None, duration=None, dow_Thu=None, dow_Fri=None, mode=None):
        """
        Creates the list of gpio pins and handles changes
        """
        self.html = []
        if gpio is not None:
            self.form = {
            'gpio': gpio,
            'start': start,
            'prio': prio,
            'groups': groups,
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
        self.html.extend([
            "<html><head>",
            "<title>web.py</title>"
            '</head><body><table border="1">',
            '<tr align="center">',
                '<td>PinID</td>',
                '<td>Name</td>',
                '<td>Groups</td>',
                '<td>Status</td>',
                '<td>Modus</td>',
                '<td>Prio</td>',
                '<td>An um</td>',
                '<td>Wochentage</td>',
                '<td>Dauer</td>',
                '<td>Sonnenverzoegerung</td>',
            '</tr>',
            ])
        self.create_tab()
        self.html.append("</table>")
        self.html.append("</body></html>")
        return "\n".join(self.html)

    def change(self):
        """
        Triggered if Web-GUI wants to change a pin
        """
        if self.form['send'] == "flip":
            self.gctrl.flip(self.form['gpio'])
        elif self.form['send'] == "OFF":
            self.gctrl.gpio_pins[self.form['gpio']].change_mode('off')
            self.gctrl.gpio_pins[self.form['gpio']].write_cfg()
        elif self.form['send'] == "ON":
            self.gctrl.gpio_pins[self.form['gpio']].change_mode('on')
            self.gctrl.gpio_pins[self.form['gpio']].write_cfg()
        elif self.form['send'] == "change":
            if self.form['mode'] == "sun":
                self.gctrl.gpio_pins[self.form['gpio']].change_mode('sun')
            elif self.form['mode'] == "time":
                dow = []
                for key,val in self.form['dow'].items():
                    if val is not None:
                        dow.append(key)
                pin_cfg = {'groups': self.form['groups'],
                      'start': self.form['start'],
                      'prio': self.form['prio'],
                      'duration': self.form['duration'],
                      'dow': ",".join(dow),
                      }
                self.gctrl.set_pin_cfg(self.form['gpio'], pin_cfg)
                self.gctrl. arrange_pins()
                self.gctrl.gpio_pins[self.form['gpio']].write_cfg()
            elif self.form['mode'] == "man":
                self.gctrl.gpio_pins[self.form['gpio']].change_mode('man')
                self.gctrl.gpio_pins[self.form['gpio']].write_cfg()
