### YumUpoid - KDE Plasmoid listing package updates available in yum
### Copyright (C) 2012 Queria Sa-Tas
### See README.rst or COPYING files for more information.

import logging
import yum
import yum.misc
import sys

class YumUpoidBase(yum.YumBase):
    """ Simplified interface to Yum.

    Provides makeCache() and checkUpdate()
    for YumUpoidGui
    """

    # "old" yum logginglevels (as expected by doConfigSetup)
    YUM_LOG_DEBUGLEVEL_INFO = 0 # quiet
    YUM_LOG_DEBUGLEVEL_INFO_2 = 2
    YUM_LOG_DEBUGLEVEL_DEBUG_1 = 5 # verbose

    YUM_LOG_ERRORLEVEL_ERROR = 1
    YUM_LOG_ERRORLEVEL_WARN = 2

    LOG_ERRORS = YUM_LOG_ERRORLEVEL_WARN
    LOG_DEBUG = YUM_LOG_DEBUGLEVEL_INFO

    def __init__(self):
        super(YumUpoidBase, self).__init__()
        self.doConfigSetup(
                errorlevel=self.LOG_ERRORS,
                debuglevel=self.LOG_DEBUG
                )
        if not self.setCacheDir():
            self.conf.cache = 1

        # TODO: add ability to check for network connection
        # so we can use only cache
        # ...    self.conf.cache = 1
        # and skip makeCache later

        # FIXME: error handling: check if there is any enabled repo here
        # FIXME: error handling: fix possible yum db lock collisions?

    def doRepoSetup(self, thisrepo=None, dosack=1):
        """taken from yum-cli/cli.py"""
        # TODO: cleanup possible
        if self._repos and thisrepo is None:
            return self._repos
            
        if thisrepo:
            yum.YumBase._getRepos(self, thisrepo=thisrepo, doSetup=True)
        else:
            yum.YumBase._getRepos(self, thisrepo=thisrepo)

        if dosack: # so we can make the dirs and grab the repomd.xml but not import the md
            self.verbose_logger.log(yum.logginglevels.INFO_2,
                _('Reading repository metadata in from local files'))
            self._getSacks(thisrepo=thisrepo)
        
        return self._repos

    def makeCache(self):
        """taken from yum-cli/yumcommands.py#MakeCacheCommand"""
        # TODO: cleanup possible
        basecmd = "makecache"
        try:
            for repo in self.repos.findRepos('*'):
                repo.metadata_expire = 0
                repo.mdpolicy = "group:all"
            self.doRepoSetup(dosack=0)
            self.repos.doSetup()
            
            self.repos.populateSack(mdtype='all', cacheonly=1)

            fname_map = {'group_gz'   : 'groups.xml',
                         'pkgtags'    : 'pkgtags.sqlite',
                         'updateinfo' : 'updateinfo.xml',
                         }
            for repo in self.repos.listEnabled():
                for MD in repo.repoXML.fileTypes():
                    if MD not in fname_map:
                        continue
                    yum.misc.repo_gen_decompress(repo.retrieveMD(MD),
                                             fname_map[MD],
                                             cached=repo.cache)
        except yum.Errors.YumBaseError, e:
            return False
            # FIXME: error handling: propagate repo refresh failure up to Gui?
            #return 1, [exception2msg(e)]
        return True

    def checkUpdate(self, offline=False):
        if offline:
            self.conf.cache = 1
        res = {
                'updates': self.doPackageLists('updates').updates,
                'obsoletes': self.doPackageLists('obsoletes').obsoletes,
                'installed': {}
                }
        res['installed'] = self._fetch_installed(res['updates'])
        return res


    def getPackage(self, package_name, offline=False):
        """ Gets package info for given package_name.
            Returns all installed versions for given package.
            """
        if offline:
            self.conf.cache = 1
        return self.doPackageLists('installed', ['name', package_name]).installed

    def getPackages(self, package_names, offline=False):
        """ Searches for installed packages matching their names
            to the ones listed in package_names.
            Returns dict formatted as {'pkg_name':[found package versions list]}.
            """
        if offline:
            self.conf.cache = 1
        names = [part for name in package_names for part in ('name', name)]
        return self.doPackageLists('installed', names).installed

    def _fetch_installed(self, updates):
        installed = dict((pkg.name, []) for pkg in updates)
        found = self.getPackages([pkg.name for pkg in updates])
        for pkg in found:
            installed[ pkg.name ].append(pkg)

        ### slow 'by-one' search:
        #print('got updates, looking up installed versions...')
        #for pkg in updates:
        #    sys.stdout.write('.')
        #    sys.stdout.flush()
        #    installed[pkg.name] = self.checkPackage(pkg.name)

        return installed

