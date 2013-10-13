#! /usr/bin/env python
# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser
from raspi.pin import MainPin, SlavePin, get_mode_id
from raspi import PREFIX
import os
from pprint import pprint


class GpioCtrl(object):
    """
    Controller of raspberry gpio pins
    """
    def __init__(self, opt):
        """
        init gpio
        """
        self.opt = opt
        self.gpio_cfg_path = "%s/etc/raspigpioctrl/" % opt['-r']
        self.gpio_pins = {}

    def add_pin(self, pin):
        """
        add pin to ctrl instance
        """
        self.gpio_pins[pin.get_id()] = pin

    def run_scenario(self):
        """
        run scenario w/o config files
        """
        if self.opt['--test'] == 'test1':
            pin1 = SlavePin(self.opt)
            cfg = {
                'dow': 'Mon,Tue,Wed,Thu,Fri,Sat,Sun',
                'duration': '60',
                'groups': 'grpA',
                'name': 'TestPin1',
                'pin_nr': '1',
                'start': '01:00',
            }
            pin1.set_cfg(cfg)
            pin1.set_pin(0)
            pin1.change_mode('time')
            pin1.val_path = "%s/gpio%s/value" % (pin1.gpio_base, 1)
            self.add_pin(pin1)
            pin5 = MainPin(self.opt)
            cfg = {
                'groups': 'grpA',
                'name': 'MainPin5',
                'pin_nr': '5',
                }
            pin5.set_cfg(cfg)
            pin5.val_path = "%s/gpio%s/value" % (pin1.gpio_base, 5)
            pin5.cfg_file = "%s/packaged/etc/raspigpioctrl/main5.cfg" % (os.environ["WORKSPACE"])
            pin5.change_mode('off')
            pin5.set_pin(0)
            self.add_pin(pin5)

    def show_pins(self):
        """
        prints strings
        """
        for pin_id, pin in self.gpio_pins.items():
            print pin_id

    def get_pin(self, pin_id):
        """
        return pin instance
        """
        return self.gpio_pins[str(pin_id)]

    def read_cfg(self, force_init=True):
        """
        read cfg file and update gpio_pins dict
        """
        path = "%s/%s" % (PREFIX, self.gpio_cfg_path)
        for root, dirs, files in os.walk(path):
            for file_path in files:
                if file_path.startswith("main"):
                    pin = MainPin(self.opt, "%s/%s" % (root, file_path))
                else:
                    pin = SlavePin(self.opt, "%s/%s" % (root, file_path))
                pin.init_pin(force_init)
                self.gpio_pins[pin.get_id()] = pin

    def flip(self, flip_pin_id):
        """
        flip the value of the given pin_identifier
        """
        assert flip_pin_id in self.gpio_pins.keys()
        fpin = self.gpio_pins[flip_pin_id]
        # if it's a SlavePin we continue
        if fpin.state == "1":
            # if the pin is to be turned off, we do not care about main-pins
            fpin.flip()
            assert fpin.isstate(0)
        else:
            if isinstance(fpin, MainPin):
                fpin.flip()
            else:
                # if we are about to fire him up, we care
                main_block = False
                for pin_id, pin in self.gpio_pins.items():
                    if isinstance(pin, MainPin):
                        if pin.mode == "off" and pin.isstate(0):
                            # nothing we can do about it, user wants to stay put
                            main_block = True
                if not main_block:
                    fpin.flip()
                    assert fpin.isstate(1)

    def set_pin(self, pin_id, val):
        """
        sets specific pin to specific val
        """
        assert pin_id in self.gpio_pins.keys()
        assert val in ('1', '0', 0, 1)
        self.gpio_pins[pin_id].set_pin(val)

    def set_pin_cfg(self, pin_id, cfg_dic):
        """
        Change the config of one pin
        """
        assert pin_id in self.gpio_pins.keys()
        self.gpio_pins[pin_id].set_cfg(cfg_dic)

    def arrange_pins(self, debug=False):
        """
        check the pins for overlapping within groups
        """
        # for every group the
        grp_times = {}
        for pin in self.gpio_pins.values():
            if isinstance(pin, MainPin):
                continue
            grp = pin.get_groups()
            if grp not in grp_times.keys():
                grp_times[grp] = []
            grp_times[grp].append(pin)
        for grp, lst in grp_times.items():
            end = None
            lst.sort()
            for item in lst:
                # check times and change if neccessary
                if (end is not None) and (end > item.get_dt_on()):
                    # we have to set a new start and adjust the end
                    item.set_cfg({'start': end.strftime("%H:%M")})
                end = item.get_dt_off()

    def shutdown_slaves(self):
        """
        iterate over pins and shut them down
        """
        for pin in self.gpio_pins.values():
            if isinstance(pin, MainPin):
                continue
            pin.set_pin(0)

    def trigger_pins(self, dt=None):
        """
        iterate over pins.
        """
        for pin in self.gpio_pins.values():
            if isinstance(pin, MainPin):
                continue
            #-> first turn off
            pin.trigger_off(dt)
        for pin in self.gpio_pins.values():
            if isinstance(pin, MainPin):
                continue
            # -> after turn on (to avoid overlapping)
            pin.trigger_on(dt)

    def check_main(self, groups):
        """
        returns True if slave flip could be done, False otherwise
        """
        grp_set = set(groups.split(","))
        for pin in self.gpio_pins.values():
            if isinstance(pin, SlavePin):
                continue
            if len(grp_set.intersection(pin.get_groups())) > 0:
                if not pin.check():
                    return False
        return True