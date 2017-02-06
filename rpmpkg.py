# -*- coding: utf-8 -*-
'''
SaltStack code snippets
Get the date of the last rpm package update/installation and the list of packages

Copyright (C) 2017 Davide Madrisan <davide.madrisan.gmail.com>

'''

# Import python libs
import time

try:
    import rpm
    HAS_RPM_LIBS = True
except ImportError:
    HAS_RPM_LIBS = False

__virtualname__ = 'rpmpkg'

def __virtual__():
    if __grains__.get('os_family') == 'RedHat':
        if not HAS_RPM_LIBS:
            return (False, 'The rpm python lib cannot be loaded')
        return __virtualname__

    return (False,
        'The {0} module cannot be loaded: '
        'unsupported OS family'.format(__virtualname__))

def list_pkgs():
    '''
    List the packages currently installed in a dict::

        {'<package_name>': '<epoch>:<version>-<release>.<arch>'}

    CLI Example:

        .. code-block:: bash

            salt '*' rpmpkg.list_pkgs
    '''
    ts = rpm.TransactionSet()
    mi = ts.dbMatch()
    epoch = lambda h: "%s:" % h['epoch'] if h['epoch'] else ''
    pkgs = dict([
        (h['name'], "%s%s-%s.%s" % (
            epoch(h), h['version'], h['release'], h['arch']))
        for h in mi])
    return pkgs

def lastupdate():
    '''
    Return the date of the last rpm package update/installation.

    CLI Example:

        .. code-block:: bash

            salt '*' rpmpkg.lastupdate
    '''
    installdate = lambda h: h.sprintf("%{INSTALLTID:date}")
    installptime = lambda h: time.strptime(installdate(h), "%c")

    ts = rpm.TransactionSet()
    mi = ts.dbMatch()
    last = max(installptime(h) for h in mi)

    return time.asctime(last)

def buildtime():
    '''
    Return the build date and time.

    CLI Example:

        .. code-block:: bash

            salt '*' rpmpkg.buildtime
    '''
    installdate = lambda h: h.sprintf("%{INSTALLTID:date}")
    installptime = lambda h: time.strptime(installdate(h), "%c")

    ts = rpm.TransactionSet()
    mi = ts.dbMatch()
    first = min(installptime(h) for h in mi)

    return time.asctime(first)
