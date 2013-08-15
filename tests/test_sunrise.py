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
        SunRise >0_0> Is Suderburg default place to go?
        """
        sun = sunrise.SunRise()
        assert sun.coord == (52.8948846, 10.4468234)

    @unittest.skip("not implemented yet")
    def test_sunrise(self):
        """
        SunRise >0_0> test sunrise (2013-08-10 -> 5:52AM)
        """
        pass

    @unittest.skip("not implemented yet")
    def test_sunset(self):
        """
        SunRise >0_0> test sunset (2013-08-10 -> 8:54PM)
        """
        pass

    @unittest.skip("not implemented yet")
    def test_solarnoon(self):
        """
        SunRise >0_0> test solarnoon
        """
        pass

    @unittest.skip("not implemented yet")
    def test_timefromdecimalday(self):
        """
        SunRise >0_0> test 
        """
        pass

    @unittest.skip("not implemented yet")
    def test_preptime(self):
        """
        SunRise >0_0> test 
        """
        pass

    @unittest.skip("not implemented yet")
    def test_calc(self):
        """
        SunRise >0_0> test 
        """
        pass


if __name__ == '__main__':
    unittest.main()