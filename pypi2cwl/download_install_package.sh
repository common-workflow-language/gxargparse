#!/usr/bin/env bash
# $1 - working directory
# $2 - package name
# $3 - pip2/pip3 - python version
# $4 - True/False : True - install globally, False - install within virtualenv

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
    pip download $2 --no-deps --no-binary :all:
    for entry in *
    do
        if [[ $entry =~ \.gz$ ]]; then
        tar xf ${entry}
        rm -rf ${entry}
        fi
    done
fi

if [ "$4" == "True" ]; then
sudo $3 install $2
else
$3 install $2
fi
