pip3 download --no-deps pycsco
mv pycsco-0.3.5.tar.gz /tmp/
cd /tmp	
tar -xvf pycsco-0.3.5.tar.gz
cp /var/www/restserver/build_scripts/patches/pycsco/pycsco_python3.patch pycsco-0.3.5/
cd pycsco-0.3.5/
patch -p1 < pycsco_python3.patch
. /var/www/restserver/venv/bin/activate
pip3 install /tmp/pycsco-0.3.5
rm -rf /tmp/pycsco-0.3.5*

