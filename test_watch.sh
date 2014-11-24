#!/bin/sh
py='/home/tops/bin/python'
cluster='10.101.83.226:4181,10.101.83.239:4181,10.101.83.237:4181'
file=watch.dat
size=10
step=1000
root='/zk_watch_test'

rm -rf $file

for((i=1; i <= 10; ++i))
do
    echo $(($i*$step)) >> $file
done

step()
{
    watch=$1
    for((i=1; i <= 10; ++i))
    do
        n=$(($i*$step))
        echo "$watch:$n"
        ops=`$py zk-watch.py --cluster="$cluster"  --root_znode="$root" --znode_count=$n --watch_session=$watch \
            --timeout=60000 --znode_size=$size | grep 'set' | awk '{print $9}' | awk -F '.' '{print $1}'`
        sed -i "${i}s/$/\t&${ops}/g" $file
    done
}

step 0
step 1
step 5
step 10

rm -rf cli_log*

