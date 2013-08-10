import unittest
from raspi import Web, Parameter, GpioCtrl

class TestRaspiGpio(unittest.TestCase):

    def setUp(self):
        options = Parameter([''])
        self.web = Web(options)

    def teardown(self):
        print ("TestUM:teardown() after each test method")

    @unittest.skip("not implemented yet")
    def test_init(self):
        """
        test 
        """
        pass


if __name__ == '__main__':
    unittest.main()