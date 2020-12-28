pip3 download --no-deps ucsmsdk
mv ucsmsdk-0.9.10.tar.gz /tmp/
cd /tmp	
tar -xvf ucsmsdk-0.9.10.tar.gz
cp /var/www/restserver/build_scripts/patches/ucsmsdk/ucsmsdk_pyparsing.patch ucsmsdk-0.9.10/
cd ucsmsdk-0.9.10/
patch -p1 < ucsmsdk_pyparsing.patch
. /var/www/restserver/venv/bin/activate
pip3 install /tmp/ucsmsdk-0.9.10
rm -rf /tmp/ucsmsdk-0.9.10*

