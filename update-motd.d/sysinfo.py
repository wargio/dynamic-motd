#!/usr/bin/python
#
# landscape-sysinfo-mini.py -- a trivial re-implementation of the 
# sysinfo printout shown on debian at boot time. No twisted, no reactor, just /proc & utmp
#
# (C) 2014 jw@owncloud.com
#
# inspired by ubuntu 14.10 /etc/update-motd.d/50-landscape-sysinfo
# Requires: python-utmp 
# for counting users.
#
# 2014-09-07 V1.0 jw, ad hoc writeup, feature-complete. Probably buggy?
# 2014-10-08 V1.1 jw, survive without swap
# 2014-10-13 V1.2 jw, survive without network

# Modified by Luc Didry in 2016
# Get the original version at https://github.com/jnweiger/landscape-sysinfo-mini

import sys
import os
import time
import glob
import utmp

_version_ = '1.2'

def percentage(x, total):
  if total < 1:
    return 0;
  p = 100. * (x / total)
  return p

def utmp_count():
  u = utmp.UtmpRecord()
  users = 0
  for i in u:
    if i.ut_type == utmp.USER_PROCESS:
      users += 1
  return users

def proc_meminfo():
  items = {}
  for l in open('/proc/meminfo').readlines():
    a = l.split()
    items[a[0]] = int(a[1])
  return items

def proc_mount():
  items = {}
  for m in open('/proc/mounts').readlines():
    a = m.split()
    if a[0].find('/dev/') == 0:
      statfs = os.statvfs(a[1])
      perc = 100 - percentage(statfs.f_bavail, statfs.f_blocks)
      gb = statfs.f_bsize*statfs.f_blocks/1024./1024/1024
      items[a[1]] = "{:4.1f} % of {:8.2f} GB".format(perc, gb)
  return items

loadav    = float(open("/proc/loadavg").read().split()[1])
processes = len(glob.glob('/proc/[0-9]*'))
statfs    = proc_mount()
users     = utmp_count()
meminfo   = proc_meminfo()
memperc   = "{:.2f}%".format(100 - percentage(meminfo['MemAvailable:'], (meminfo['MemTotal:'] or 1)))
swapperc  = "{:.2f}%".format(100 - percentage(meminfo['SwapFree:'], (meminfo['SwapTotal:'] or 1)))

if meminfo['SwapTotal:'] == 0: swapperc = '---'

print ("  System information as of {}\n".format(time.asctime()))
print ("  System load:  {:<5.2f}                Processes:           {}".format(loadav, processes))
print ("  Memory usage: {:<4s}               Users logged in:     {}".format(memperc, users))
print ("  Swap usage:   {}".format(swapperc))

print ("  Disk Usage:")
for k in sorted(statfs.keys()):
  print ("    {} {}".format(statfs[k], k))

if users > 0:
    a = utmp.UtmpRecord()

    print ("\n  Logged in users:")

    for b in a: # example of using an iterator
        if b.ut_type == utmp.USER_PROCESS:
            print ("    \033[1;31m{:<10s}\033[m from {:<25s} at {:<20s}".format(b.ut_user, b.ut_host, time.ctime(b.ut_tv[0])))
    a.endutent()

sys.exit(0)
