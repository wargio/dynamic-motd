#!/bin/bash

if [ $EUID -ne 0 ]; then
  echo "Please run as root"
  exit
fi

if [ -d "/etc/update-motd.d/" ]; then
	rm -rfv /etc/update-motd.d/
fi

cp -rv update-motd.d/ /etc/
chmod -v 755 /etc/update-motd.d/
chmod -v 644 /etc/update-motd.d/colors /etc/update-motd.d/sysinfo.py
rm -rfv /etc/motd
ln -sv /var/run/motd /etc/motd
