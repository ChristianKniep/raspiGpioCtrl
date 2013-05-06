#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Bibliotheken laden
import re
import os
import web
import sys
import datetime
import time
from optparse import OptionParser
from ConfigParser import ConfigParser
from sunrise import SunRise
#

global cfg_file
cfg_file = "raspi_gpio.cfg"

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
            default=0, action="count", help="Erhoehe Debug-Level (-d:1, -ddd:3")
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
        
        # copy over all class.attributes
        (self.options, self.args) = self.parser.parse_args()
        # To allow webpy to use the sys.argv and not be bothered by the scripts
        # options sys.argv has to be altered. Kind of ugly, but ...
        del_argv = []
        for cnt in range(len(sys.argv)):
            if sys.argv[cnt] in ("-w", "-p", "--dry-run", "-j", "-c"):
                del_argv.append(sys.argv[cnt])
        for arg in del_argv:
            sys.argv.remove(arg)
        # 
        sys.argv.append(self.get("web_port"))

    def get(self, name):
        """ return option value """
        if name in self.options.__dict__.keys():
            return self.options.__dict__[name]
        else:
            raise IOError(("Option '%s' not found" % name))

global options
options = Parameter()


class GpioCtrl(object):
    """ webpy server
    """
    def __init__(self, opt):
        self.opt = opt
        self.gpio_pins = {
            #pin:{
            #  id:<one/two word name>
            #  mode:time, sun, man
            #  prio:if overlaping happens this should order the run(not implemented)
            #  on:when to switch on
            #  duration:<runtime in minutes>
            #  sun_delay=offset to sunset (negative value is possible)
            #  state:0/1 (will be read)
            #}
        }
        self.gpio_test = {
             'gpio4':{
                'id':'Front',
                'mode':'time',
                'prio':'0',
                'on':"18:00",
                'duration':"30",
                'sun_delay':'10',
                'state':0,
                'dow':'Mon,Tue,Wed,Thu,Fr,Sat,Sun',
             },
        }
        # since the /tmp/ directory is trashed
        # the webserver is only running once
        self.lock_dir = "/tmp/raspi_gpio_lockdir"
        if self.opt.get("dry_run"):
            self.gpio_path = "."
        else:
            self.gpio_path = "/sys/class/gpio"
        self.config()
        self.sun = SunRise()

    def run_webserver(self):
        """ bringt die Sache ans Laufen
        """
        if self.aquire_lock():
            self.urls = (
                "/(.*)", "Dashboard",
                )
            app = web.application(self.urls, globals())
            app.run()

    def aquire_lock(self, force=False):
        """ try to obtain lock file, return True if ok
            False otherwise. If forced, renew lock.
        """
        if not os.path.exists(self.lock_dir):
            os.mkdir(self.lock_dir)
            return True
        if force:
            os.remove(self.lock_dir)
            os.mkdir(self.lock_dir)
            return True
        return False

    def config(self):
        """ Lese Config ein
        """
        # default values
        config = ConfigParser()
        config.read(cfg_file)
        if self.opt.get("create_cfg"):
            for gpio in self.gpio_test.keys():
                if gpio not in config.sections():
                    # Ansonsten legen wir die cfg an
                    config.add_section(gpio)
                    for key, val in self.gpio_test[gpio].items():
                        config.set(gpio, key, val)
                    filed = open(cfg_file, "wb")
                    config.write(filed)
                    filed.close()
            config.read(cfg_file)
        for gpio in config.sections():
            self.gpio_pins[gpio] = {}
            for option in config.options(gpio):
                self.gpio_pins[gpio][option] = config.get(gpio, option)
        self.read_init_pins()
    
    def read_init_pins(self):
        ## init pins
        for gpio in self.gpio_pins.keys():
            pfad = "%s/%s/value" % (self.gpio_path, gpio)
            if not os.path.exists(pfad):
                self.init_gpio(gpio)
            else:
                self.read_gpiopin(gpio)

    def now_gt(self, clock):
        """ Checks whether the current time is greater then the given
            clock == datetime.object
        """
        mat = re.match("(?P<h>\d+):(?P<m>\d+)", clock)
        assert mat, "'%s' has to match H+:M+!" % clock
        cdic = mat.groupdict()
        now = datetime.datetime.now()
        clock_dt = datetime.datetime(
                    year=now.year, month=now.month, day=now.day,
                    hour=int(cdic['h']), minute=int(cdic['m']))
        return now > clock_dt

    def run_cronjob(self):
        """ runs a cronjob to update the sunset-times and
            flips the pins if needed
        """
        self.gpio_pins = self.lese_config()
        self.read_init_pins()
        self.sun = SunRise()
        for gpio in self.gpio_pins.keys():
            self.time_trigger(gpio)
    
    def time_trigger(self, gpio):
        """ reacts if the time should trigger something
        """
        if self.gpio_pins[gpio]['mode'] == 'manuell':
            # nothing to be done
            pass 
        else:
            if self.gpio_pins[gpio]['mode'] == 'sonne':
                # check the sunset-time
                self.set_sunset(gpio)
            # Now we check if there is something to do
            now = datetime.datetime.now()
            dow = time.strftime("%a")
            dow_go = True
            if 'dow' in self.gpio_pins[gpio].keys() and \
                        self.gpio_pins[gpio]['dow'] != "":
                dow_set = self.gpio_pins[gpio]['dow'].split(",")
                if dow not in dow_set:
                    dow_go = False
            gpio_on = self.get_dt_on(gpio)
            gpio_off = self.get_dt_off(gpio)
            if dow_go and gpio_on <= now <= gpio_off:
                if int(self.gpio_pins[gpio]['state']) != 1:
                    print self.gpio_pins[gpio]['state']
                    print "flip! %s" % gpio
                    self.wechsel(gpio)
                print "ON: ", gpio, self.gpio_pins[gpio]
            else:
                if int(self.gpio_pins[gpio]['state']) == 1:
                    print "flip! %s" % gpio
                    self.wechsel(gpio)
                print "OFF ", gpio, self.gpio_pins[gpio]
    
    def get_dt_on(self, gpio):
        """ returns a datetime instance with the date to switch on
        """
        (std, minute) = self.gpio_pins[gpio]['on'].split(":")
        now = datetime.datetime.now()
        temp_on = datetime.datetime(year=now.year,
                        month=now.month,
                        day=now.day,
                        hour=int(std),
                        minute=int(minute))
        return temp_on
    
    def get_dt_off(self, gpio):
        """ returns a datetime instance with the date to switch on + duration
        """
        (std, minute) = self.gpio_pins[gpio]['on'].split(":")
        now = datetime.datetime.now()
        temp_on = datetime.datetime(year=now.year,
                        month=now.month,
                        day=now.day,
                        hour=int(std),
                        minute=int(minute))
        offset = datetime.timedelta(0,
                        minutes=int(self.gpio_pins[gpio]['duration']))
        return temp_on + offset
    
    def set_sunset(self, gpio):
        """ set the sunset value
        """
        values = self.gpio_pins[gpio]
        untergang = self.sun.sunset()
        now = datetime.datetime.now()
        temp_on = datetime.datetime(year=now.year,
                        month=now.month,
                        day=now.day,
                        hour=untergang.hour,
                        minute=untergang.minute)
        offset = datetime.timedelta(0, minutes=int(values['sun_delay']))
        neue_on = temp_on + offset
        self.change_cfg(gpio, 'on',
                        neue_on.strftime("%H:%M"))
    
    @staticmethod
    def lese_config():
        """ Lese Config ein
        """
        config = ConfigParser()
        config.read(cfg_file)
        gpio_pins = {}
        for gpio in config.sections():
            gpio_pins[gpio] = {}
            for option in config.options(gpio):
                gpio_pins[gpio][option] = config.get(gpio, option)
        return gpio_pins

    def init_gpio(self, gpio):
        """ Initiere gpio-pin
        """
        reg = "gpio(\d+)"
        mat = re.match(reg, gpio)
        assert mat, "gpiopin '%s' ist nicht koscher!" % gpio
        gpio_nr =  mat.group(1)
        if not self.opt.get("dry_run"):
            pfad = "%s/export" % (self.gpio_path)
            os.system("echo %s > %s" % (gpio_nr, pfad))
            pfad = "%s/%s/direction" % (self.gpio_path, gpio)
            os.system("echo out > %s" % (pfad))
            pfad = "%s/%s/value" % (self.gpio_path, gpio)
            os.system("echo 0 > %s" % (pfad))
        else:
            pfad = "%s/%s" % (self.gpio_path, gpio)
            os.system("mkdir %s" % pfad)
            pfad = "%s/%s/value" % (self.gpio_path, gpio)
            os.system("echo 0 > %s" % (pfad))
    
    def schalten(self, wert, gpiopin):
        """ Schaltet pin gpiopin auf wert 
        """ 
        assert (wert == 0) or (wert == 1), \
                " Ungueltiger Wert, Wert muss 0 (aus) oder 1 (ein) sein!"
        cmd = "echo %s > %s/%s/value" % (wert, self.gpio_path, gpiopin)
        os.system(cmd)
        self.read_gpiopin(gpiopin)
    
    def read_gpiopin(self, gpiopin):
        """ read current status and updates gpio_pins dictonary
        """
        fobj = open("%s/%s/value" % (self.gpio_path, gpiopin), "r")
        new_state = fobj.read().strip()
        # Ugly quick fix, should be fixed in a better way
        if gpiopin not in self.gpio_pins.keys():
            self.gpio_pins[gpiopin] = {}
            self.gpio_pins[gpiopin]['state'] = 0
        if self.gpio_pins[gpiopin]['state'] != new_state:
            self.gpio_pins[gpiopin]['state'] = new_state
            self.change_cfg(gpiopin, 'state', new_state)
        
        fobj.close()
    
    def wechsel(self, gpiopin):
        """ liest gpiopin aus und wechselt den Zustand
        """
        fobj = open("%s/%s/value" % (self.gpio_path, gpiopin), "r")
        wert = fobj.read().strip()
        fobj.close()
        assert int(wert) in [0, 1], "Wertebereich verlassen '%s'" % wert
        if int(wert) == 1:
            self.schalten(0, gpiopin)
        else:
            self.schalten(1, gpiopin)
    
    def change_cfg(self, gpio, key, val):
        """ Update cfg und gpio_pins
        """
        self.gpio_pins[gpio][key] = val
        config = ConfigParser()
        config.read(cfg_file)
        config.set(gpio, key, val)
        filed = open(cfg_file, "wb")
        config.write(filed)
        filed.close()


