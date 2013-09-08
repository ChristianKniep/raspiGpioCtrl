import unittest
import argparse
import os
import datetime
from raspi.ctrl import GpioCtrl, PREFIX
from raspi.pin import GpioPin, get_mode_id, PIN_MODES
from pprint import pprint

if not PREFIX.endswith("/"):
    PREFIX += "/"

class TestRaspiGpio(unittest.TestCase):
    def setUp(self):
        self.opt = {
            "-r":"packaged",
            "--dry-run":True,
        }
        self.skip_keys = ['opt']
        self.def_items = {
            'gpio_cfg_path': "%s/etc/raspigpioctrl/" % (self.opt['-r']),
            'gpio_pins': {},
        }

    def check(self, ctrl, exp_items=None):
        """
        check __dict__ for expected items
        """
        def_items = {}
        for key, val in self.def_items.items():
            if exp_items is not None and key in exp_items.keys():
                def_items[key] = exp_items[key]
            else:
                def_items[key] = self.def_items[key]
        
        for key, val in ctrl.__dict__.items():
            if key in self.skip_keys:
                continue
            if key == "gpio_pins":
                # check json of each gpiopin
                for pin_key, pin_inst in val.items():
                    got = pin_inst.get_json()
                    exp = def_items[key][pin_key].get_json()
                    amsg = "\nEXP\n%s\n" % exp
                    amsg += "GOT\n%s\n" % got
                    self.assertTrue(got == exp, amsg)
            else:
                amsg = "%s not in %s" % (key, ','.join(def_items.keys()))
                self.assertTrue(key in def_items.keys(), amsg)
                amsg = "\nEXP '%s' (%s) \n%s\n" % (key, type(def_items[key]),
                                                   def_items[key])
                amsg += "GOT '%s' (%s) \n%s\n" % (key, type(val), val)
                self.assertTrue(val == def_items[key], amsg)
            del def_items[key]
        amsg = "instance has items left: %s" % ','.join(def_items)
        self.assertTrue(len(def_items) == 0, amsg)

    def teardown(self):
        print ("TestUM:teardown() after each test method")

    def test0_0_init(self):
        """
        GpioCtrl >0_0> Check initial instance
        """
        ctrl = GpioCtrl(self.opt)
        self.check(ctrl)

    def test1_0_read_cfg_dir(self):
        """
        GpioCtrl >1_0> Read default config dir
        """
        ctrl = GpioCtrl(self.opt)
        ctrl.read_cfg(True)
        pincfg_path = "%s/%s/etc/raspigpioctrl/" % (PREFIX, self.opt['-r'])
        pin1 = GpioPin(self.opt, "%s/pin1.cfg" % pincfg_path)
        pin2 = GpioPin(self.opt, "%s/pin2.cfg" % pincfg_path)
        pin3 = GpioPin(self.opt, "%s/pin3.cfg" % pincfg_path)
        exp_items = {
            'gpio_pins': {
                '1': pin1,
                '2': pin2,
                '3': pin3,
            }
        }
        self.check(ctrl, exp_items)

    def test2_0_flip(self):
        """
        GpioCtrl >2_0> flip pin2
        """
        ctrl = GpioCtrl(self.opt)
        ctrl.read_cfg()
        ctrl.flip('2')
        gpio_sys = "%s/packaged/sys/class/gpio/" % PREFIX 
        print gpio_sys
        filed = open("%s/gpio2/value" % gpio_sys, "r")
        cont = filed.read().strip()
        filed.close()
        self.assertTrue(cont == "1", cont)
        ctrl.flip('2')
        gpio_sys = "%s./packaged/sys/class/gpio/" % PREFIX
        filed = open("%s/gpio2/value" % gpio_sys, "r")
        cont = filed.read().strip()
        filed.close()
        self.assertTrue(cont == "0", cont)

    def test3_0_check_arrangement(self):
        """
        GpioCtrl >3_0> Pins are not grouped
        """
        ctrl = GpioCtrl(self.opt)
        ctrl.read_cfg()
        ctrl.set_pin_cfg('1', {'groups':''})
        ctrl.set_pin_cfg('2', {'groups':''})
        ctrl.set_pin_cfg('3', {'groups':''})
        pincfg_path = "%s/%s/etc/raspigpioctrl/" % (PREFIX, self.opt['-r'])
        pin1 = GpioPin(self.opt, "%s/pin1.cfg" % pincfg_path)
        pin1.set_cfg({'groups':''})
        pin2 = GpioPin(self.opt, "%s/pin2.cfg" % pincfg_path)
        pin2.set_cfg({'groups':''})
        pin3 = GpioPin(self.opt, "%s/pin3.cfg" % pincfg_path)
        pin3.set_cfg({'groups':''})
        exp_items = {
            'gpio_pins': {
                '1': pin1,
                '2': pin2,
                '3': pin3,
            }
        }
        self.check(ctrl, exp_items)

    def test3_1_check_arrangement_group_collision(self):
        """
        GpioCtrl >3_1> Pins are grouped, times are equal, rpio differ
        """
        ctrl = GpioCtrl(self.opt)
        ctrl.read_cfg()
        ctrl.set_pin_cfg('1', {'groups':'a',
                      'start':'00:00',
                      'prio':'0',
                      'duration':'10',
                      })
        ctrl.set_pin_cfg('2', {'groups':'a',
                      'start':'00:00',
                      'prio':'1',
                      'duration':'10',
                      })
        ctrl.set_pin_cfg('3', {'groups':'a',
                      'start':'00:00',
                      'prio':'2',
                      'duration':'10',
                      })
        pincfg_path = "%s/%s/etc/raspigpioctrl/" % (PREFIX, self.opt['-r'])
        pin1 = GpioPin(self.opt, "%s/pin1.cfg" % pincfg_path)
        pin1.set_cfg({'groups':'a',
                      'start':'00:00',
                      'prio':'0',
                      'duration':'10',
                      })
        pin2 = GpioPin(self.opt, "%s/pin2.cfg" % pincfg_path)
        pin2.set_cfg({'groups':'a',
                      'start':'00:10',
                      'prio':'1',
                      'duration':'10',
                      })
        pin3 = GpioPin(self.opt, "%s/pin3.cfg" % pincfg_path)
        pin3.set_cfg({'groups':'a',
                      'start':'00:20',
                      'prio':'2',
                      'duration':'10',
                      })
        exp_items = {
            'gpio_pins': {
                '1': pin1,
                '2': pin2,
                '3': pin3,
            }
        }
        ctrl.arrange_pins()
        self.check(ctrl, exp_items)

    def test4_0_trigger_pin(self):
        """
        GpioCtrl >4_0> trigger pins
        """
        now = datetime.datetime.now()
        ctrl = GpioCtrl(self.opt)
        ctrl.read_cfg()
        cfg = {
            'groups':'a',
            'prio':'0',
            'duration':'10',
        }
        ctrl.set_pin_cfg('1', cfg)
        ctrl.set_pin_cfg('2', cfg)
        ctrl.set_pin_cfg('3', cfg)
        ctrl.set_pin_cfg('1', {'start':'00:00'})
        ctrl.set_pin_cfg('2', {'start':'00:10'})
        ctrl.set_pin_cfg('3', {'start':'00:25'})
        # t0
        dt = self.create_dt(0, 0)
        ctrl.trigger_pins(dt)
        mask = {'1': '1', '2': '0', '3': '0'}
        self.check_pins(ctrl, mask)
        # t1
        dt = self.create_dt(11, 0)
        ctrl.trigger_pins(dt)
        mask = {'1': '0', '2': '1', '3': '0'}
        self.check_pins(ctrl, mask)
        # t2
        dt = self.create_dt(21, 0)
        ctrl.trigger_pins(dt)
        mask = {'1': '0', '2': '0', '3': '0'}
        self.check_pins(ctrl, mask)
        # t3
        dt = self.create_dt(30, 0)
        ctrl.trigger_pins(dt)
        mask = {'1': '0', '2': '0', '3': '1'}
        self.check_pins(ctrl, mask)
        # t4
        dt = self.create_dt(37, 0)
        ctrl.trigger_pins(dt)
        mask = {'1': '0', '2': '0', '3': '0'}
        self.check_pins(ctrl, mask)

    def test5_0_iter_pins(self):
        """
        GpioCtrl >5_0> read cfg and iterate a couple of times over the pins
        """
        ctrl = GpioCtrl(self.opt)
        ctrl.read_cfg()
        cfg = {
            'groups':'a',
            'prio':'0',
            'duration':'10',
        }
        ctrl.set_pin_cfg('1', cfg)
        ctrl.set_pin_cfg('2', cfg)
        ctrl.set_pin_cfg('3', cfg)
        ctrl.set_pin_cfg('1', {'start':'00:05'})
        ctrl.set_pin_cfg('2', {'start':'00:10'})
        ctrl.set_pin_cfg('3', {'start':'00:15'})
        print "### Before arrange"
        for key, item  in ctrl.gpio_pins.items():
            print key, item.get_dt_on(), item.get_dt_off()
        ctrl.arrange_pins(True)
        print "### After arrange"
        for key, item  in ctrl.gpio_pins.items():
            print key, item.get_dt_on(), item.get_dt_off()
        # t0
        dt = self.create_dt(5, 0)
        ctrl.trigger_pins(dt)
        mask = {'1': '1', '2': '0', '3': '0'}
        self.check_pins(ctrl, mask)
        # t1
        dt = self.create_dt(16, 0)
        ctrl.trigger_pins(dt)
        mask = {'1': '0', '2': '1', '3': '0'}
        self.check_pins(ctrl, mask)
        # t2
        dt = self.create_dt(25, 0)
        ctrl.trigger_pins(dt)
        mask = {'1': '0', '2': '0', '3': '1'}
        self.check_pins(ctrl, mask)

    @staticmethod
    def create_dt(t_minute=None, t_hour=None,
                  t_day=None, t_month=None, t_year=None):
        """
        returns datetime
        """
        now = datetime.datetime.now()
        if t_minute is None:
            t_minute = now.minute 
        if t_hour is None:
            t_hour = now.hour 
        if t_day is None:
            t_day = now.day 
        if t_month is None:
            t_month = now.month 
        if t_year is None:
            t_year = now.year
        dt = datetime.datetime(year=t_year,
                        month=t_month,
                        day=t_day,
                        hour=t_hour,
                        minute=t_minute)
        return dt

    def check_pins(self, ctrl, mask):
        """
        check states of mask pins
        """
        for key, val in mask.items():
            got = ctrl.gpio_pins[key].read_real_life()
            amsg = "gpio%s>> EXP:%s GOT:%s" % (key, val, got)
            self.assertTrue(got == val, amsg)


if __name__ == '__main__':
    unittest.main()