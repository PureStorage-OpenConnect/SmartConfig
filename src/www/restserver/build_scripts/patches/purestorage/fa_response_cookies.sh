pip3 download --no-deps purestorage==1.19.0
mv purestorage-1.19.0.tar.gz /tmp/
cd /tmp	
tar -xvf purestorage-1.19.0.tar.gz
cp /var/www/restserver/build_scripts/patches/purestorage/fa_response_cookies.patch purestorage-1.19.0/
cd purestorage-1.19.0/
patch -p1 < fa_response_cookies.patch
. /var/www/restserver/venv/bin/activate
pip3 install /tmp/purestorage-1.19.0
rm -rf /tmp/purestorage-1.19.0*

