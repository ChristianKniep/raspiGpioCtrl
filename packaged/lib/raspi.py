#! /usr/bin/env python
# -*- coding: utf-8 -*-

from optparse import OptionParser
from ConfigParser import ConfigParser
import sys
import os
import md5
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


class Parameter(object):
    """ parameter object """
    def __init__(self):
        # Parameterhandling
        usage = "scgather [options]"
        self.args = None
        self.options = None
        self.parser = OptionParser(usage=usage)
        self.default()

    def default(self):
        """ Default-Options """
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

    def get(self, name):
        """ return option value """
        if name in self.options.__dict__.keys():
            return self.options.__dict__[name]
        else:
            raise IOError(("Option '%s' not found" % name))


class GpioCtrl(object):
    """
    Controller of raspberry gpio pins
    """
    def __init__(self):
        """
        init gpio
        """
        self.gpio_pins = {}
        self.cfg_file = None

    def set_cfg(self, file_path):
        """
        Set file path of cfg_file
        """
        self.cfg_file = file_path

    def read_cfg(self):
        """
        read cfg file and update gpio_pins dict
        """
        config = ConfigParser()
        pass


class GpioPin(object):
    """
    Object that represents a pin
    """
    def __init__(self, cfg_file=None):
        """
        create object from cfg_file or empty one
        """
        self.cfg_file = None
        self.crypt = None
        self.pin_nr = '0'
        self.prio = '0'
        self.name = 'None'
        self.mode = '0'
        self.groups = ''
        self.start = '00:00'
        self.duration = '0'
        self.sun_delay = '0'
        self.state = '0'
        self.dow = 'Mon,Tue,Wed,Thu,Fr,Sat,Sun'
        if cfg_file is not None:
            self.cfg_file = cfg_file
            self.read_cfg()

    def read_cfg(self):
        """
        read in instance from cfg file
        """
        cfg = ConfigParser()
        assert os.path.exists(self.cfg_file)
        cfg.read(self.cfg_file)
        for opt in cfg.options('global'):
            self.__dict__[opt] = cfg.get('global', opt)
        self.crypt = self.get_md5()

    def get_md5(self, file_path=None):
        """
        returns md5 hash of file content
        """
        if file_path is None:
            filed = open(self.cfg_file, "r")
        else:
            filed = open(file_path, "r")
        crypt = md5.new(filed.read())
        filed.close()
        return crypt.hexdigest()

    def write_cfg(self, cfg_file=None):
        """
        write config to file - rereads if md5 has changed
        """
        crypt = None
        if cfg_file is None:
            # if no cfg_file is given, the instance should already have one
            assert self.cfg_file != None
        else:
            # if a cfg was given, it will be set as default file
            self.cfg_file = cfg_file

        if os.path.exists(self.cfg_file):
            # if the file exists we get the md5
            crypt = self.get_md5()
            if self.crypt == crypt:
                raise IOError("cfg file changed on disk!")

        cfg = ConfigParser()
        sec = 'global'
        cfg.add_section(sec)
        for key, val in self.get_json().items():
            cfg.set(sec, key, val)
        filed = open(cfg_file, "w")
        cfg.write(filed)
        filed.close()
        self.crypt = self.get_md5()

    def get_json(self):
        """
        return json
        """
        res = {
            'nr': self.pin_nr,
            'name': self.name,
            'mode': PIN_MODES[self.mode],
            'prio': self.prio,
            'on': self.start,
            'duration': self.duration,
            'sun_delay': self.sun_delay,
            'state': self.state,
            'dow': self.dow,
            'groups': self.groups,
        }
        return res



class Web(object):
    """
    Webside modeled as an cherrypy class
    """
    def __init__(self, opt):
        self.cfg_file = "/etc/raspi_gpio.cfg"
        self.gctrl = GpioCtrl(opt)
        self.gpio_pins = self.gctrl.gpio_pins
        pprint(self.gpio_pins)
        self.form_gpio = None
        self.form_on = None
        self.form_dow_Wed = None
        self.form_dow_Sun = None
        self.form_dow_Sat = None
        self.form_dow_Tue = None
        self.form_sun_delay = None
        self.form_dow_Mon = None
        self.form_send = None
        self.form_duration = None
        self.form_dow_Thu = None
        self.form_mode = None

    def create_row(self, gpio):
        """ Erstellt Zeile fuer gpio-pin in Form eines Formulars
        """
        self.html += """
            <tr>
            <form method="POST">
                <td><b>%(id)s</b></td>""" % self.gpio_pins[gpio]
        self.html += "<input type='hidden' name='gpio' value='%s'>" % gpio
        if self.gpio_pins[gpio]['state'] == "0":
            state_col = 'red'
        else:
            state_col = 'green'
        self.html += "<td style='background-color:%s'>" % state_col
        self.html += "<input name='send' type='submit' value='flip'></td>"
        self.html += """
                <td>"""
        for mode in ['time', 'sun', 'man']:
            if self.gpio_pins[gpio]['mode'] == mode:
                checked = " checked"
            else:
                checked = ""
            self.html += """
                    <input type="radio" name="mode" value="%s"%s>%s""" % \
                            (mode, checked, mode)
        self.html += """
                </td>"""
        self.html += """
                <td><input type="text" name="on" value="%(on)s" size="6">o'clock (24h)</td>
                <td>""" % self.gpio_pins[gpio]
        for dow in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
            checked = ""
            if 'dow' in self.gpio_pins[gpio].keys() and \
               re.match(".*%s.*" % dow, self.gpio_pins[gpio]['dow']):
                checked = " checked"
            self.html += "<input type='checkbox' name='dow_%s' value='%s'%s>%s" % (dow, dow, checked, dow)
        self.html += "</td>"
        self.html += """
                <td><input type="text" name="duration" value="%(duration)s" size="5">min</td>
                <td><input type="text" name="sun_delay" value="%(sun_delay)s" size="5">min</td>
                <td><input name="send" type="submit" value="change"></td>
            </form>
            </tr>""" % self.gpio_pins[gpio]

    def create_tab(self):
        """ Creates table to show the different gpiopins
        """
        for gpio in self.gpio_pins.keys():
            self.create_row(gpio)

    @cherrypy.expose
    def index(self, gpio=None, on=None, dow_Wed=None, dow_Sun=None,
              dow_Sat=None, dow_Tue=None, sun_delay=None, dow_Mon=None,
              send=None, duration=None, dow_Thu=None, mode=None):
        """
        Creates the list of gpio pins and handles changes
        """
        if gpio != None:
            self.form_gpio = gpio
            self.form_on = on
            self.form_dow_Wed = dow_Wed
            self.form_dow_Sun = dow_Sun
            self.form_dow_Sat = dow_Sat
            self.form_dow_Tue = dow_Tue
            self.form_sun_delay = sun_delay
            self.form_dow_Mon = dow_Mon
            self.form_send = send
            self.form_duration = duration
            self.form_dow_Thu = dow_Thu
            self.form_mode = mode
            self.change()
        self.html = """
        <html><head>
                <title>web.py</title>
        </head><body><table border="1">
            <tr align="center">
                <td> </td>
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
        </table></body></html>
        """
        return self.html

    def change(self):
        """
        Triggered if Web-GUI wants to change a pin
        """
        print "%s! %s" % (self.form_send, self.form_gpio)
        if self.form_send == "flip":
            pass
        elif self.form_send == "change":
            if self.form_mode == "sun":
                self.gpio_ctrl.set_sunset(self.form_gpio)
