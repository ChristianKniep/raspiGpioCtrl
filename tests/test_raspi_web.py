import unittest
import os
from pprint import pprint
from raspi.web import Web
from raspi.pin import SlavePin, MainPin
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
        self.exp = [
            '<html><head>',
            '<title>web.py</title></head><body><table border="1">',
            '<tr align="center">',
            '<td>PinID</td>',
            '<td>Name</td>',
            '<td>Groups</td>',
            '<td>Status</td>',
            '<td>Modus</td>',
            '<td>Prio</td>',
            '<td>An um</td>',
            '<td>Wochentage</td>',
            '<td>Dauer</td>',
            '<td>Sonnenverzoegerung</td>',
            '</tr>',
            '<tr>',
            '<form method="POST">',
            '<td><b>1</b></td>',
            '<td><b>Front</b></td>',
            "<td><input type='text' name='groups' value='garden' size='10'></td>",
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
            "<td><input type='text' name='start' value='00:00' size='5'>(24h)</td>",
            '<td>',
            "<input type='checkbox' name='dow_Mon' value='Mon' checked>Mon",
            "<input type='checkbox' name='dow_Tue' value='Tue' checked>Tue",
            "<input type='checkbox' name='dow_Wed' value='Wed' checked>Wed",
            "<input type='checkbox' name='dow_Thu' value='Thu' checked>Thu",
            "<input type='checkbox' name='dow_Fri' value='Fri'>Fri",
            "<input type='checkbox' name='dow_Sat' value='Sat' checked>Sat",
            "<input type='checkbox' name='dow_Sun' value='Sun' checked>Sun",
            '</td>',
            "<td><input type='text' name='duration' value='0' size='5'>min</td>",
            "<td><input type='text' name='sun_delay' value='0' size='5'>min</td>",
            "<td><input name='send' type='submit' value='change'></td>",
            '</form>',
            '</tr>',
            '</table>',
            '</body></html>'
        ]

    def check_web(self, got, exp):
        """
        checks web output line by line
        """
        if len(got) != len(exp):
            print "###################"
            print "## len-mismatch: GOT:%s/EXP:%s" % (len(got), len(exp))
            print "####### exp"
            #pprint(exp)
            print "####### got"
            #pprint(got)
            self.assertTrue(False)
        for cnt in range(0, len(got)):
            res = got[cnt] == exp[cnt]
            amsg = "%-3s: %s GOT!=EXP %s" % (cnt, got[cnt], exp[cnt])
            self.assertTrue(res, amsg)

    def test0_0_init(self):
        """
        Web >0_0> fire up web class
        """
        exp = ""
        
        test1_file = "%s/packaged/etc/raspigpioctrl/pin1.cfg" % PREFIX
        pin1 = SlavePin(self.opt, test1_file)
        pin1.init_pin(True)
        
        web = Web(self.opt)
        web.add_pin(pin1)
        web.index()
        exp = [line for line in self.exp]
        exp[20] = "<td style='background-color:red'>"
        self.check_web(web.html, exp)

    def test0_1_init_flip(self):
        """
        Web >0_1> show green status
        """

        test1_file = "%s/packaged/etc/raspigpioctrl/pin1.cfg" % PREFIX
        pin1 = SlavePin(self.opt, test1_file)
        pin1.init_pin(True)
        pin1.flip()
        
        web = Web(self.opt)
        web.add_pin(pin1)
        web.index()
        exp = [line for line in self.exp]
        exp[20] = "<td style='background-color:green'>"
        self.assertEqual(web.html, exp)

    def test0_2_dow(self):
        """
        Web >0_2> all dow checked
        """
        test1_file = "%s/packaged/etc/raspigpioctrl/pin1.cfg" % PREFIX
        pin1 = SlavePin(self.opt, test1_file)
        pin1.init_pin(True)
        pin1.set_cfg({'dow':'Mon,Tue,Wed,Thu,Fri,Sat,Sun'})
        
        web = Web(self.opt)
        web.add_pin(pin1)
        web.index()
        exp = [
            '<html><head>',
            '<title>web.py</title></head><body><table border="1">',
            '<tr align="center">',
            '<td>PinID</td>',
            '<td>Name</td>',
            '<td>Groups</td>',
            '<td>Status</td>',
            '<td>Modus</td>',
            '<td>Prio</td>',
            '<td>An um</td>',
            '<td>Wochentage</td>',
            '<td>Dauer</td>',
            '<td>Sonnenverzoegerung</td>',
            '</tr>',
            '<tr>',
            '<form method="POST">',
            '<td><b>1</b></td>',
            '<td><b>Front</b></td>',
            "<td><input type='text' name='groups' value='garden' size='10'></td>",
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
            "<td><input type='text' name='start' value='00:00' size='5'>(24h)</td>",
            '<td>',
            "<input type='checkbox' name='dow_Mon' value='Mon' checked>Mon",
            "<input type='checkbox' name='dow_Tue' value='Tue' checked>Tue",
            "<input type='checkbox' name='dow_Wed' value='Wed' checked>Wed",
            "<input type='checkbox' name='dow_Thu' value='Thu' checked>Thu",
            "<input type='checkbox' name='dow_Fri' value='Fri' checked>Fri",
            "<input type='checkbox' name='dow_Sat' value='Sat' checked>Sat",
            "<input type='checkbox' name='dow_Sun' value='Sun' checked>Sun",
            '</td>',
            "<td><input type='text' name='duration' value='0' size='5'>min</td>",
            "<td><input type='text' name='sun_delay' value='0' size='5'>min</td>",
            "<td><input name='send' type='submit' value='change'></td>",
            '</form>',
            '</tr>',
            '</table>',
            '</body></html>'
        ]
        self.check_web(web.html, exp)

    def test0_3_flip(self):
        """
        Web >0_3> press flip button
        """
        test1_file = "%s/packaged/etc/raspigpioctrl/pin1.cfg" % PREFIX
        pin1 = SlavePin(self.opt, test1_file)
        pin1.init_pin(True)
        pin1.set_cfg({'dow':'Mon,Tue,Wed,Fri,Sat,Sun'})
        
        web = Web(self.opt)
        web.add_pin(pin1)
        web.index(send='flip', gpio='1')
        exp = [line for line in self.exp]
        exp[39] = "<input type='checkbox' name='dow_Thu' value='Thu'>Thu"
        exp[40] = "<input type='checkbox' name='dow_Fri' value='Fri' checked>Fri"
        self.check_web(web.html, exp)
        web.index(send='flip', gpio='1')
        exp[20] = "<td style='background-color:red'>"
        self.check_web(web.html, exp)

    def test0_4_sun(self):
        """
        Web >0_4> change mod to sun
        """
        exp = ""
        
        test1_file = "%s/packaged/etc/raspigpioctrl/pin1.cfg" % PREFIX
        pin1 = SlavePin(self.opt, test1_file)
        pin1.init_pin(True)
        pin1.set_cfg({'dow':'Mon,Tue,Wed,Thu,Fri,Sat,Sun'})
        
        web = Web(self.opt)
        web.add_pin(pin1)
        web.index(send='change', mode='sun', gpio='1')
        self.assertTrue(web.gctrl.gpio_pins['1'].get_json()['mode'] == 'sun')



if __name__ == '__main__':
    unittest.main()