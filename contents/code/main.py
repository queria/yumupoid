#!/usr/bin/env python

### YumUpoid - KDE Plasmoid listing package updates available in yum
### Copyright (C) 2012 Queria Sa-Tas
### See README.rst or COPYING files for more information.

from gui import *

def CreateApplet(parent):
    return YumUpoid(parent)

if __name__ == '__main__':
    YumUpoidCli().run()


