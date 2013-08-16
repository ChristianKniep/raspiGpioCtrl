#! /usr/bin/env python
# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser


class GpioCtrl(object):
    """
    Controller of raspberry gpio pins
    """
    def __init__(self, opt):
        """
        init gpio
        """
        self.opt = opt
        self.gpio_pins = {}
        self.cfg_file = None

    def set_cfg(self, file_path):
        """
        Set file path of cfg_file
        """
        self.cfg_file = file_path

    def read_cfg(self):
        """
        read cfg file and update gpio_pins dict
        """
        config = ConfigParser()
