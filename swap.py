# -*- coding: utf-8 -*-
'''
SaltStack code snippets.
Return informations for swap filesystem
Copyright (C) 2017 Davide Madrisan <davide.madrisan.gmail.com>
'''
# Import python libs
import collections
import os

# Import Salt libs
import salt.utils

# Define the module's virtual name
__virtualname__ = 'swap'

swap_proc_file = '/proc/swaps'

def __virtual__():
    '''
    Make sure the /proc file system is mounted and provides /proc/swaps
    '''
    if not os.path.isfile(swap_proc_file):
        return (False, 'The {0} file cannot be found.'.format(swap_proc_file))
    return True

def _sizeof_fmt(tok, factor=1024.0, skip=1, suffix='B'):
    '''
    Divide 'tok' to its best unit and append it to the output.
    '''
    try:
        num = int(tok)
    except ValueError:
        return tok

    units = ['', 'k','M','G','T','P']
    for unit in units[skip:]:
        if num < factor:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= factor
    return "%.1f%s%s" % (num, 'p', suffix)

def usage(human_readable=True):
    '''
    Return usage information for swap filesystem

    CLI Example:

    .. code-block:: bash

        salt '*' swap.usage True

    '''
    cols = ('filename', 'swaptype', 'size', 'used', 'priority')
    Swap = collections.namedtuple('Swap', cols)
    fmt = lambda num: _sizeof_fmt(num) if human_readable else int(num)

    def swap_info(swap):
        return {
            'available': fmt(int(swap.size) - int(swap.used)),
            'device': swap.filename,
            'priority': swap.priority,
            'size': fmt(swap.size),
            'used': fmt(swap.used)
        }

    blkid_out = __salt__['disk.blkid']()
    swap_devices = [dev for dev, details in blkid_out.items()
                       if details.get('TYPE', '') == 'swap']

    def to_blkid(dev):
        '''
        This function Try to map the dm device to the lvm one (in case of lvm
        partitioning).  Ex: /dev/dm-1 --> /dev/mapper/rootvg-swaplv
        '''
        for blkdev in swap_devices:
            try:
                rl =__salt__['file.readlink'](blkdev, canonicalize=True)
                if rl == dev:
                    return blkdev
            except:
                pass
        return dev

    header = lambda line: line.startswith('Filename')

    with salt.utils.fopen(swap_proc_file, 'r') as fh_:
        data = (Swap(*line.split()) for line in fh_
            if not header(line))
        return dict((to_blkid(swap.filename), swap_info(swap)) for swap in data
            if swap.swaptype == 'partition')   # ignore swap files
