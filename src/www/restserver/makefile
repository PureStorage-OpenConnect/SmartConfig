# Pure Project Make File
# author: Abhilash

VIRTUALENV = $(shell which virtualenv)

clean: shutdown
	rm -fr venv
	rm -fr puremicroframework.egg-info
	find . -name "*.pyc" -exec rm -f {} \;

venv:
	$(VIRTUALENV) venv

install: clean venv
	. venv/bin/activate; sh install_packages.sh
	. venv/bin/activate; python setup.py install
	. venv/bin/activate; python setup.py develop

launch: venv shutdown
	. venv/bin/activate; python  src/www/restserver/pure_dir/services/common/gateway/gateway.py &
	#. venv/bin/activate; python  services/ &

confconsole:
	rm -rf /usr/lib/confconsole 
	rm -rf /usr/bin/confconsole	
	rm -rf /etc/confconsole
	cp -r pure_dir/infra/confconsole /usr/lib/.
	chmod +x /usr/lib/confconsole/*
	ln -s /usr/lib/confconsole/confconsole.py /usr/bin/confconsole
	yes | cp -r /usr/lib/confconsole/etc/init.d/confconsole /etc/init.d/confconsole
	mkdir -p /etc/systemd/system/getty@tty1.service.d
	yes | cp -r /usr/lib/confconsole/etc/systemd/system/getty@tty1.service.d/override.conf /etc/systemd/system/getty@tty1.service.d/override.conf
	yes | cp -r /usr/lib/confconsole/etc/sysconfig/network-scripts/static-network /etc/sysconfig/network-scripts/static-network
	mkdir -p /etc/confconsole
	yes | cp -r /usr/lib/confconsole/etc/confconsole/services.txt /etc/confconsole/.
	yes | cp -r /usr/lib/confconsole/etc/confconsole/confconsole.conf /etc/confconsole/.
	
firewall:
	firewall-cmd --zone=public --add-service=http --permanent

shutdown:

