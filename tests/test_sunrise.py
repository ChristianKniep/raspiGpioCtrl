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

    def test0_init(self):
        """
        Is Suderburg default place to go?
        """
        sun = sunrise.SunRise()
        assert sun.coord == (52.8948846, 10.4468234)

    @unittest.skip("not implemented yet")
    def test_sunrise(self):
        """
        test sunrise (2013-08-10 -> 5:52AM)
        """
        pass

    @unittest.skip("not implemented yet")
    def test_sunset(self):
        """
        test sunset (2013-08-10 -> 8:54PM)
        """
        pass

    @unittest.skip("not implemented yet")
    def test_solarnoon(self):
        """
        test solarnoon
        """
        pass

    @unittest.skip("not implemented yet")
    def test_timefromdecimalday(self):
        """
        test 
        """
        pass

    @unittest.skip("not implemented yet")
    def test_preptime(self):
        """
        test 
        """
        pass

    @unittest.skip("not implemented yet")
    def test_calc(self):
        """
        test 
        """
        pass


if __name__ == '__main__':
    unittest.main()