import unittest
import os
from pprint import pprint
from raspi.web import Web
from raspi.pin import GpioPin
import cherrypy

PREFIX = os.environ.get("WORKSPACE", "./")
if not PREFIX.endswith("/"):
    PREFIX += "/"

class TestRaspiWeb(unittest.TestCase):

    def setUp(self):
        self.opt = {
            "-r":"packaged",
            "--dry-run":True,
            "--no-read":True,
            '-d':1,
        }

    def test0_0_init(self):
        """
        Web >0_0> fire up web class
        """
        exp = ""
        
        test1_file = "%s/packaged/etc/raspigpioctrl/pin1.cfg" % PREFIX
        pin1 = GpioPin(self.opt, test1_file)
        pin1.init_pin(True)
        
        web = Web(self.opt)
        web.add_pin(pin1)
        web.index()
        exp = [
            '<html><head>',
            '<title>web.py</title></head><body><table border="1">',
            '<tr align="center">',
            '<td>GpioNr</td>',
            '<td>PinID</td>',
            '<td>Groups</td>',
            '<td>Prio</td>',
            '<td>Status</td>',
            '<td>Modus</td>',
            '<td>An um</td>',
            '<td>Wochentage</td>',
            '<td>Dauer</td>',
            '<td>Sonnenverzoegerung</td>',
            '</tr>',
            '<tr>',
            '<form method="POST">',
            '<td><b>1</b></td>',
            '<td><b>1</b></td>',
            '<td><b>garden</b></td>',
            "<input type='hidden' name='gpio' value='1'>",
            "<td style='background-color:red'>",
            "<input name='send' type='submit' value='flip'></td>",
            '<td>',
            "<input type='radio' name='mode' value='time' checked>time",
            "<input type='radio' name='mode' value='sun'>sun",
            "<input type='radio' name='mode' value='man'>man",
            "<td><select name='prio'>",
            "<option value='0'selected>0</option>",
            "<option value='1'>1</option>",
            "<option value='2'>2</option>",
            "<option value='3'>3</option>",
            "<option value='4'>4</option>",
            '</select></td>',
            '</td>',
            "<td><input type='text' name='start' value='01:00' size='6'>o'clock (24h)</td>",
            '<td>',
            "<input type='checkbox' name='dow_Mon' value='Mon'>Mon",
            "<input type='checkbox' name='dow_Tue' value='Tue'>Tue",
            "<input type='checkbox' name='dow_Wed' value='Wed' checked>Wed",
            "<input type='checkbox' name='dow_Thu' value='Thu'>Thu",
            "<input type='checkbox' name='dow_Fri' value='Fri'>Fri",
            "<input type='checkbox' name='dow_Sat' value='Sat'>Sat",
            "<input type='checkbox' name='dow_Sun' value='Sun' checked>Sun",
            '</td>',
            "<td><input type='text' name='duration' value='60' size='5'>min</td>",
            "<td><input type='text' name='sun_delay' value='0' size='5'>min</td>",
            "<td><input name='send' type='submit' value='change'></td>",
            '</form>',
            '</tr>',
            '</table>',
            '</body></html>',
            ]
        self.assertEqual(web.html, exp)

    def test0_1_init_flip(self):
        """
        Web >0_1> show green status
        """
        exp = ""
        
        test1_file = "%s/packaged/etc/raspigpioctrl/pin1.cfg" % PREFIX
        pin1 = GpioPin(self.opt, test1_file)
        pin1.init_pin(True)
        pin1.flip()
        
        web = Web(self.opt)
        web.add_pin(pin1)
        web.index()
        exp = [
            '<html><head>',
            '<title>web.py</title></head><body><table border="1">',
            '<tr align="center">',
            '<td>GpioNr</td>',
            '<td>PinID</td>',
            '<td>Groups</td>',
            '<td>Prio</td>',
            '<td>Status</td>',
            '<td>Modus</td>',
            '<td>An um</td>',
            '<td>Wochentage</td>',
            '<td>Dauer</td>',
            '<td>Sonnenverzoegerung</td>',
            '</tr>',
            '<tr>',
            '<form method="POST">',
            '<td><b>1</b></td>',
            '<td><b>1</b></td>',
            '<td><b>garden</b></td>',
            "<input type='hidden' name='gpio' value='1'>",
            "<td style='background-color:green'>",
            "<input name='send' type='submit' value='flip'></td>",
            '<td>',
            "<input type='radio' name='mode' value='time' checked>time",
            "<input type='radio' name='mode' value='sun'>sun",
            "<input type='radio' name='mode' value='man'>man",
            "<td><select name='prio'>",
            "<option value='0'selected>0</option>",
            "<option value='1'>1</option>",
            "<option value='2'>2</option>",
            "<option value='3'>3</option>",
            "<option value='4'>4</option>",
            '</select></td>',
            '</td>',
            "<td><input type='text' name='start' value='01:00' size='6'>o'clock (24h)</td>",
            '<td>',
            "<input type='checkbox' name='dow_Mon' value='Mon'>Mon",
            "<input type='checkbox' name='dow_Tue' value='Tue'>Tue",
            "<input type='checkbox' name='dow_Wed' value='Wed' checked>Wed",
            "<input type='checkbox' name='dow_Thu' value='Thu'>Thu",
            "<input type='checkbox' name='dow_Fri' value='Fri'>Fri",
            "<input type='checkbox' name='dow_Sat' value='Sat'>Sat",
            "<input type='checkbox' name='dow_Sun' value='Sun' checked>Sun",
            '</td>',
            "<td><input type='text' name='duration' value='60' size='5'>min</td>",
            "<td><input type='text' name='sun_delay' value='0' size='5'>min</td>",
            "<td><input name='send' type='submit' value='change'></td>",
            '</form>',
            '</tr>',
            '</table>',
            '</body></html>',
            ]
        self.assertEqual(web.html, exp)

    def test0_2_dow(self):
        """
        Web >0_2> all dow checked
        """
        exp = ""
        
        test1_file = "%s/packaged/etc/raspigpioctrl/pin1.cfg" % PREFIX
        pin1 = GpioPin(self.opt, test1_file)
        pin1.init_pin(True)
        pin1.set_cfg({'dow':'Mon,Tue,Wed,Thu,Fri,Sat,Sun'})
        
        web = Web(self.opt)
        web.add_pin(pin1)
        web.index()
        exp = [
            '<html><head>',
            '<title>web.py</title></head><body><table border="1">',
            '<tr align="center">',
            '<td>GpioNr</td>',
            '<td>PinID</td>',
            '<td>Groups</td>',
            '<td>Prio</td>',
            '<td>Status</td>',
            '<td>Modus</td>',
            '<td>An um</td>',
            '<td>Wochentage</td>',
            '<td>Dauer</td>',
            '<td>Sonnenverzoegerung</td>',
            '</tr>',
            '<tr>',
            '<form method="POST">',
            '<td><b>1</b></td>',
            '<td><b>1</b></td>',
            '<td><b>garden</b></td>',
            "<input type='hidden' name='gpio' value='1'>",
            "<td style='background-color:red'>",
            "<input name='send' type='submit' value='flip'></td>",
            '<td>',
            "<input type='radio' name='mode' value='time' checked>time",
            "<input type='radio' name='mode' value='sun'>sun",
            "<input type='radio' name='mode' value='man'>man",
            "<td><select name='prio'>",
            "<option value='0'selected>0</option>",
            "<option value='1'>1</option>",
            "<option value='2'>2</option>",
            "<option value='3'>3</option>",
            "<option value='4'>4</option>",
            '</select></td>',
            '</td>',
            "<td><input type='text' name='start' value='01:00' size='6'>o'clock (24h)</td>",
            '<td>',
            "<input type='checkbox' name='dow_Mon' value='Mon' checked>Mon",
            "<input type='checkbox' name='dow_Tue' value='Tue' checked>Tue",
            "<input type='checkbox' name='dow_Wed' value='Wed' checked>Wed",
            "<input type='checkbox' name='dow_Thu' value='Thu' checked>Thu",
            "<input type='checkbox' name='dow_Fri' value='Fri' checked>Fri",
            "<input type='checkbox' name='dow_Sat' value='Sat' checked>Sat",
            "<input type='checkbox' name='dow_Sun' value='Sun' checked>Sun",
            '</td>',
            "<td><input type='text' name='duration' value='60' size='5'>min</td>",
            "<td><input type='text' name='sun_delay' value='0' size='5'>min</td>",
            "<td><input name='send' type='submit' value='change'></td>",
            '</form>',
            '</tr>',
            '</table>',
            '</body></html>',
            ]
        self.assertEqual(web.html, exp)

    def test0_3_flip(self):
        """
        Web >0_3> press flip button
        """
        exp = ""
        
        test1_file = "%s/packaged/etc/raspigpioctrl/pin1.cfg" % PREFIX
        pin1 = GpioPin(self.opt, test1_file)
        pin1.init_pin(True)
        pin1.set_cfg({'dow':'Mon,Tue,Wed,Thu,Fri,Sat,Sun'})
        
        web = Web(self.opt)
        web.add_pin(pin1)
        web.index(send='flip', gpio='1')
        exp = [
            '<html><head>',
            '<title>web.py</title></head><body><table border="1">',
            '<tr align="center">',
            '<td>GpioNr</td>',
            '<td>PinID</td>',
            '<td>Groups</td>',
            '<td>Prio</td>',
            '<td>Status</td>',
            '<td>Modus</td>',
            '<td>An um</td>',
            '<td>Wochentage</td>',
            '<td>Dauer</td>',
            '<td>Sonnenverzoegerung</td>',
            '</tr>',
            '<tr>',
            '<form method="POST">',
            '<td><b>1</b></td>',
            '<td><b>1</b></td>',
            '<td><b>garden</b></td>',
            "<input type='hidden' name='gpio' value='1'>",
            "<td style='background-color:green'>",
            "<input name='send' type='submit' value='flip'></td>",
            '<td>',
            "<input type='radio' name='mode' value='time' checked>time",
            "<input type='radio' name='mode' value='sun'>sun",
            "<input type='radio' name='mode' value='man'>man",
            "<td><select name='prio'>",
            "<option value='0'selected>0</option>",
            "<option value='1'>1</option>",
            "<option value='2'>2</option>",
            "<option value='3'>3</option>",
            "<option value='4'>4</option>",
            '</select></td>',
            '</td>',
            "<td><input type='text' name='start' value='01:00' size='6'>o'clock (24h)</td>",
            '<td>',
            "<input type='checkbox' name='dow_Mon' value='Mon' checked>Mon",
            "<input type='checkbox' name='dow_Tue' value='Tue' checked>Tue",
            "<input type='checkbox' name='dow_Wed' value='Wed' checked>Wed",
            "<input type='checkbox' name='dow_Thu' value='Thu' checked>Thu",
            "<input type='checkbox' name='dow_Fri' value='Fri' checked>Fri",
            "<input type='checkbox' name='dow_Sat' value='Sat' checked>Sat",
            "<input type='checkbox' name='dow_Sun' value='Sun' checked>Sun",
            '</td>',
            "<td><input type='text' name='duration' value='60' size='5'>min</td>",
            "<td><input type='text' name='sun_delay' value='0' size='5'>min</td>",
            "<td><input name='send' type='submit' value='change'></td>",
            '</form>',
            '</tr>',
            '</table>',
            '</body></html>',
            ]
        self.assertEqual(web.html, exp)

    def test0_4_sun(self):
        """
        Web >0_4> change mod to sun
        """
        exp = ""
        
        test1_file = "%s/packaged/etc/raspigpioctrl/pin1.cfg" % PREFIX
        pin1 = GpioPin(self.opt, test1_file)
        pin1.init_pin(True)
        pin1.set_cfg({'dow':'Mon,Tue,Wed,Thu,Fri,Sat,Sun'})
        
        web = Web(self.opt)
        web.add_pin(pin1)
        web.index(send='change', mode='sun', gpio='1')
        self.assertTrue(web.gctrl.gpio_pins['1'].get_json()['mode'] == 'sun')



if __name__ == '__main__':
    unittest.main()