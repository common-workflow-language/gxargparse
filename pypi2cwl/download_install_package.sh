#!/usr/bin/env bash
# $1 - package name
# $2 - pip2/pip3 - python version
# $3 - True/False : True - install globally, False - install within virtualenv

mkdir p2c-dir
cd p2c-dir

# if package was already downloaded we shouldn't download it again
package_downloaded=false
for entry in *
do
    if [[ $entry == $1* ]]; then
    package_downloaded=true
    fi
done

if [ "$package_downloaded" = false ]; then
    pip download $1 --no-deps --no-binary :all:
    for entry in *
    do
        if [[ $entry =~ \.gz$ ]]; then
        tar xf ${entry}
        rm -rf ${entry}
        fi
    done
fi

if [ "$3" == "True" ]; then
sudo $2 install $1
else
$2 install $1
fi
