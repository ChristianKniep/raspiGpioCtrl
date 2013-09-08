import unittest
import argparse
from raspi.web import Web
from raspi.ctrl import GpioCtrl

class TestRaspiGpio(unittest.TestCase):

    def setUp(self):
        self.opt = argparse.Namespace(debug=1, root=".", dry_run=True)
        self.web = Web(self.opt)

    def teardown(self):
        print ("TestUM:teardown() after each test method")


if __name__ == '__main__':
    unittest.main()