import unittest
import argparse
from raspi.web import Web
import cherrypy

class TestRaspiWeb(unittest.TestCase):

    def setUp(self):
        self.opt = {
            "-r":"packaged",
            "--dry-run":True,
            '-d':1,
        }

    def test0_0_init(self):
        """
        Web >0_0> fire up web class
        """
        exp = ""
        web = Web(self.opt)
        

if __name__ == '__main__':
    unittest.main()