#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Bibliotheken laden
import re
import os
import sys
import web
import subprocess
from pprint import pprint
from optparse import OptionParser
from ConfigParser import ConfigParser
from sunrise import SunRise
#

global cfg_file
cfg_file = "/root/example.cfg"

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
        (self.options, args) = self.parser.parse_args()
        
        # copy over all class.attributes
        self.args = args

    def get(self, name):
        """ return option value """
        if self.has_key(name):
            return self.__dict__[name]
        else:
            return None

    def has_key(self, name):
        """ checks whether an option exists or not """
        return name in self.__dict__.keys()


class WebServer(object):
    """ webpy server
    """
    def __init__(self, opt):
        self.opt = opt
        self.urls = (
            "/(.*)", "Dashboard",
            )
        self.gpio_pins = {
            #pin:{
            #  wo:<Sprechender Name>
            #  modus:zeit, sonnenstand oder manuell
            #  prio:wenn Kollision, dann wird nach Prioritaet vorgegangen
            #  zeit_an:UHRZEIT AN (wird genutzt wenn modus==zeit)
            #  dauer:Dauer in Minuten
            #  sun_delay=Minuten nach Sonnenuntergang (kann auch negativ sein)
            #  status:0/1 (wird eingelesen)
            #}
             'gpio4':{
                'wo':'Vorne',
                'modus':'zeit',
                'prio':'0',
                'zeit_an':"18:00",
                'dauer':"30",
                'sun_delay':'10',
                'status':0,
             },
             'gpio17':{
                'wo':'Mitte',
                'modus':'zeit',
                'prio':'0',
                'zeit_an':"18:00",
                'dauer':"30",
                'sun_delay':'10',
                'status':0,
             },
             'gpio18':{
                'wo':'Teich',
                'modus':'zeit',
                'prio':'0',
                'zeit_an':"18:00",
                'dauer':"30",
                'sun_delay':'10',
                'status':0,
             },
        }

    def run(self):
        """ bringt die Sache ans Laufen
        """
        self.config()
        app = web.application(self.urls, globals())
        app.run()
    
    def config(self):
        """ Lese Config ein
        """
        config = ConfigParser()
        config.read(cfg_file)
        for gpio in self.gpio_pins.keys():
            if gpio in config.sections():
                # Wenn es drin ist, dann ueberschreiben wir den default
                for option in config.options(gpio):
                    self.gpio_pins[gpio][option] = config.get(gpio, option)
            else:
                # Ansonsten legen wir die cfg an
                config.add_section(gpio)
                for key, val in self.gpio_pins[gpio].items():
                    config.set(gpio, key, val)
                filed = open(cfg_file, "wb")
                config.write(filed)
                filed.close()

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

class Dashboard(object):
    """ Klasse um GPIO-Pins auf Webseite zu stellen und aenderbar zu machen
    """
    gpio_pins = lese_config()
    
    def GET(self, gpio):
        """ HTML response
        """
        self.gpio_path = "/sys/class/gpio"
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
                <td>Dauer</td>
                <td>Sonnenverzoegerung</td>
            </tr>
        """
        self.lese_status()
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
                <td><b>%(wo)s</b></td>""" % self.gpio_pins[gpio]
        self.html += "<input type='hidden' name='gpio' value='%s'>" % gpio
        if self.gpio_pins[gpio]['status'] == "0":
            status_col = 'red'
        else:
            status_col = 'green'
        self.html += "<td style='background-color:%s'>" % status_col
        self.html += "<input name='send' type='submit' value='flip'></td>"
        self.html += """
                <td>"""
        for modus in ['zeit', 'sonne', 'manuell']:
            if self.gpio_pins[gpio]['modus'] == modus:
                checked = " checked"
            else:
                checked = ""
            self.html += """
                    <input type="radio" name="modus" value="%s"%s>%s""" % \
                            (modus, checked, modus)
        self.html += """
                </td>"""
        self.html += """
                <td><input type="text" name="zeit_an" value="%(zeit_an)s" size="6">Uhr</td>
                <td><input type="text" name="dauer" value="%(dauer)s" size="5">min</td>
                <td><input type="text" name="sun_delay" value="%(sun_delay)s" size="5">min</td>
                <td><input name="send" type="submit" value="aendern"></td>
            </form>
            </tr>""" % self.gpio_pins[gpio] 
    
    def lese_status(self):
        """ Wird vor dem Laden der Seite ausgefuehrt und liesst den Status
            der Pins aus
        """
        
        for gpio in self.gpio_pins.keys():
            pfad = "%s/%s/value" % (self.gpio_path, gpio)
            if not os.path.exists(pfad):
                self.init_gpio(gpio)
            else:
                fobj = open("/sys/class/gpio/%s/value" % gpio, "r")
                self.gpio_pins[gpio]['status'] = fobj.read().strip()
                fobj.close()
            self.create_row(gpio)
    

    def init_gpio(self, gpio):
        """ Initiere gpio-pin
        """
        reg = "gpio(\d+)"
        mat = re.match(reg, gpio)
        assert mat, "gpiopin '%s' ist nicht koscher!" % gpio
        gpio_nr =  mat.group(1)
        pfad = "%s/export" % (self.gpio_path)
        os.system("echo %s > %s" % (gpio_nr, pfad))
        pfad = "%s/%s/direction" % (self.gpio_path, gpio)
        os.system("echo out > %s" % (pfad))
        pfad = "%s/%s/value" % (self.gpio_path, gpio)
        os.system("echo 0 > %s" % (pfad))
    
 
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
 
    def POST(self, gpio):
        """ Behandle formular
        """
        form =  web.input()
        if form.send == "aendern":
            for key in form.keys():
                if key in ('send', 'gpio'):
                    continue
                if form[key] != self.gpio_pins[form.gpio][key]:
                    self.change_cfg(form.gpio, key, form[key])
            # Wenn Sonnensteuerung gewollt ist,
            # dann stellen wir schon mal die Zeit von heute ein
            if form.modus == "sonne":
                sun = SunRise()
                untergang = sun.sunset().strftime("%H:%M")
                self.change_cfg(form.gpio, 'zeit_an', untergang)
        if form.send == "flip":
            self.wechsel(form.gpio)
        raise web.redirect('/')
    
    def wechsel(self, gpiopin):
        """ liest gpiopin aus und wechselt den Zustand
        """
        fobj = open("/sys/class/gpio/%s/value" % gpiopin, "r")
        wert = fobj.read().strip()
        fobj.close()
        assert int(wert) in [0, 1], "Wertebereich verlassen '%s'" % wert
        if int(wert) == 1:
            self.schalten(0, gpiopin)
        else:
            self.schalten(1, gpiopin)
    
    @staticmethod
    def schalten(wert, gpiopin):
        """ Schaltet pin gpiopin auf wert 
        """ 
        assert (wert == 0) or (wert == 1), \
                " Ungueltiger Wert, Wert muss 0 (aus) oder 1 (ein) sein!"
        cmd = "echo %s > /sys/class/gpio/%s/value" % (wert, gpiopin)
        os.system(cmd)

def main():
    """ main function """
    # Parameter
    options = Parameter()
    
    ws = WebServer(options)
    ws.run()

# ein Aufruf von main() ganz unten
if __name__ == "__main__":
    main()
