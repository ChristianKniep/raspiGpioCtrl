import unittest
#from raspi_gpio import Parameter
import sunrise

class TestUM(unittest.TestCase):

    def setUp(self):
        print ("TestUM:setup() ")
        #options = Parameter([''])
        #self.srv = GpioCtrl(options)

    def teardown(self):
        print ("TestUM:teardown() after each test method")

    def test_strings_b_2(self):
        print 'test_strings_b_2()  <============================ actual test code'
        assert 'b'*2 == 'bb'

if __name__ == '__main__':
    unittest.main()