class Dashboard(object):
    """ Klasse um GPIO-Pins auf Webseite zu stellen und aenderbar zu machen
    """
    # Da dies beim ersten Einlesen der Datei angelegt wird, ist
    # eine evtl neu angelegte Config noch nicht existent.
    # ist halt ein Klassen und kein Instanzen-Objekt. FWIW!
    gpio_ctrl = GpioCtrl(options)
    
    def GET(self, gpio):
        """ HTML response
        """
        self.gpio_pins = self.gpio_ctrl.lese_config()
        self.gpio_ctrl.read_init_pins()
            
        # Anfang der HTML Seite
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
    
    def POST(self, gpio):
        """ Behandle formular
        """
        self.gpio_pins = self.gpio_ctrl.lese_config()
        self.gpio_ctrl.read_init_pins()
        form =  web.input()
        if form.send == "change":
            dows = []
            reg_dow = re.compile("dow_(.*)")
            for key in form.keys():
                if key in ('send', 'gpio'):
                    continue
                mat_dow = re.match(reg_dow, key)
                if mat_dow:
                    dow = mat_dow.group(1)
                    dows.append(dow)
                    continue
                if form[key] != self.gpio_pins[form.gpio][key]:
                    self.gpio_ctrl.change_cfg(form.gpio, key, form[key])
            if 'dow' not in self.gpio_pins[form.gpio].keys() or \
               ",".join(dows) != self.gpio_pins[form.gpio]['dow']:
                self.gpio_ctrl.change_cfg(form.gpio, 'dow', ",".join(dows))
            # Wenn Sonnensteuerung gewollt ist,
            # dann stellen wir schon mal die Zeit von heute ein
            if form.mode == "sun":
                self.gpio_ctrl.set_sunset(form.gpio)
                self.gpio_ctrl.time_trigger(form.gpio)
        if form.send == "flip":
            self.gpio_ctrl.wechsel(form.gpio)
            self.gpio_ctrl.change_cfg(form.gpio, 'mode', "man")
        raise web.redirect('/')


def main():
    """ main function """
    # Parameter
    srv = GpioCtrl(options)
    if options.get("run_cronjob"):
        srv.run_cronjob()
    elif options.get("run_webserver"):
        srv.run_webserver()
        

# ein Aufruf von main() ganz unten
if __name__ == "__main__":
    main()
