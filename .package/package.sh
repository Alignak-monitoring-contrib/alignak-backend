#!/bin/sh

set -ev

gem install fpm

# Debian

sed -i -e "s/# plugin/plugin/g" etc/uwsgi.ini

if [ "$1" = "master" ]; then
   if [ "$2" = "2.7" ]; then
     fpm -s python --python-install-lib "/usr/lib/python2.7/dist-packages" -t deb -a all --python-disable-dependency uwsgi -d uwsgi-plugin-python -d python-requests-futures --deb-systemd .package/alignak-backend.service --deb-no-default-config-files --python-install-data '/usr/local' ./setup.py
     version=`python -c "from alignak_backend import __version__;print(__version__)"`
   elif [ "$2" = "3.4" ]; then
     sudo apt-get install python3-setuptools
     sudo apt-get install -y python3-pip
     fpm -s python --python-install-lib "/usr/lib/python3/dist-packages" --python-pip /usr/bin/pip3 --python-bin /usr/bin/python3 --python-package-name-prefix python3 -t deb -a all --python-disable-dependency uwsgi -d uwsgi-plugin-python3 -d python3-requests-futures --deb-systemd .package/alignak-backend.service --deb-no-default-config-files --python-install-data '/usr/local' ./setup.py
     version=`python3 -c "from alignak_backend import __version__;print(__version__)"`
   fi
   sed -i -e "s|\"dev\"|\"${version}\"|g" .bintray.json
   sed -i -e s/alignak_deb-testing/alignak_deb-stable/g .bintray.json
elif [ "$1" = "develop" ]; then
   DEVVERSION=`date "+%Y%m%d%H%M%S"`
   if [ "$2" = "2.7" ]; then
     fpm --debug -s python --python-install-lib "/usr/lib/python2.7/dist-packages" -t deb -a all -v $DEVVERSION-dev --python-disable-dependency uwsgi -d uwsgi-plugin-python -d python-requests-futures --deb-systemd .package/alignak-backend.service --deb-no-default-config-files --python-install-data '/usr/local' ./setup.py
   elif [ "$2" = "3.4" ]; then
     sudo apt-get install python3-setuptools
     sudo apt-get install -y python3-pip
     fpm -s python --python-install-lib "/usr/lib/python3/dist-packages" --python-pip /usr/bin/pip3 --python-bin /usr/bin/python3 --python-package-name-prefix python3 -t deb -a all -v $DEVVERSION-dev --python-disable-dependency uwsgi -d uwsgi-plugin-python3 -d python3-requests-futures --deb-systemd .package/alignak-backend.service ./setup.py
   fi
fi
