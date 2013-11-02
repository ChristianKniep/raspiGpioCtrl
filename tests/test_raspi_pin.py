import unittest
import os
import datetime
from ConfigParser import ConfigParser
from raspi.pin import SlavePin, MainPin, PIN_MODES, get_mode_id
from pprint import pprint

PREFIX = os.environ.get("WORKSPACE", "./")
if not PREFIX.endswith("/"):
    PREFIX += "/"

class TestRaspiPin(unittest.TestCase):
    def setUp(self):
        self.opt = {
            "-r":"packaged",
            "--dry-run":True,
            '-d':1,
        }
        self.pin0 = SlavePin(self.opt)
        self.skip_keys = ['opt']

    def check_dict(self, pin, exp_items):
        """
        check __dict__ for expected items
        """
        exp = exp_items.copy()
        for key, val in pin.__dict__.items():
            if key in self.skip_keys:
                continue
            amsg = "%s not in %s" % (key, '/'.join(exp.keys()))
            self.assertTrue(key in exp.keys(), amsg)
            amsg = "\nEXP '%s' (%s) \n%s\n" % (key, type(exp[key]),
                                             exp[key])
            amsg += "GOT '%s' (%s) \n%s\n" % (key, type(val), val)
            self.assertTrue(val == exp[key], amsg)
            del exp[key]
        amsg = "instance has items left: %s" % ','.join(exp)
        self.assertTrue(len(exp) == 0, amsg)

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
            'mode': 'off',
            'groups': '',
            'start': '00:00',
            'duration': '0',
            'sun_delay': '0',
            'state': '0',
            'dow': 'Mon,Tue,Wed,Thu,Fr,Sat,Sun',
            'gpio_base': "%spackaged/sys/class/gpio" % PREFIX,
            'pin_base': "%spackaged/sys/class/gpio/gpio0" % PREFIX,
        }
        self.check_dict(self.pin0, exp_items)

    def test0_1_init_cfg(self):
        """
        Pin >0_1> check items in initial __dict__ from test1.cfg
        """
        test1_file = "%s/packaged/etc/raspigpioctrl/pin1.cfg" % PREFIX
        pin1 = SlavePin(self.opt, test1_file)
        pin1.init_pin(True)
            
        exp_items = {
            'crypt': '8c34222d580d60b98fe73a05eeca0d3d',
            'pin_nr': '1',
            'cfg_file': test1_file,
            'name': 'Front',
            'prio': '0',
            'mode': 'time',
            'groups': 'garden',
            'start': '01:00',
            'duration': '60',
            'sun_delay': '0',
            'state': '0',
            'dow': 'Wed,Sun',
            'gpio_base': "%spackaged/sys/class/gpio" % PREFIX,
            'pin_base': "%spackaged/sys/class/gpio/gpio1" % PREFIX,
        }
        self.check_dict(pin1, exp_items)

    def test0_3_init(self):
        """
        Pin >0_3> change cfg of init_pin
        """
        pin = SlavePin(self.opt)
        exp_items = {
            'crypt': None,
            'pin_nr': '0',
            'cfg_file': None,
            'name': 'None',
            'prio': '0',
            'mode': 'off',
            'groups': '',
            'start': '00:00',
            'duration': '0',
            'sun_delay': '0',
            'state': '0',
            'dow': 'Mon,Tue,Wed,Thu,Fr,Sat,Sun',
            'gpio_base': "%spackaged/sys/class/gpio" % PREFIX,
            'pin_base': "%spackaged/sys/class/gpio/gpio0" % PREFIX,
        }
        exp1 = exp_items.copy()
        self.check_dict(pin, exp1)
        cfg = {
            'pin_nr': '1',
            'name': 'Front',
        }
        pin.set_cfg(cfg)
        pin.change_mode('time')
        exp_items['name'] = 'Front'
        exp_items['mode'] = 'time'
        pin_base = "%spackaged/sys/class/gpio/gpio1" % PREFIX
        exp_items['pin_base'] = pin_base
        exp_items['pin_nr'] = '1'
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
                'pin_nr': '0',
                'groups': '',
                'name': 'None',
                'mode': 'off',
                'prio': '0',
                'start': "00:00",
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
        pin = SlavePin(self.opt)
        pin.write_cfg(cfg_file)
        self.assertTrue(pin.crypt == '9ec78ec1ae354d5cd568a90ab2f1493a',
                        "CRYPT: %s" % pin.crypt)
        os.remove(cfg_file)

    def test2_1_save_cfg(self):
        """
        Pin >2_1> Write real pin1 cfg
        """
        test1_cfg = "%s/packaged/etc/raspigpioctrl/pin1.cfg" % PREFIX
        pin = SlavePin(self.opt, test1_cfg)
        pin.start = "10:00"
        pin.duration = "30"
        pin.dow = "Fri,Sat,Sun"
        cfg_file = '%s/misc/tmp_test.cfg' % PREFIX
        if os.path.exists(cfg_file):
            os.remove(cfg_file)
        pin.write_cfg(cfg_file)
        self.assertTrue(pin.crypt == '80a913b6297d386cd72b9f9fd9172c34',
                        "CRYPT: %s" % pin.crypt)
        os.remove(cfg_file)

    def test2_2_failed_save_cfg(self):
        """
        Pin >2_2> Write cfg with changed cfg-file in background (IOError)
        """
        test1_cfg = "%s/packaged/etc/raspigpioctrl/pin1.cfg" % PREFIX
        pin = SlavePin(self.opt, test1_cfg)
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
        self.assertTrue(pin.crypt == '80a913b6297d386cd72b9f9fd9172c34',
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
        pin1 = SlavePin(self.opt, test1_file)
        gpio_sys = "%s/packaged/sys/class/gpio/" % PREFIX
        if os.path.exists("%s/packaged/sys" % PREFIX):
            print os.system("rm -rf %s/packaged/sys" % PREFIX)
            pin1.deb("'%s' removed")
            self.assertFalse(os.path.exists(gpio_sys), "")
        pin1.init_pin()
        filed = open("%s/gpio1/value" % gpio_sys, "r")
        cont = filed.read().strip()
        self.assertTrue(cont == "0", cont)

    def test3_0_1_pin(self):
        """
        Pin >3_0_1> init main pin
        """
        test_file = "%s/packaged/etc/raspigpioctrl/main5.cfg" % PREFIX
        pin = MainPin(self.opt, test_file)
        gpio_sys = "%s/packaged/sys/class/gpio/" % PREFIX
        if os.path.exists("%s/packaged/sys" % PREFIX):
            print os.system("rm -rf %s/packaged/sys" % PREFIX)
            pin.deb("'%s' removed")
            self.assertFalse(os.path.exists(gpio_sys), "")
        pin.init_pin()
        filed = open("%s/gpio5/value" % gpio_sys, "r")
        cont = filed.read().strip()
        self.assertTrue(cont == "0", cont)
        pin.flip()
        filed = open("%s/gpio5/value" % gpio_sys, "r")
        cont = filed.read().strip()
        self.assertTrue(cont == "1", cont)
        pin.flip()
        filed = open("%s/gpio5/value" % gpio_sys, "r")
        cont = filed.read().strip()
        self.assertTrue(cont == "0", cont)
        pin.change_mode('auto')
        pin.flip()
        filed = open("%s/gpio5/value" % gpio_sys, "r")
        cont = filed.read().strip()
        self.assertTrue(cont == "1", cont)
        pprint(pin.get_json())
        self.assertTrue(pin.ismode('off'))

    def test3_1_pin(self):
        """
        Pin >3_1> read_real_life()
        """
        test1_file = "%s/packaged/etc/raspigpioctrl/pin1.cfg" % PREFIX
        pin1 = SlavePin(self.opt, test1_file)
        self.assertTrue("0" == pin1.read_real_life())
        pin1.flip()
        self.assertTrue("1" == pin1.read_real_life())

    def test3_2_pin(self):
        """
        Pin >3_2> init dry-run pin and set_pin(1) / set_pin(0)
        """
        test1_file = "%s/packaged/etc/raspigpioctrl/pin1.cfg" % PREFIX
        pin1 = SlavePin(self.opt, test1_file)
        gpio_sys = "%s/packaged/sys/class/gpio/" % PREFIX
        if os.path.exists("%s/packaged/sys" % PREFIX):
            print os.system("rm -rf %s/packaged/sys" % PREFIX)
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
        pin1 = SlavePin(self.opt, test1_file)
        gpio_sys = "%s/packaged/sys/class/gpio/" % PREFIX
        if os.path.exists("%s/packaged/sys" % PREFIX):
            print os.system("rm -rf %s/packaged/sys" % PREFIX)
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

    def test3_4_flip(self):
        """
        Pin >3_4> init dry-run pin and flip twice with main-pin
        """
        test1_file = "%s/packaged/etc/raspigpioctrl/pin1.cfg" % PREFIX
        pin1 = SlavePin(self.opt, test1_file)
        test5_file = "%s/packaged/etc/raspigpioctrl/main5.cfg" % PREFIX
        pin5 = MainPin(self.opt, test5_file)
        gpio_sys = "%s/packaged/sys/class/gpio/" % PREFIX
        if os.path.exists("%s/packaged/sys" % PREFIX):
            print os.system("rm -rf %s/packaged/sys" % PREFIX)
            pin1.deb("'%s' removed")
            self.assertFalse(os.path.exists(gpio_sys), "")
        pin1.init_pin()
        pin5.init_pin()
        pin1.set_pin(0)
        pin5.set_pin(0)
        pin5.change_mode('auto')
        pin1.flip()
        filed = open("%s/gpio1/value" % gpio_sys, "r")
        cont = filed.read().strip()
        filed.close()
        self.assertTrue(cont == "1", cont)

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
        pin = SlavePin(self.opt)
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
        pin = SlavePin(self.opt)
        pin.change_mode("time")
        self.assertTrue(pin.mode == "time")
        pin.change_mode("man")
        self.assertTrue(pin.mode == "man")
        pin.change_mode("sun")
        with self.assertRaises(ValueError):
            pin.change_mode("buh")
        self.assertTrue(pin.mode == "sun")
        self.assertTrue(get_mode_id("buh") is None)

    def test5_1_change_false_mode(self):
        """
        Pin >5_0> Change mode to FooBar, expecting ValueError
        """
        pin = SlavePin(self.opt)
        self.assertRaises(ValueError, pin.change_mode, ("FooBar"))

    def test6_0_get_id(self):
        """
        Pin >6_0> Get identifier for sorting pin-list in GpioCtrl
        """
        test1_file = "%s/packaged/etc/raspigpioctrl/pin1.cfg" % PREFIX
        pin1 = SlavePin(self.opt, test1_file)
        self.assertTrue(pin1.get_id() == "1")

    def test7_0_eq(self):
        """
        Pin >7_0> self.__eq__(other) True
        """
        lst = []
        pin0 = SlavePin(self.opt)
        pin0.set_cfg({
            'groups':'garden',
            'pin_nr': '4',
            'start': '00:10',
            'prio': '0',
            'duration': '10',
        })
        pin1 = SlavePin(self.opt)
        pin1.set_cfg({
            'groups':'garden',
            'pin_nr': '3',
            'start': '00:10',
            'prio': '0',
            'duration': '10',
        })
        pin2 = SlavePin(self.opt)
        pin2.set_cfg({
            'groups':'garden',
            'pin_nr': '3',
            'start': '00:20',
            'prio': '0',
            'duration': '10',
        })
        amsg = "\n%s\n!=\n%s" % (pin0.get_json(), pin1.get_json())
        self.assertTrue(pin0.__eq__(pin1), amsg)
        amsg = "\n%s\n==\n%s" % (pin0.get_json(), pin2.get_json())
        self.assertFalse(pin0.__eq__(pin2))

    def test7_1_ne(self):
        """
        Pin >7_1> self.__ne__(other) True
        """
        lst = []
        pin0 = SlavePin(self.opt)
        pin0.set_cfg({
            'groups':'garden',
            'pin_nr': '4',
            'start': '00:10',
            'prio': '0',
            'duration': '10',
        })
        pin1 = SlavePin(self.opt)
        pin1.set_cfg({
            'groups':'garden',
            'pin_nr': '3',
            'start': '00:10',
            'prio': '0',
            'duration': '10',
        })
        pin2 = SlavePin(self.opt)
        pin2.set_cfg({
            'groups':'garden',
            'pin_nr': '3',
            'start': '00:20',
            'prio': '0',
            'duration': '10',
        })
        amsg = "\n%s\n!=\n%s" % (pin0.get_json(), pin1.get_json())
        self.assertFalse(pin0.__ne__(pin1), amsg)
        amsg = "\n%s\n==\n%s" % (pin0.get_json(), pin2.get_json())
        self.assertTrue(pin0.__ne__(pin2))

    def test7_2_lt(self):
        """
        Pin >7_2> self.__lt__(other)
        """
        lst = []
        pin0 = SlavePin(self.opt)
        pin0.set_cfg({
            'groups':'garden',
            'pin_nr': '4',
            'start': '00:00',
            'prio': '0',
            'duration': '10',
        })
        pin1 = SlavePin(self.opt)
        pin1.set_cfg({
            'pin_nr': '3',
            'start': '00:10',
            'prio': '0',
            'duration': '10',
        })
        pin2 = SlavePin(self.opt)
        pin2.set_cfg({
            'groups':'garden',
            'pin_nr': '3',
            'start': '00:00',
            'prio': '1',
            'duration': '10',
        })
        pin3 = SlavePin(self.opt)
        pin3.set_cfg({
            'groups':'garden',
            'pin_nr': '3',
            'start': '00:00',
            'prio': '0',
            'duration': '20',
        })
        amsg = "\n%s\n<\n%s" % (pin0.get_json(), pin1.get_json())
        self.assertTrue(pin0.__lt__(pin1), amsg)
        amsg = "\n%s\n<\n%s" % (pin0.get_json(), pin2.get_json())
        self.assertTrue(pin0.__lt__(pin2), amsg)
        amsg = "\n%s\n<\n%s" % (pin0.get_json(), pin3.get_json())
        self.assertTrue(pin0.__lt__(pin3), amsg)
        amsg = "\n%s\n>\n%s" % (pin0.get_json(), pin1.get_json())
        self.assertFalse(pin1.__lt__(pin0), amsg)
        amsg = "\n%s\n>\n%s" % (pin0.get_json(), pin2.get_json())
        self.assertFalse(pin2.__lt__(pin0), amsg)
        amsg = "\n%s\n<\n%s" % (pin0.get_json(), pin3.get_json())
        self.assertFalse(pin3.__lt__(pin0), amsg)

    def test7_3_le(self):
        """
        Pin >7_3> self.__le__(other)
        """
        lst = []
        pin0 = SlavePin(self.opt)
        pin0.set_cfg({
            'groups':'garden',
            'pin_nr': '4',
            'start': '00:00',
            'prio': '0',
            'duration': '10',
        })
        pin1 = SlavePin(self.opt)
        pin1.set_cfg({
            'groups':'garden',
            'pin_nr': '3',
            'start': '00:10',
            'prio': '0',
            'duration': '10',
        })
        pin2 = SlavePin(self.opt)
        pin2.set_cfg({
            'groups':'garden',
            'pin_nr': '3',
            'start': '00:00',
            'prio': '1',
            'duration': '10',
        })
        pin3 = SlavePin(self.opt)
        pin3.set_cfg({
            'groups':'garden',
            'pin_nr': '3',
            'start': '00:00',
            'prio': '0',
            'duration': '20',
        })
        pin4 = SlavePin(self.opt)
        pin4.set_cfg({
            'groups':'garden',
            'pin_nr': '4',
            'start': '00:00',
            'prio': '0',
            'duration': '30',
        })
        amsg = "\n%s\n<=\n%s" % (pin0.get_json(), pin1.get_json())
        self.assertTrue(pin0.__le__(pin1), amsg)
        amsg = "\n%s\n<=\n%s" % (pin0.get_json(), pin2.get_json())
        self.assertTrue(pin0.__le__(pin2), amsg)
        amsg = "\n%s\n<=\n%s" % (pin0.get_json(), pin3.get_json())
        self.assertTrue(pin0.__le__(pin3), amsg)
        amsg = "\n%s\n<=\n%s" % (pin0.get_json(), pin1.get_json())
        self.assertTrue(pin1.__le__(pin1), amsg)
        amsg = "\n%s\n<=\n%s" % (pin0.get_json(), pin2.get_json())
        self.assertTrue(pin2.__le__(pin2), amsg)
        amsg = "\n%s\n<=\n%s" % (pin0.get_json(), pin3.get_json())
        self.assertTrue(pin3.__le__(pin3), amsg)
        amsg = "\n%s\n>=\n%s" % (pin0.get_json(), pin1.get_json())
        self.assertFalse(pin1.__le__(pin0), amsg)
        amsg = "\n%s\n>\n%s" % (pin0.get_json(), pin2.get_json())
        self.assertFalse(pin2.__le__(pin0), amsg)
        amsg = "\n%s\n>\n%s" % (pin0.get_json(), pin3.get_json())
        self.assertFalse(pin3.__le__(pin0), amsg)
        amsg = "\n%s\n !__le__ \n%s" % (pin4.get_json(), pin3.get_json())
        self.assertFalse(pin4.__le__(pin3), amsg)

    def test7_4_gt(self):
        """
        Pin >7_4> self.__gt__(other)
        """
        lst = []
        pin0 = SlavePin(self.opt)
        pin0.set_cfg({
            'groups':'garden',
            'pin_nr': '4',
            'start': '00:00',
            'prio': '0',
            'duration': '10',
        })
        pin1 = SlavePin(self.opt)
        pin1.set_cfg({
            'groups':'garden',
            'pin_nr': '3',
            'start': '00:10',
            'prio': '0',
            'duration': '10',
        })
        pin2 = SlavePin(self.opt)
        pin2.set_cfg({
            'groups':'garden',
            'pin_nr': '3',
            'start': '00:00',
            'prio': '1',
            'duration': '10',
        })
        pin3 = SlavePin(self.opt)
        pin3.set_cfg({
            'groups':'garden',
            'pin_nr': '3',
            'start': '00:00',
            'prio': '0',
            'duration': '20',
        })
        pin4 = SlavePin(self.opt)
        pin4.set_cfg({
            'groups':'garden',
            'pin_nr': '4',
            'start': '00:00',
            'prio': '1',
            'duration': '20',
        })
        amsg = "\n%s\n>\n%s" % (pin1.get_json(), pin0.get_json())
        self.assertTrue(pin1.__gt__(pin0), amsg)
        amsg = "\n%s\n>\n%s" % (pin2.get_json(), pin0.get_json())
        self.assertTrue(pin2.__gt__(pin0), amsg)
        amsg = "\n%s\n>\n%s" % (pin0.get_json(), pin0.get_json())
        self.assertTrue(pin3.__gt__(pin0), amsg)
        amsg = "\n%s\n<\n%s" % (pin0.get_json(), pin1.get_json())
        self.assertFalse(pin0.__gt__(pin1), amsg)
        amsg = "\n%s\n<\n%s" % (pin0.get_json(), pin0.get_json())
        self.assertFalse(pin0.__gt__(pin0), amsg)
        amsg = "\n%s\n<\n%s" % (pin0.get_json(), pin1.get_json())
        self.assertFalse(pin0.__gt__(pin1), amsg)
        amsg = "\n%s\n!__gt__\n%s" % (pin3.get_json(), pin4.get_json())
        self.assertFalse(pin3.__gt__(pin4), amsg)

    def test7_5_ge(self):
        """
        Pin >7_5> self.__ge__(other)
        """
        lst = []
        pin0 = SlavePin(self.opt)
        pin0.set_cfg({
            'groups':'garden',
            'pin_nr': '4',
            'start': '00:00',
            'prio': '0',
            'duration': '10',
        })
        pin1 = SlavePin(self.opt)
        pin1.set_cfg({
            'groups':'garden',
            'pin_nr': '3',
            'start': '00:10',
            'prio': '0',
            'duration': '10',
        })
        pin2 = SlavePin(self.opt)
        pin2.set_cfg({
            'groups':'garden',
            'pin_nr': '3',
            'start': '00:00',
            'prio': '1',
            'duration': '10',
        })
        pin3 = SlavePin(self.opt)
        pin3.set_cfg({
            'groups':'garden',
            'pin_nr': '3',
            'start': '00:00',
            'prio': '0',
            'duration': '20',
        })
        pin4 = SlavePin(self.opt)
        pin4.set_cfg({
            'groups':'garden',
            'pin_nr': '4',
            'start': '00:00',
            'prio': '0',
            'duration': '10',
        })
        amsg = "\n%s\n>\n%s" % (pin1.get_json(), pin0.get_json())
        self.assertTrue(pin1.__ge__(pin0), amsg)
        amsg = "\n%s\n>\n%s" % (pin2.get_json(), pin0.get_json())
        self.assertTrue(pin2.__ge__(pin0), amsg)
        amsg = "\n%s\n>\n%s" % (pin0.get_json(), pin0.get_json())
        self.assertTrue(pin3.__ge__(pin0), amsg)
        amsg = "\n%s\n<\n%s" % (pin0.get_json(), pin1.get_json())
        self.assertFalse(pin0.__ge__(pin1), amsg)
        amsg = "\n%s\n<\n%s" % (pin0.get_json(), pin0.get_json())
        self.assertTrue(pin0.__ge__(pin0), amsg)
        amsg = "\n%s\n<\n%s" % (pin0.get_json(), pin1.get_json())
        self.assertFalse(pin0.__ge__(pin1), amsg)
        amsg = "\n%s\n__ge__\n%s" % (pin3.get_json(), pin4.get_json())
        self.assertTrue(pin3.__ge__(pin4), amsg)
        amsg = "\n%s\n!__ge__\n%s" % (pin3.get_json(), pin2.get_json())
        self.assertFalse(pin3.__ge__(pin2), amsg)
        amsg = "\n%s\n!__ge__\n%s" % (pin4.get_json(), pin3.get_json())
        self.assertFalse(pin4.__ge__(pin3), amsg)

    def test8_0_trigger(self):
        """
        Pin >8_0> trigger off
        """
        pin = SlavePin(self.opt)
        now = datetime.datetime.now()
        delay = datetime.timedelta(seconds=600)
        temp_on = now - delay
        cfg = {
            'start': temp_on.strftime("%H:%M"),
            'duration': '5',
            'pin_nr': '1',
        }
        pin.set_cfg(cfg)
        pin.change_mode('time')
        pin.init_pin()
        pin.set_pin(1)
        self.assertTrue("1" == pin.read_real_life())
        pin.trigger_off()
        self.assertTrue("0" == pin.read_real_life())
        pin.trigger_off()
        self.assertTrue("0" == pin.read_real_life())
        pin.set_pin(1)
        self.assertTrue("1" == pin.read_real_life())
        pin.trigger_off()
        self.assertTrue("0" == pin.read_real_life())

    def test8_1_trigger(self):
        """
        Pin >8_1> trigger on
        """
        pin = SlavePin(self.opt)
        now = datetime.datetime.now()
        delay = datetime.timedelta(seconds=60)
        temp_on = now + delay
        cfg = {
            'start': now.strftime("%H:%M"),
            'duration': '5',
            'pin_nr': '1',
        }
        pin.set_cfg(cfg)
        pin.change_mode('time')
        pin.init_pin()
        pin.trigger_on()
        self.assertTrue("1" == pin.read_real_life())
        pin.set_pin(0)
        self.assertTrue("0" == pin.read_real_life())
        pin.trigger_on()
        self.assertTrue("1" == pin.read_real_life())


if __name__ == '__main__':
    unittest.main()