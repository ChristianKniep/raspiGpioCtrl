#! /usr/bin/env python
# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser
import sys
import os
import subprocess
import md5
import datetime
import traceback

from raspi import PREFIX

PIN_MODES = {
    '0': 'off',
    '1': 'time',
    '2': 'man',
    '3': 'sun',
    '4': 'on',
}


def get_mode_id(mode):
    """
    reverse lookup of PIN_MODES
    """
    for key, val in PIN_MODES.items():
        if val == mode:
            return key
    return None


class BasePin(object):
    """
    the basic pin, could be slave or main
    """
    def __init__(self, opt, cfg_file=None):
        """
        create object from cfg_file or empty one
        """
        self.opt = opt
        self.gpio_base = "%s%s/sys/class/gpio" % (PREFIX, opt['-r'])
        self.cfg_file = None
        self.crypt = None
        self.pin_nr = '0'
        self.name = 'None'
        self.mode = 'off'
        self.groups = ''
        self.state = '0'
        if cfg_file is not None:
            self.cfg_file = cfg_file
            self.read_cfg()
        self.pin_base = "%s/gpio%s" % (self.gpio_base, self.pin_nr)

    def get_groups(self):
        """
        return identifier on which a sort should be done
        """
        return self.groups

    def get_id(self):
        """
        return identifier on which a sort should be done
        """
        return self.pin_nr

    def deb(self, msg, dlevel=1):
        """
        Print debug message
        """
        if self.opt['-d'] >= dlevel:
            print "%s >> %s" % (dlevel, msg)

    def init_pin(self, force_init=False):
        """
        Init pin
        """
        pin_name = "gpio%s" % self.pin_nr
        if not self.pin_val_exists() or force_init:
            if not self.opt['--dry-run']:
                pfad = "%s/%s" % (self.gpio_base, pin_name)
                os.system("echo %s > %s" % (self.pin_nr, pfad))
                os.system("echo out > %s" % (pfad))
                self.set_pin(0)
            else:
                pfad = "%s/%s" % (self.gpio_base, pin_name)
                os.system("mkdir -p %s" % pfad)
                self.set_pin(0)
        else:
            self.set_real_life()

    def set_real_life(self):
        """
        read real live value and overwrite current state
        """
        rl_val = self.read_real_life()
        if self.state != rl_val:
            self.state = rl_val
            print "PinNR %s: Overwrite pin_state with RL (%s)" % \
                  (self.pin_nr, rl_val)

    def read_cfg(self):
        """
        read in instance from cfg file
        """
        cfg = ConfigParser()
        amsg = "'%s' does not exists..." % self.cfg_file
        assert os.path.exists(self.cfg_file), amsg
        cfg.read(self.cfg_file)
        for opt in cfg.options('global'):
            self.__dict__[opt] = str(cfg.get('global', opt))
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
            amsg = "if no cfg_file is given, the instance should already have one"
            assert self.cfg_file is not None, amsg
            # if a cfg was given, it will be set as default file
        else:
            self.cfg_file = cfg_file

        if os.path.exists(self.cfg_file):
            self.deb(self.cfg_file)
            # if the file exists we get the md5
            crypt = self.get_md5()
            self.deb(crypt)
            if self.crypt != crypt:
                raise IOError("cfg file changed on disk!")

        cfg = ConfigParser()
        sec = 'global'
        cfg.add_section(sec)
        for key, val in self.get_json().items():
            cfg.set(sec, key, val)
        filed = open(self.cfg_file, "w")
        cfg.write(filed)
        filed.close()
        self.crypt = self.get_md5()
        self.val_path = "%s/gpio%s/value" % (self.gpio_base, self.pin_nr)

    def read_real_life(self):
        """
        """
        pfad = "%s/value" % self.pin_base
        filed = open(pfad, "r")
        cont = filed.read().strip()
        filed.close()
        return cont

    def pin_val_exists(self):
        """
        returns True if file exists
        """
        pfad = "%s/value" % (self.pin_base)
        print pfad
        return os.path.exists(pfad)

    def set_pin(self, val):
        """
        set pin to value
        """
        pfad = "%s/value" % (self.pin_base)
        cmd = "echo %s > %s" % (val, pfad)
        err = os.system(cmd)
        self.state = str(val)



