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
            "--test":'None',
            '-d':1,
        }
        self.exp_head = [
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
            ]
        self.exp_pin1 = [
            '<tr>',
            '<form method="POST" action="update_slave">',
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
            "<td><input type='text' name='start' value='01:00' size='5'>(24h)</td>",
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
            ]
        self.exp_main5 = [
            "<tr>",
            '<form method="POST" action="update_main">',
            "<td><b>5</b></td>",
            "<td><b>Mainrelay</b></td>",
            "<td><input type='text' name='groups' value='garden' size='10'></td>",
            "<input type='hidden' name='gpio' value='5'>",
            "<td style='background-color:red'>",
            "<input name='send' type='submit' value='flip'></td>",
            "<td style='background-color:red'>",
            "<input name='send' type='submit' value='OFF'><input name='send' type='submit' value='AUTO'></td>",
            "<td></td>",
            "<td></td>",
            "<td></td>",
            "<td colspan='2'>Run <input type='text' value='2' name='test_dur' size='2'>min group test.<input name='send' type='submit' value='START TEST'></td>",
            "<td><input name='send' type='submit' value='change'></td>",
            "</form>",
            '</tr>'
        ]
        self.exp_tail = [
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
            #self.assertTrue(False)
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
        exp = [line for line in self.exp_head]
        exp.extend([line for line in self.exp_pin1])
        exp.extend([line for line in self.exp_tail])
        exp[20] = "<td style='background-color:red'>"
        got = web.html
        self.check_web(got, exp)

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
        exp = [line for line in self.exp_head]
        exp.extend([line for line in self.exp_pin1])
        exp.extend([line for line in self.exp_tail])
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
        exp = [line for line in self.exp_head]
        exp.extend([line for line in self.exp_pin1])
        exp.extend([line for line in self.exp_tail])
        exp[20] = "<td style='background-color:red'>"
        exp[36] = "<input type='checkbox' name='dow_Mon' value='Mon' checked>Mon"
        exp[37] = "<input type='checkbox' name='dow_Tue' value='Tue' checked>Tue"
        exp[39] = "<input type='checkbox' name='dow_Thu' value='Thu' checked>Thu"
        exp[40] = "<input type='checkbox' name='dow_Fri' value='Fri' checked>Fri"
        exp[41] = "<input type='checkbox' name='dow_Sat' value='Sat' checked>Sat"
        exp[42] = "<input type='checkbox' name='dow_Sun' value='Sun' checked>Sun"
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
        web.update_slave(send='flip', gpio='1')
        exp = [line for line in self.exp_head]
        exp.extend([line for line in self.exp_pin1])
        exp.extend([line for line in self.exp_tail])
        exp[36] = "<input type='checkbox' name='dow_Mon' value='Mon' checked>Mon"
        exp[37] = "<input type='checkbox' name='dow_Tue' value='Tue' checked>Tue"
        exp[39] = "<input type='checkbox' name='dow_Thu' value='Thu'>Thu"
        exp[40] = "<input type='checkbox' name='dow_Fri' value='Fri' checked>Fri"
        exp[41] = "<input type='checkbox' name='dow_Sat' value='Sat' checked>Sat"
        exp[42] = "<input type='checkbox' name='dow_Sun' value='Sun' checked>Sun"
        self.check_web(web.html, exp)
        web.update_slave(send='flip', gpio='1')
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
        web.update_slave(send='change', mode='sun', gpio='1')
        self.assertTrue(web.gctrl.gpio_pins['1'].get_json()['mode'] == 'sun')

    def test1_0_main(self):
        """
        Web >1_0> main pin plus pin1
        """
        pin1_file = "%s/packaged/etc/raspigpioctrl/pin1.cfg" % PREFIX
        pin1 = SlavePin(self.opt, pin1_file)
        pin1.init_pin(True)
        pin1.set_pin(0)
        pin1.set_cfg({'dow':'Mon,Tue,Wed,Thu,Fri,Sat,Sun'})
        self.assertTrue(pin1.isstate(0))
        pin5_file = "%s/packaged/etc/raspigpioctrl/main5.cfg" % PREFIX
        pin5 = MainPin(self.opt, pin5_file)
        pin5.init_pin(True)
        pin5.set_cfg({'groups':'garden'})
        pprint(pin5.get_json())
        pin5.change_mode('off')
        pin5.set_pin(0)
        self.assertTrue(pin5.isstate(0))

        web = Web(self.opt)
        web.add_pin(pin1)
        web.add_pin(pin5)
        web.index()
        exp = [line for line in self.exp_head]
        exp.extend([line for line in self.exp_pin1])
        exp.extend([line for line in self.exp_main5])
        exp.extend([line for line in self.exp_tail])
        exp[20] = "<td style='background-color:red'>"
        exp[36] = "<input type='checkbox' name='dow_Mon' value='Mon' checked>Mon"
        exp[37] = "<input type='checkbox' name='dow_Tue' value='Tue' checked>Tue"
        exp[39] = "<input type='checkbox' name='dow_Thu' value='Thu' checked>Thu"
        exp[40] = "<input type='checkbox' name='dow_Fri' value='Fri' checked>Fri"
        exp[41] = "<input type='checkbox' name='dow_Sat' value='Sat' checked>Sat"
        exp[42] = "<input type='checkbox' name='dow_Sun' value='Sun' checked>Sun"
        exp[52] = '<td><b>MainPin5</b></td>'
        got = web.html
        self.check_web(got, exp)
        pin5.change_mode('auto')
        web.index()
        exp[55] = "<td style='background-color:red'>"
        exp[57] = "<td style='background-color:green'>"
        got = web.html
        self.check_web(got, exp)

    def test2_0_change(self):
        """
        Web >2_0> change main pin through web-class
        """
        exp = [line for line in self.exp_head]
        exp.extend([line for line in self.exp_pin1])
        exp.extend([line for line in self.exp_main5])
        exp.extend([line for line in self.exp_tail])
        opt = self.opt.copy()
        opt['--test'] = "test1"
        web = Web(opt)
        web.index()
        got = web.html
        exp[17] = '<td><b>TestPin1</b></td>'
        exp[18] = "<td><input type='text' name='groups' value='grpA' size='10'></td>"
        exp[20] = "<td style='background-color:red'>"
        exp[34] = "<td><input type='text' name='start' value='01:00' size='5'>(24h)</td>"
        exp[36] = "<input type='checkbox' name='dow_Mon' value='Mon' checked>Mon"
        exp[37] = "<input type='checkbox' name='dow_Tue' value='Tue' checked>Tue"
        exp[39] = "<input type='checkbox' name='dow_Thu' value='Thu' checked>Thu"
        exp[40] = "<input type='checkbox' name='dow_Fri' value='Fri' checked>Fri"
        exp[41] = "<input type='checkbox' name='dow_Sat' value='Sat' checked>Sat"
        exp[42] = "<input type='checkbox' name='dow_Sun' value='Sun' checked>Sun"
        exp[44] = "<td><input type='text' name='duration' value='60' size='5'>min</td>"
        exp[52] = "<td><b>MainPin5</b></td>"
        exp[53] = "<td><input type='text' name='groups' value='grpA' size='10'></td>"
        exp[55] = "<td style='background-color:red'>"
        exp[57] = "<td style='background-color:red'>"
        self.check_web(got, exp)
        # should not happen
        web.update_slave(gpio='1', send='flip')
        got = web.html
        self.check_web(got, exp)
        # flip state=1
        web.update_main(gpio='5', send='flip')
        got = web.html
        exp[55] = "<td style='background-color:green'>"
        self.check_web(got, exp)
        # should happen
        web.update_slave(gpio='1', send='flip')
        got = web.html
        exp[20] = "<td style='background-color:green'>"
        self.check_web(got, exp)
        # flip state=off
        web.update_main(gpio='5', send='flip')
        got = web.html
        exp[20] = "<td style='background-color:red'>"
        exp[55] = "<td style='background-color:red'>"
        self.check_web(got, exp)
        web.update_main(gpio='5', send='AUTO')
        got = web.html
        exp[57] = "<td style='background-color:green'>"
        self.check_web(got, exp)
        web.update_slave(gpio='1', send='flip')
        got = web.html
        exp[20] = "<td style='background-color:green'>"
        exp[55] = "<td style='background-color:green'>"
        self.check_web(got, exp)
        web.update_slave(gpio='1', send='flip')
        got = web.html
        exp[20] = "<td style='background-color:red'>"
        exp[55] = "<td style='background-color:red'>"
        self.check_web(got, exp)



if __name__ == '__main__':
    unittest.main()