#!/bin/bash

# Script to convert xml sources in __xml__ to the local arch.

arch=$(uname -i);
if [ "$arch" == "x86_64" ] ; then
        ARCH=64;
elif [ "$arch" == "i386" ] ; then
        ARCH=32;
else
        echo "Unrecognized arch $arch";
        exit 1;
fi

echo "Detected arch $ARCH."

for pth in $(find __xml__ -type f) ; do
        target=$(echo $pth | sed "s/__xml__/$ARCH/" | sed "s/.rrd.xml/.rrd/")
        echo "Converting from $pth";
        echo "             to      $target";
        rm -rf $target;

        fname=$( basename $target )
        direc=$(echo $target | sed "s/$fname//g")
        mkdir -p $direc

        rrdtool restore $pth $target
done
