import unittest
import argparse
import os
import datetime
from raspi.ctrl import GpioCtrl, PREFIX
from raspi.pin import GpioPin, get_mode_id, PIN_MODES
from pprint import pprint

class TestRaspiGpio(unittest.TestCase):
    def setUp(self):
        self.opt = argparse.Namespace(debug=1, root="./packaged", dry_run=True)
        self.skip_keys = ['opt']
        self.def_items = {
            'gpio_cfg_path': "%s/etc/raspigpioctrl/" % (self.opt.root),
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
        ctrl.read_cfg()
        pincfg_path = "%s/%s/etc/raspigpioctrl/" % (PREFIX, self.opt.root)
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
        pincfg_path = "%s/%s/etc/raspigpioctrl/" % (PREFIX, self.opt.root)
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
        pincfg_path = "%s/%s/etc/raspigpioctrl/" % (PREFIX, self.opt.root)
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
        ctrl.arange_pins()
        self.check(ctrl, exp_items)

    def test4_0_trigger_pin(self):
        """
        GpioCtrl >4_0> trigger pins
        """
        ctrl = GpioCtrl(self.opt)
        ctrl.read_cfg()
        ctrl.set_pin_cfg('1', {'groups':'a',
                      'start':'00:00',
                      'prio':'0',
                      'duration':'10',
                      })
        ctrl.set_pin_cfg('2', {'groups':'a',
                      'start':'00:10',
                      'prio':'0',
                      'duration':'10',
                      })
        ctrl.set_pin_cfg('3', {'groups':'a',
                      'start':'00:25',
                      'prio':'0',
                      'duration':'10',
                      })
        now = datetime.datetime.now()
        dt = datetime.datetime(year=now.year,
                        month=now.month,
                        day=now.day,
                        hour=0,
                        minute=0)
        ctrl.trigger_pins(dt)
        self.assertTrue(ctrl.gpio_pins['1'].read_real_life() == '1')
        self.assertTrue(ctrl.gpio_pins['2'].read_real_life() == '0')
        self.assertTrue(ctrl.gpio_pins['3'].read_real_life() == '0')
        dt = datetime.datetime(year=now.year,
                        month=now.month,
                        day=now.day,
                        hour=0,
                        minute=11)
        ctrl.trigger_pins(dt)
        self.assertTrue(ctrl.gpio_pins['1'].read_real_life() == '0')
        self.assertTrue(ctrl.gpio_pins['2'].read_real_life() == '1')
        self.assertTrue(ctrl.gpio_pins['3'].read_real_life() == '0')
        dt = datetime.datetime(year=now.year,
                        month=now.month,
                        day=now.day,
                        hour=0,
                        minute=21)
        ctrl.trigger_pins(dt)
        self.assertTrue(ctrl.gpio_pins['1'].read_real_life() == '0')
        self.assertTrue(ctrl.gpio_pins['2'].read_real_life() == '0')
        self.assertTrue(ctrl.gpio_pins['3'].read_real_life() == '0')
        dt = datetime.datetime(year=now.year,
                        month=now.month,
                        day=now.day,
                        hour=0,
                        minute=30)
        ctrl.trigger_pins(dt)
        self.assertTrue(ctrl.gpio_pins['1'].read_real_life() == '0')
        self.assertTrue(ctrl.gpio_pins['2'].read_real_life() == '0')
        self.assertTrue(ctrl.gpio_pins['3'].read_real_life() == '1')
        dt = datetime.datetime(year=now.year,
                        month=now.month,
                        day=now.day,
                        hour=0,
                        minute=37)
        ctrl.trigger_pins(dt)
        self.assertTrue(ctrl.gpio_pins['1'].read_real_life() == '0')
        self.assertTrue(ctrl.gpio_pins['2'].read_real_life() == '0')
        self.assertTrue(ctrl.gpio_pins['3'].read_real_life() == '0')


if __name__ == '__main__':
    unittest.main()