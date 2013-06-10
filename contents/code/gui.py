### YumUpoid - KDE Plasmoid listing package updates available in yum
### Copyright (C) 2012 Queria Sa-Tas
### See README.rst or COPYING files for more information.

from __future__ import print_function
from datetime import timedelta, datetime
from base import YumUpoidBase
from pkg_resources import parse_version
from PyQt4.QtCore import *
from PyQt4.QtGui import QGraphicsLinearLayout
#                             from PyQt4.QtGui import *
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript

class YumUpoidGui(object):
    def __init__(self):
        self.conf_show_release_change = False
        pass

    def yumMakeCache(self):
        return YumUpoidBase().makeCache()

    def yumGetUpdates(self,offline=False):
        return YumUpoidBase().checkUpdate(offline)

    def format_version(self,pkg,full=False):
        if full:
            epoch = ''
            if pkg.epoch and pkg.epoch != '0':
                epoch = "{0}:".format(pkg.epoch)
            # results of fullare "too" long for me
            return "{0}{1}-{2}.{3}".format(
                        epoch,
                        pkg.version,
                        pkg.release,
                        pkg.arch)
        return "{0}".format(pkg.version)

    def format_update(self, new_pkg, old_pkgs=None):
        old_pkgs = old_pkgs or []
        old_version = [self.format_version(pkg) for pkg in old_pkgs] or ['?']
        new_version = self.format_version(new_pkg)
        change_symbol = ' => '

        if new_version in old_version:
            if self.conf_show_release_change:
                # we need to also display release revision
                old_version = [self.format_version(pkg, True) for pkg in old_pkgs] or ['?']
                new_version = self.format_version(new_pkg, True)
            else:
                change_symbol = ' '
                old_version = [new_version]
                new_version = 'repack'
        return "{0} {1}{2}{3}".format(
                new_pkg.name,
                ', '.join(old_version),
                change_symbol,
                new_version)

    def split_updates(self, updates, installed):
        splitted = {'updates': [], 'downgrades': [], 'repacks': []}
        for pkg in updates:
            change = -9999
            for old in (installed[pkg.name] or []):
                change = max(change,
                             cmp(parse_version(pkg.version),
                                 parse_version(old.version)))
            if change == -1:
                splitted['downgrades'].append(pkg)
            if change == 0:
                splitted['repacks'].append(pkg)
            else:
                splitted['updates'].append(pkg)
        return splitted


class YumUpoid(YumUpoidGui,plasmascript.Applet):


    def __init__(self, parent, args=None):
        YumUpoidGui.__init__(self)
        plasmascript.Applet.__init__(self,parent)
        self.timer = QTimer()
        self.refresh_timer = QTimer()
        self.refresh_timer.setSingleShot(True)
        self.skip_yum = False
        self.updates = ''
        self.force_makecache = False # force 'yum makecache' on refresh
        self.set_interval(30)

    def init(self):
        self.init_applet()

        QObject.connect(self.refresh_timer, SIGNAL('timeout()'), self.refresh)

        # call first refresh after our plasmoid is completely set-up
        QObject.connect(self.timer, SIGNAL('timeout()'), self.firstrun)
        self.timer.start(1000)
        self.next_check = datetime.now()

    def init_applet(self):
        self.setHasConfigurationInterface(False)
        self.setAspectRatioMode(Plasma.IgnoreAspectRatio)

        self.theme = Plasma.Svg(self)
        self.theme.setImagePath("widgets/background")
        self.setBackgroundHints(Plasma.Applet.DefaultBackground)

        self.layout = QGraphicsLinearLayout(Qt.Horizontal, self.applet)
        self.output = Plasma.TextBrowser(self.applet)
        self.output.setText('initializing please wait ...')
        self.layout.addItem(self.output)
        self.applet.setLayout(self.layout)

        self.resize(600, 300)

    def set_interval(self, interval_minutes):
        interval_minutes = max(interval_minutes, 10)

        self.interval_minutes = interval_minutes
        self.interval = 1000 * 60 * interval_minutes
        self.interval_delta = timedelta(minutes=interval_minutes)

    def firstrun(self):
        QObject.disconnect(self.timer, SIGNAL('timeout()'), self.firstrun)
        self.timer.stop()

        QObject.connect(self.timer, SIGNAL('timeout()'), self.trigger_refresh)
        self.timer.start(self.interval)

        self.trigger_refresh()


    def trigger_refresh(self):
        self.output.setText('checking updates...')
        self.refresh_timer.start(300)
        self.next_check = datetime.now() + self.interval_delta
        

    def refresh(self):
        message = ''

        if not self.skip_yum:
            if not self.force_makecache or self.yumMakeCache():
                self.updates = ''
            else:
                message = "Offline - using local cache only.\n"

            if not self.updates:
                self.getUpdates()

        self.output.setText(message + self.updates #)
            + "\nNext check at {0}.".format(self.format_next_check()))

    def getUpdates(self, offline=False):
        self.updates = ''
        packages = self.yumGetUpdates(offline)
        obsoletes = []
        updates = []

        obsoletes = [ "  {0}\n".format(package.name)
            for package in packages['obsoletes']]
        updates = [ "  {0}\n".format(
            self.format_update(
                package,
                packages['installed'][package.name]))
            for package in packages['updates']]

        obsoletes.sort()
        updates.sort()

        if obsoletes:
            self.updates += "==[ Obsolete packages ]==\n"
            self.updates += "".join(obsoletes)
        if updates:
            self.updates += "==[ Available updates ]==\n"
            self.updates += "".join(updates)

        if not self.updates:
            self.updates = "Your system is up to date.\nGood job!\n"
        
    def format_next_check(self):
        now = datetime.now()
        nxt = self.next_check
        if nxt.date() == now.date():
            return "{0:02}:{1:02}".format( nxt.hour, nxt.minute )
        else:
            return "{0}.{1}. {2:02}:{3:02}".format(
                    nxt.day,
                    nxt.month,
                    nxt.hour,
                    nxt.minute
                    )

        

class YumUpoidCli(YumUpoidGui):
    def __init__(self):
        YumUpoidGui.__init__(self)

    def show_updates(self):
        packages = self.yumGetUpdates()

        if packages['obsoletes']:
            obsolete = [package.name for package in packages['obsoletes']]
            obsolete.sort()
            print("[OBSO] ", end='')
            print("\n[OBSO] ".join(obsolete))

        changed = self.split_updates(
            packages['updates'], packages['installed'])
        categories = {
            'DOWN': 'Downgrades',
            'UPDT': 'Updates',
            'RPCK': 'Repacks'}
        for label, change in categories.iteritems():
            chid = change.lower()
            if changed[chid]:
                changed[chid] = [self.format_update(
                    pkg, packages['installed'][pkg.name])
                    for pkg in changed[chid]]
                changed[chid].sort()
                print('[%s] ' % label, end='')
                print(('\n[%s] ' % label).join(changed[chid]))

    def show_package(self):
        pkg = YumUpoidBase().getPackages(['opera'])
        print(pkg)
        #print('available: '+str(pkg.available))
        #print('installed: '+str(pkg.installed))
        #print('updates: '+str(pkg.updates))
        #print('extras: '+str(pkg.extras))
        #print('obsoletes: '+str(pkg.obsoletes))
        #print('recent: '+str(pkg.recent))

    def run(self):
        self.show_updates()
        #self.show_package()
