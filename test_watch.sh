#!/bin/sh
py='/home/tops/bin/python'
cluster='10.101.83.226:4181,10.101.83.239:4181,10.101.83.237:4181'
file=watch.dat
step=10000
root='/zk_watch_test'

rm -rf $file

for((i=1; i <= 10; ++i))
do
    echo $(($i*$step)) >> $file
done

for((i=1; i <= 10; ++i))
do
    n=$(($i*$step))
    ops=`$py zk-watch.py --cluster="$cluster"  --root_znode="$root" --znode_count=$n | \
        grep 'set' | awk '{print $9}' | awk -F '.' '{print $1}'`
    ops_no=`$py zk-watch.py --cluster="$cluster"  --root_znode="$root" --znode_count=$n --watch_multiple=0| \
        grep 'set' | awk '{print $9}' | awk -F '.' '{print $1}'`
    echo $ops, $ops_no
    sed -i "${i}s/$/\t&${ops}/g" $file
    sed -i "${i}s/$/\t&${ops_no}/g" $file
done

rm -rf cli_log*

