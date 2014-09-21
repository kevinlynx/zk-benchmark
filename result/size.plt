set xlabel "node data size(kb)"
set ylabel "set/get ops"
set title "zookeeper node size benchmark"
set xrange [0:100]
set xtics 10, 10, 100
set yrange [0:8000]
set ytics 0, 1000, 8000
plot "node_size.dat" u 1:2 w lp pt 5 title "set", "node_size.dat" u 1:3 w lp pt 7 title "get"


