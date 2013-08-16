import unittest
import os
import argparse
import datetime
from ConfigParser import ConfigParser
from raspi.pin import GpioPin, PIN_MODES

PREFIX = os.environ.get("WORKSPACE", ".")

class TestRaspiPin(unittest.TestCase):
    def setUp(self):
        self.opt = argparse.Namespace(debug=1, root=".", dry_run=True)
        self.pin0 = GpioPin(self.opt)
        self.skip_keys = ['opt']

    def teardown(self):
        print ("TestUM:teardown() after each test method")

    def check_dict(self, pin, exp_items):
        """
        check __dict__ for expected items
        """
        for key, val in pin.__dict__.items():
            if key in self.skip_keys:
                continue
            amsg = "%s not in %s" % (key, ','.join(exp_items.keys()))
            self.assertTrue(key in exp_items.keys(), amsg)
            amsg = "\nEXP '%s' (%s) \n%s\n" % (key, type(exp_items[key]),
                                             exp_items[key])
            amsg += "GOT '%s' (%s) \n%s\n" % (key, type(val), val)
            self.assertTrue(val == exp_items[key], amsg)
            del exp_items[key]
        amsg = "instance has items left: %s" % ','.join(exp_items)
        self.assertTrue(len(exp_items) == 0, amsg)

    def test0_0_init(self):
        """
        Pin >0_0> check items in initial __dict__
        """
        exp_items = {
            'crypt': None,
            'pin_nr': '0',
            'cfg_file': None,
            'name': 'None',
            'prio': '0',
            'mode': '0',
            'groups': '',
            'start': '00:00',
            'duration': '0',
            'sun_delay': '0',
            'state': '0',
            'dow': 'Mon,Tue,Wed,Thu,Fr,Sat,Sun',
            'gpio_base': "./sys/class/gpio",
            'pin_base': "./sys/class/gpio/gpio0",
        }
        self.check_dict(self.pin0, exp_items)

    def test0_1_init_cfg(self):
        """
        Pin >0_1> check items in initial __dict__ from test1.cfg
        """
        test1_file = "%s/packaged/etc/raspigpioctrl/pin1.cfg" % PREFIX
        pin1 = GpioPin(self.opt, test1_file)
            
        exp_items = {
            'crypt': '045ca070608fe91b1066b98e8180d635',
            'pin_nr': '1',
            'cfg_file': test1_file,
            'name': 'Front',
            'prio': '0',
            'mode': '1',
            'groups': 'garden',
            'start': '01:00',
            'duration': '60',
            'sun_delay': '0',
            'state': '0',
            'dow': 'Wed,Sun',
            'gpio_base': "./sys/class/gpio",
            'pin_base': "./sys/class/gpio/gpio1",
        }
        self.check_dict(pin1, exp_items)

    def test0_3_init(self):
        """
        Pin >0_3> change cfg of init_pin
        """
        pin = GpioPin(self.opt)
        exp_items = {
            'crypt': None,
            'pin_nr': '1',
            'cfg_file': None,
            'name': 'Front',
            'prio': '0',
            'mode': '0',
            'groups': '',
            'start': '00:00',
            'duration': '0',
            'sun_delay': '0',
            'state': '0',
            'dow': 'Mon,Tue,Wed,Thu,Fr,Sat,Sun',
            'gpio_base': "./sys/class/gpio",
            'pin_base': "./sys/class/gpio/gpio1",
        }
        cfg = {
            'pin_nr': '1',
            'name': 'Front',
        }
        pin.set_cfg(cfg)
        self.check_dict(pin, exp_items)

    def test0_2_md5(self):
        """
        Pin >0_2> check md5 of default test-file
        """
        crypt = self.pin0.get_md5("%s/misc/md5_check" % PREFIX)
        self.assertTrue("8c77efd73d331fb65bef594e2c854894" == crypt)

    def test1_0_get_json(self):
        """
        Pin >1_0> get initial json
        """
        json = self.pin0.get_json()
        exp = {
                'nr': '0',
                'groups': '',
                'name': 'None',
                'mode': 'off',
                'prio': '0',
                'on': "00:00",
                'duration': '0',
                'sun_delay': '0',
                'state': '0',
                'dow': 'Mon,Tue,Wed,Thu,Fr,Sat,Sun',
             }
        amsg = "EXP\n%s\n!=\nGOT\n%s\n" % (exp, json)
        self.assertTrue(json == exp, amsg)

    def test2_0_save_cfg(self):
        """
        Pin >2_0> Write empty pin0
        """
        cfg_file = '%s/misc/tmp_test.cfg' % PREFIX
        if os.path.exists(cfg_file):
            os.remove(cfg_file)
        pin = GpioPin(self.opt)
        pin.write_cfg(cfg_file)
        self.assertTrue(pin.crypt == '730f699d91ae6beb84bab4ae8362e55b',
                        "CRYPT: %s" % pin.crypt)
        os.remove(cfg_file)

    def test2_1_save_cfg(self):
        """
        Pin >2_1> Write real pin1 cfg
        """
        test1_cfg = "%s/packaged/etc/raspigpioctrl/pin1.cfg" % PREFIX
        pin = GpioPin(self.opt, test1_cfg)
        pin.start = "10:00"
        pin.duration = "30"
        pin.dow = "Fri,Sat,Sun"
        cfg_file = '%s/misc/tmp_test.cfg' % PREFIX
        if os.path.exists(cfg_file):
            os.remove(cfg_file)
        pin.write_cfg(cfg_file)
        self.assertTrue(pin.crypt == '0d8e37fb31e650472960e42be02b80f6',
                        "CRYPT: %s" % pin.crypt)
        os.remove(cfg_file)

    def test2_2_failed_save_cfg(self):
        """
        Pin >2_2> Write cfg with changed cfg-file in background (IOError)
        """
        test1_cfg = "%s/packaged/etc/raspigpioctrl/pin1.cfg" % PREFIX
        pin = GpioPin(self.opt, test1_cfg)
        cfg = {
            'start': "10:00",
            'duration': "30",
            'dow': "Fri,Sat,Sun"
        }
        pin.set_cfg(cfg)
        cfg_file = '%s/misc/tmp_test.cfg' % PREFIX
        if os.path.exists(cfg_file):
            os.remove(cfg_file)
        pin.write_cfg(cfg_file)
        self.assertTrue(pin.crypt == '0d8e37fb31e650472960e42be02b80f6',
                        "CRYPT: %s" % pin.crypt)
        
        cfg = {'start': "10:30"}
        pin.set_cfg(cfg)
        os.system("echo FooBar >> %s" % cfg_file)
        self.assertRaises(IOError, pin.write_cfg, (cfg_file))
        os.remove(cfg_file)

    def test3_0_pin(self):
        """
        Pin >3_0> init dry-run pin
        """
        test1_file = "%s/packaged/etc/raspigpioctrl/pin1.cfg" % PREFIX
        pin1 = GpioPin(self.opt, test1_file)
        gpio_sys = "./sys/class/gpio/"
        if os.path.exists("./sys"):
            print os.system("rm -rf ./sys")
            pin1.deb("'%s' removed")
            self.assertFalse(os.path.exists(gpio_sys), "")
        pin1.init_pin()
        filed = open("%s/gpio1/value" % gpio_sys, "r")
        cont = filed.read().strip()
        self.assertTrue(cont == "0", cont)

    def test3_1_pin(self):
        """
        Pin >3_1> read_real_life()
        """
        test1_file = "%s/packaged/etc/raspigpioctrl/pin1.cfg" % PREFIX
        pin1 = GpioPin(self.opt, test1_file)
        self.assertTrue("0" == pin1.read_real_life())
        pin1.flip()
        self.assertTrue("1" == pin1.read_real_life())

    def test3_2_pin(self):
        """
        Pin >3_2> init dry-run pin and set_pin(1) / set_pin(0)
        """
        test1_file = "%s/packaged/etc/raspigpioctrl/pin1.cfg" % PREFIX
        pin1 = GpioPin(self.opt, test1_file)
        gpio_sys = "./sys/class/gpio/"
        if os.path.exists("./sys"):
            print os.system("rm -rf ./sys")
            pin1.deb("'%s' removed")
            self.assertFalse(os.path.exists(gpio_sys), "")
        pin1.init_pin()
        pin1.set_pin(1)
        filed = open("%s/gpio1/value" % gpio_sys, "r")
        cont = filed.read().strip()
        filed.close()
        self.assertTrue(cont == "1", cont)
        pin1.set_pin(0)
        filed = open("%s/gpio1/value" % gpio_sys, "r")
        cont = filed.read().strip()
        filed.close()
        self.assertTrue(cont == "0", cont)
    
    def test3_3_flip(self):
        """
        Pin >3_3> init dry-run pin and flip twice
        """
        test1_file = "%s/packaged/etc/raspigpioctrl/pin1.cfg" % PREFIX
        pin1 = GpioPin(self.opt, test1_file)
        gpio_sys = "./sys/class/gpio/"
        if os.path.exists("./sys"):
            print os.system("rm -rf ./sys")
            pin1.deb("'%s' removed")
            self.assertFalse(os.path.exists(gpio_sys), "")
        pin1.init_pin()
        pin1.flip()
        filed = open("%s/gpio1/value" % gpio_sys, "r")
        cont = filed.read().strip()
        filed.close()
        self.assertTrue(cont == "1", cont)
        pin1.flip()
        filed = open("%s/gpio1/value" % gpio_sys, "r")
        cont = filed.read().strip()
        filed.close()
        self.assertTrue(cont == "0", cont)

    def test4_0_datetime(self):
        """
        Pin >4_0> check datetime for 00:00 + 0min
        """
        now = datetime.datetime.now()
        exp_dt = datetime.datetime(year=now.year,
                        month=now.month,
                        day=now.day,
                        hour=0,
                        minute=0)
        self.assertTrue(exp_dt == self.pin0.get_dt_on())
        self.assertTrue(exp_dt == self.pin0.get_dt_off())

    def test4_1_datetime(self):
        """
        Pin >4_1> check datetime for runtime including midnight
        """
        pin = GpioPin(self.opt)
        pin.set_cfg({'start': '23:30', 'duration': '60'})
        now = datetime.datetime.now()
        exp_on = datetime.datetime(year=now.year,
                        month=now.month,
                        day=now.day,
                        hour=23,
                        minute=30)
        exp_off = datetime.datetime(year=now.year,
                        month=now.month,
                        day=now.day+1,
                        hour=0,
                        minute=30)
        self.assertTrue(exp_on == pin.get_dt_on())
        self.assertTrue(exp_off == pin.get_dt_off())

    def test5_0_change_mode(self):
        """
        Pin >5_0> Change mode to time, manual, sun
        """
        pin = GpioPin(self.opt)
        pin.change_mode("time")
        self.assertTrue(pin.mode == "1")
        pin.change_mode("manual")
        self.assertTrue(pin.mode == "2")
        pin.change_mode("sun")
        self.assertTrue(pin.mode == "3")

    def test5_1_change_false_mode(self):
        """
        Pin >5_0> Change mode to FooBar, expecting ValueError
        """
        pin = GpioPin(self.opt)
        self.assertRaises(ValueError, pin.change_mode, ("FooBar"))


    @unittest.skip("not implemented yet")
    def test99_0_save_cfg(self):
        """
        Pin >99_0> init
        """
        pass


if __name__ == '__main__':
    unittest.main()