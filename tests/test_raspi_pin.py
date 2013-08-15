import unittest
import os
from ConfigParser import ConfigParser
from raspi import GpioPin, PIN_MODES

PREFIX = os.environ.get("WORKSPACE", ".")

class TestRaspiPin(unittest.TestCase):
    def setUp(self):
        self.pin0 = GpioPin()

    def teardown(self):
        print ("TestUM:teardown() after each test method")

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
        }
        for key, val in self.pin0.__dict__.items():
            amsg = "%s not in %s" % (key, ','.join(exp_items.keys()))
            self.assertTrue(key in exp_items.keys(), amsg)
            self.assertTrue(val == exp_items[key])
            del exp_items[key]
        amsg = "instance has items left: %s" % ','.join(exp_items)
        self.assertTrue(len(exp_items) == 0, amsg)

    def test0_1_init_cfg(self):
        """
        Pin >0_0> check items in initial __dict__ from test1.cfg
        """
        test1_file = "%s/misc/test1.cfg" % PREFIX
        pin1 = GpioPin(test1_file)
            
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
        }
        for key, val in pin1.__dict__.items():
            amsg = "%s not in %s" % (key, ','.join(exp_items.keys()))
            self.assertTrue(key in exp_items.keys(), amsg)
            self.assertTrue(val == exp_items[key],
                            "%s!=%s" % (val, exp_items[key]))
            del exp_items[key]
        amsg = "instance has items left: %s" % ','.join(exp_items)
        self.assertTrue(len(exp_items) == 0, amsg)

    def test0_2_md5(self):
        """
        Pin >0_2> check md5 of default test-file
        """
        crypt = self.pin0.get_md5("%s/misc/md5_check" % PREFIX)
        self.assertTrue("8c77efd73d331fb65bef594e2c854894" == crypt)

    def test1_0_get_json(self):
        """
        Pin >0_0> get initial json
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
        pin = GpioPin()
        pin.write_cfg(cfg_file)
        self.assertTrue(pin.crypt == '730f699d91ae6beb84bab4ae8362e55b',
                        "CRYPT: %s" % pin.crypt)
        #os.remove(cfg_file)

    @unittest.skip("not implemented yet")
    def test1_0_save_cfg(self):
        """
        Pin >1_0> init
        """
        pass


if __name__ == '__main__':
    unittest.main()