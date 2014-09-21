set xlabel "node count"
set ylabel "set ops"
set title "zookeeper watch/node count benchmark"
set xrange [0:110000]
set xtics 10000, 10000, 100000
set yrange [0:8000]
set ytics 0, 1000, 8000
plot "watch.dat" using 1:2 w lp pt 5 title "watch", "watch.dat" using 1:3 w lp pt 7 title "without watch"


