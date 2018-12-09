#!/bin/sh
if [ -f /etc/debian_version ]; then
	apt-get install  libyaml-0-2
        #apt-get install  libyaml-devel.x86_64
else
	yum install -y libffi-devel.x86_64
	yum install -y libyaml-devel.x86_64
	yum install -y dialog
	yum install -y at
	yum install -y genisoimage
fi
