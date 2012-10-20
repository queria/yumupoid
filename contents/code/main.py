#!/usr/bin/env python

""" KDE Plasmoid displaying available yum package updates """
from gui import *

def CreateApplet(parent):
    return YumUpoid(parent)

if __name__ == '__main__':
    YumUpoidCli().run()


