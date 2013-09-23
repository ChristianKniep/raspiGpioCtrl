#! /usr/bin/env python
# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser
from raspi.pin import GpioPin, get_mode_id
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
        self.main_pins = {}

    def add_pin(self, pin):
        """
        add pin to ctrl instance
        """
        self.gpio_pins[pin.get_id()] = pin
        if 'main' in pin.get_groups():
            self.main_pins[pin.get_id()] = pin

    def read_cfg(self, force_init=True):
        """
        read cfg file and update gpio_pins dict
        """
        path = "%s/%s" % (PREFIX, self.gpio_cfg_path)
        for root, dirs, files in os.walk(path):
            for file_path in files:
                pin = GpioPin(self.opt, "%s/%s" % (root, file_path))
                pin.init_pin(force_init)
                self.gpio_pins[pin.get_id()] = pin

    def flip(self, pin_id):
        """
        flip the value of the given pin_identifier
        """
        assert pin_id in self.gpio_pins.keys()
        self.gpio_pins[pin_id].flip()
        self.trigger_main()

    def trigger_main(self):
        """
        if a rain relay is set switch the main relay
        -> check if more then two of a group is switched on
        """
        main_pinids = set(self.main_pins.keys())
        gpio_pinids = set(self.gpio_pins.keys())
        assert len(main_pinids) <= 1
        main_pinid = main_pinids[0]
        if self.main_pins[min_pinid].main_check():
            # if false, nothing to do, because main blocks everything
            for pin_id in set(main_pinids).difference(gpio_pinids):
                print pin_id
            
    

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

    def trigger_pins(self, dt=None):
        """
        iterate over pins.
        """
        for pin in self.gpio_pins.values():
            #-> first turn off
            pin.trigger_off(dt)
        for pin in self.gpio_pins.values():
            # -> after turn on (to avoid overlapping)
            pin.trigger_on(dt)
