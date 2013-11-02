#! /usr/bin/env python
# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser
from raspi.pin import MainPin, SlavePin, get_mode_id
from raspi import PREFIX
import os
import time
from pprint import pprint
import datetime

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

    def run_cron(self):
        """
        checks the pins one time and exit
        """
        self.read_cfg()
        self.trigger_pins()
        self.check_test_stop()
    
    def check_test_stop(self):
        """
        checks wether its time to stop the test
        """
        test_ongoing = {}
        now = datetime.datetime.now()
        for pin in self.gpio_pins.values():
            for grp in pin.get_groups().split(","):
                if grp not in test_ongoing:
                    test_ongoing[grp] = False
                if isinstance(pin, SlavePin):
                    if now < pin.get_dt_off():
                        test_ongoing[grp] |= True
        for pin in self.gpio_pins.values():
            if isinstance(pin, MainPin):
                # TODO: If one Main is part of two groups we got a problem
                for grp in pin.get_groups().split(","):
                    if not test_ongoing[grp]:
                        self.stop_test(pin)

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
                'crypt': 'eaa491247883b9b1cd0760bae439a253'
                }
            pin5.set_cfg(cfg, True)
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

    def start_test(self, main_pin):
        """
        Starts a testrun for group of given MainPin
        """
        assert isinstance(main_pin, MainPin)
        main_json = main_pin.get_json()
        now = datetime.datetime.now()
        offset = datetime.timedelta(0, minutes=int(main_json['test_dur']))
        tstart = now + offset
        cfg = {
            'test_state': '1',
            'test_start': tstart.strftime("%H:%M"),
            'test_dur': main_json['test_dur'],
        }
        for pin in self.gpio_pins.values():
            if main_pin.is_group_buddy(pin):
                print "cfg: ", cfg
                pin.set_cfg(cfg)
                pin.write_cfg()
        self.arrange_pins()
    
    def read_real_life(self):
        """
        read real life and update status
        """
        for pin in self.gpio_pins.values():
            pin.set_real_life()

    def stop_test(self, main_pin):
        """
        Starts a testrun for group of given MainPin
        """
        assert isinstance(main_pin, MainPin)
        cfg = {
            'test_state': '0',
        }
        for pin in self.gpio_pins.values():
            if main_pin.is_group_buddy(pin):
                pin.set_cfg(cfg)
                pin.write_cfg()

    def get_pin(self, pin_id):
        """
        return pin instance
        """
        return self.gpio_pins[str(pin_id)]

    def read_cfg(self, force_init=False):
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
                self.add_pin(pin)

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
                pin_json = item.get_json()
                if (end is not None) and (end > item.get_dt_on()):
                    # we have to set a new start and adjust the end
                    if pin_json['test_state'] == '0':
                        item.set_cfg({'start': end.strftime("%H:%M")})
                    else:
                        item.set_cfg({'test_start': end.strftime("%H:%M")})
                    item.write_cfg()
                end = item.get_dt_off()

    def shutdown_slaves(self):
        """
        iterate over pins and shut them down
        """
        for pin in self.gpio_pins.values():
            if isinstance(pin, MainPin):
                continue
            pin.set_pin(0)

    def fire_main(self, groups):
        """
        iterate over main pins and fire them up
        """
        grp_set = set(groups.split(","))
        for pin in self.gpio_pins.values():
            if isinstance(pin, MainPin):
                pin_grp = pin.get_groups().split(",")
                if len(grp_set.intersection(pin_grp)) > 0:
                    pin.set_pin(1)

    def shutdown_main(self):
        """
        iterate over main pins and shut them down
        """
        for pin in self.gpio_pins.values():
            if isinstance(pin, SlavePin):
                if pin.isstate(1):
                    pin.deb("I am still up! abort shut down main")
                    break
        else:
            for pin in self.gpio_pins.values():
                if isinstance(pin, MainPin):
                    pin.deb("I am shut down now")
                    pin.set_pin(0)

    def trigger_pins(self, dt=None):
        """
        iterate over pins.
        """
        for pin in self.gpio_pins.values():
            if isinstance(pin, MainPin):
                continue
            #-> first turn off
            if pin.trigger_off(dt):
                self.flip_slave(pin.pin_nr)
        for pin in self.gpio_pins.values():
            if isinstance(pin, MainPin):
                continue
            # -> after turn on (to avoid overlapping)
            if pin.trigger_on(dt):
                self.flip_slave(pin.pin_nr)

    def flip_slave(self, gpio):
        """
        checks if slave could be fliped
        """
        pin = self.get_pin(gpio)
        if pin.isstate(1):
            # switch off is possible at all times
            pin.flip()
            self.shutdown_main()
        else:
            main_check = self.check_main(pin.get_groups())
            grp_check = self.check_slaves(pin.get_groups())
            if main_check and grp_check:
                self.fire_main(pin.get_groups())
                pin.flip()
    
    def check_main(self, groups):
        """
        returns True if slave flip could be done, False otherwise
        """
        grp_set = set(groups.split(","))
        for pin in self.gpio_pins.values():
            if isinstance(pin, SlavePin):
                continue
            pin_grp = pin.get_groups().split(",")
            if len(grp_set.intersection(pin_grp)) > 0:
                if not pin.check():
                    return False
        return True

    def check_slaves(self, groups):
        """
        returns True if no other slave from group is switched on
        """
        grp_set = set(groups.split(","))
        for pin in self.gpio_pins.values():
            if isinstance(pin, MainPin):
                continue
            pin_grp = pin.get_groups().split(",")
            if len(grp_set.intersection(pin_grp)) > 0:
                if pin.isstate(1):
                    return False
        return True