class SlavePin(BasePin):
    """
    Object that represents a pin
    """
    def __init__(self, opt, cfg_file=None):
        """
        create object from cfg_file or empty one
        """
        super(SlavePin, self).__init__(opt, cfg_file)
        self.prio = '0'
        self.start = '00:00'
        self.duration = '0'
        self.sun_delay = '0'
        self.dow = 'Mon,Tue,Wed,Thu,Fr,Sat,Sun'

    def __eq__(self, other):
        """
        compares to instances ==
        """
        start = self.start == other.start
        prio = self.prio == other.prio
        duration = self.duration == other.duration
        groups = set(self.groups.split(",")) == set(other.groups.split(","))
        return start and prio and duration

    def __ne__(self, other):
        """
        compares to instances '=='
        """
        return not self.__eq__(other)

    def __lt__(self, other):
        """
        self < other?
        """
        if self.start < other.start:
            return True
        elif self.start > other.start:
            return False
        elif self.prio < other.prio:
            return True
        elif self.prio > other.prio:
            return False
        elif self.duration < other.duration:
            return True
        else:
            return False

    def __le__(self, other):
        """
        self <= other?
        """
        if self.start < other.start:
            return True
        elif self.start > other.start:
            return False
        elif self.prio < other.prio:
            return True
        elif self.prio > other.prio:
            return False
        elif self.duration <= other.duration:
            return True
        else:
            return False

    def __gt__(self, other):
        """
        self > other?
        """
        if self.start > other.start:
            return True
        elif self.start < other.start:
            return False
        elif int(self.prio) > int(other.prio):
            return True
        elif self.prio < other.prio:
            return False
        elif self.duration > other.duration:
            return True
        else:
            return False

    def __ge__(self, other):
        """
        self >= other?
        """
        if self.start > other.start:
            return True
        elif self.start < other.start:
            return False
        elif self.prio > other.prio:
            return True
        elif self.prio < other.prio:
            return False
        elif self.duration >= other.duration:
            return True
        else:
            return False

    def set_cfg(self, cfg_dic):
        """
        Alter the config, only a number of cfgs are changable
        """
        w_able = ['pin_nr', 'prio', 'name', 'groups', 'start',
                  'duration', 'sun_delay', 'dow']
        for key, val in cfg_dic.items():
            assert key in w_able, "%s not allowed to be set" % key
            self.__dict__[key] = str(val)
            if key == "pin_nr":
                self.pin_base = "%s/gpio%s" % (self.gpio_base, self.pin_nr)
                self.init_pin()

    def change_mode(self, mode_str):
        """
        change mode
        """
        for key, val in PIN_MODES.items():
            if val == mode_str:
                self.mode = mode_str
                break
        else:
            raise ValueError("%s is no valid mode" % mode_str)

    def get_json(self):
        """
        return json
        """
        res = {
            'pin_nr': self.pin_nr,
            'name': self.name,
            'mode': self.mode,
            'prio': self.prio,
            'start': self.start,
            'duration': self.duration,
            'sun_delay': self.sun_delay,
            'state': self.state,
            'dow': self.dow,
            'groups': self.groups,
        }
        return res

    def flip(self):
        """
        changes the value of the pin
        """
        if self.state == "0":
            self.set_pin(1)
        else:
            self.set_pin(0)

    def get_dt_on(self):
        """
        returns a datetime instance with the date to switch on
        """
        (std, minute) = self.start.split(":")
        now = datetime.datetime.now()
        temp_on = datetime.datetime(year=now.year,
                                    month=now.month,
                                    day=now.day,
                                    hour=int(std),
                                    minute=int(minute))
        return temp_on

    def get_dt_off(self):
        """
        returns a datetime instance with the date to switch on + duration
        """
        (std, minute) = self.start.split(":")
        now = datetime.datetime.now()
        temp_on = datetime.datetime(year=now.year,
                                    month=now.month,
                                    day=now.day,
                                    hour=int(std),
                                    minute=int(minute))
        offset = datetime.timedelta(0,
                                    minutes=int(self.duration))
        return temp_on + offset

    def trigger_off(self, dt=None):
        """
        checks off date and turn off, if the time is right
        """
        if dt is None:
            dt = datetime.datetime.now()
        off = self.get_dt_off()
        if off <= dt and self.state == '1' \
           and self.mode not in ('manual'):
            self.set_pin(0)

    def trigger_on(self, dt=None):
        """
        checks off date and turn off, if the time is right
        """
        if dt is None:
            dt = datetime.datetime.now()
        on = self.get_dt_on()
        off = self.get_dt_off()
        if on <= dt and off > dt and self.state == '0' \
           and self.mode not in (get_mode_id('manual'), get_mode_id('off')):
            self.set_pin(1)


class MainPin(BasePin):
    """
    Main gpio_pin serves as a global switch that activates a fuse or
    a pump.
    """
    def __init__(self, opt, cfg_file=None):
        """
        init main pin
        """
        super(MainPin, self).__init__(opt, cfg_file)
        self.mode = "off"

    def get_json(self):
        """
        return json
        """
        res = {
            'pin_nr': self.pin_nr,
            'name': self.name,
            'mode': self.mode,
            'state': self.state,
            'groups': self.groups,
            }
        return res

    def check(self):
        """
        returns True if main does not block the whole think
        > if mode==off and state==0: user did not want to rain at all
        > elif mode==on: could be fliped on
        """
        if self.mode == "off" and self.state == "0":
            return False
        elif self.mode == "ON":
            return True

    def change_mode(self, mode_str):
        """
        change mode
        """
        if mode_str in ("on", "off"):
            self.mode = mode_str
        else:
            raise ValueError("%s is no valid mode" % mode_str)

    def set_cfg(self, cfg_dic):
        """
        Alter the config, only a number of cfgs are changable
        """
        w_able = ['pin_nr', 'name', 'groups', 'dow']
        for key, val in cfg_dic.items():
            assert key in w_able, "%s not allowed to be set" % key
            self.__dict__[key] = str(val)
            if key == "pin_nr":
                self.pin_base = "%s/gpio%s" % (self.gpio_base, self.pin_nr)
                self.init_pin()

    def flip(self):
        """
        changes the value of the pin
        """
        # could only be switch if not in auto-mode
        if self.state == "0" and self.mode == "off":
            self.set_pin(1)
        else:
            self.set_pin(0)
