#!/bin/sh
py='/home/tops/bin/python'
cluster='10.101.83.226:4181,10.101.83.239:4181,10.101.83.237:4181'
file=node_size.dat
root='/zk_size_test'
count=10000

rm -rf $file

for((i=1; i <= 7; ++i))
do
    echo "$(($i*10))" >> $file
done

test()
{
    size=$1
    $py zk-latencies.py --cluster="$cluster"  --root_znode="$root" --znode_count=$count \
        --znode_size=$size --timeout=30000 > result.tmp
    op_set=`cat result.tmp | grep 'set' | awk '{print $9}' | awk -F '.' '{print $1}'`
    op_get=`cat result.tmp | grep 'get' | awk '{print $9}' | awk -F '.' '{print $1}'`
    echo "size test $count $size" >> size.result
    cat result.tmp >> size.result
    echo $op_set, $op_get
    sed -i "${i}s/$/\t&${op_set}/g" $file
    sed -i "${i}s/$/\t&${op_get}/g" $file
}

for((i=1; i <= 7; ++i))
do
    n=$(($i*1024*10))
    test $n
done

rm -rf cli_log*

