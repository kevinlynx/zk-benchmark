#!/bin/sh
py='/home/tops/bin/python'
cluster='10.101.83.226:4181,10.101.83.239:4181,10.101.83.237:4181'
file=node.dat
step=10000
root='/zk_node_test'

rm -rf $file

for((i=1; i <= 10; ++i))
do
    echo $(($i*$step)) >> $file
done

for((i=1; i <= 10; ++i))
do
    n=$(($i*$step))
    $py zk-latencies.py --cluster="$cluster"  --root_znode="$root" --znode_count=$n > result.tmp
    op_set=`cat result.tmp | grep 'set' | awk '{print $9}' | awk -F '.' '{print $1}'`
    op_get=`cat result.tmp | grep 'get' | awk '{print $9}' | awk -F '.' '{print $1}'`
    echo $op_set, $op_get
    sed -i "${i}s/$/\t&${op_set}/g" $file
    sed -i "${i}s/$/\t&${op_get}/g" $file
done

rm -rf cli_log*

