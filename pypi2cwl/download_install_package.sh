#!/usr/bin/env bash
# $1 - working directory
# $2 - package name
# $3 - True/False : True - install globally, False - install within virtualenv

cd $1
mkdir p2c-dir
cd p2c-dir

# if package was already downloaded we shouldn't download it again
package_downloaded=false
for entry in *
do
    if [[ $entry == $2* ]]; then
    package_downloaded=true
    fi
done

if [ "$package_downloaded" = false ]; then
    pip install $2 --download . --no-deps --no-binary :all:
    for entry in *
    do
        if [[ $entry =~ \.gz$ ]]; then
        tar xf ${entry}
        y=${entry%%.tar.gz}
        2to3 -w ${y##*/}/setup.py
        rm -rf ${entry}
        fi
    done
fi

if [ "$3" == "True" ]; then
    sudo pip2 install $2 || sudo pip3 install $2 || exit 1;
else
    pip2 install $2 || pip3 install $2 || exit 1
fi
