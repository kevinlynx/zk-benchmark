#!/usr/bin/env python

import datetime, time, os
from optparse import OptionParser

import zkclient
from zkclient import ZKClient, CountingWatcher, zookeeper


usage = "usage: %prog [options]"
parser = OptionParser(usage=usage)
parser.add_option("", "--cluster", dest="cluster",
                  default=None, help="comma separated list of host:port, test as a cluster")
parser.add_option("", "--timeout", dest="timeout", type="int",
                  default=5000, help="session timeout in milliseconds (default %default)")
parser.add_option("", "--root_znode", dest="root_znode",
                  default="/zk-latencies", help="root for the test, default /zk-latencies")
parser.add_option("", "--znode_count", dest="znode_count", default=10000, type="int",
                  help="the number of znodes to operate on in each performance section (default %default)")
parser.add_option("", "--watch_multiple", dest="watch_multiple", default=1, type="int",
                  help="number of watches to put on each znode (default %default)")
parser.add_option("", "--znode_size", dest="znode_size", type="int",
                  default=25, help="data size when creating/setting znodes (default %default)")
parser.add_option("", "--next_watch", dest="next_watch", action="store_true",
                  default=False, help="data size when creating/setting znodes (default %default)")
parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="verbose output, include more detail")
parser.add_option("-q", "--quiet",
                  action="store_true", dest="quiet", default=False,
                  help="quiet output, basically just success/failure")

(options, args) = parser.parse_args()

zkclient.options = options

zookeeper.set_log_stream(open("cli_log_%d.txt" % (os.getpid()),"w"))

class SmokeError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def print_elap(start, msg, count):
    elapms = (time.time() - start) * 1000
    if int(elapms) != 0:
        print("%s in %6d ms (%f ms/op %f/sec)"
              % (msg, int(elapms), elapms/count, count/(elapms/1000.0)))
    else:
        print("%s in %6d ms (included in prior)" % (msg, int(elapms)))

def timer(ops, msg, count=options.znode_count):
    start = time.time()
    for op in ops:
        pass
    print_elap(start, msg, count)

def timer2(func, msg, count=options.znode_count):
    start = time.time()
    func()
    print_elap(start, msg, count)

def child_path(i):
    return "%s/session_%d" % (options.root_znode, i)

def create_nodes(s):
    def func():
        callbacks = []
        for j in xrange(options.znode_count):
            cb = zkclient.CreateCallback()
            cb.cv.acquire()
            s.acreate(child_path(j), cb, data)
            callbacks.append(cb)

        for j, cb in enumerate(callbacks):
            cb.waitForSuccess()
            if cb.path != child_path(j):
                raise SmokeError("invalid path %s for operation %d on handle %d" %
                                 (cb.path, j, cb.handle))

    timer2(func, "created %7d permanent znodes " % (options.znode_count))

def add_wathches(s):
    # async operation in a watcher causes dead lock ?
    def watch(handle, typ, state, path):
        print "watch event (%s)" % path
        cb = zkclient.GetCallback()
        cb.cv.acquire()
        s.aget(path, cb, watch)
        cb.waitForSuccess()

    def watch_sync(handle, typ, state, path):
        if options.verbose:
            print "watch event (%s)" % path
        if options.next_watch and s.exists(path):
            s.get(path, watch_sync)

    def func():
        callbacks = []
        for j in xrange(options.znode_count):
            cb = zkclient.GetCallback()
            cb.cv.acquire()
            s.aget(child_path(j), cb, watch_sync)
            callbacks.append(cb)

        for cb in callbacks:
            cb.waitForSuccess()
            if cb.value != data:
                raise SmokeError("invalid data %s for operation %d on handle %d" %
                                 (cb.value, j, cb.handle))

    timer2(func, "get     %7d           znodes " % (options.znode_count))

def set_nodes(s, data):
    def func():
        callbacks = []
        for j in xrange(options.znode_count):
            cb = zkclient.SetCallback()
            cb.cv.acquire()
            s.aset(child_path(j), cb, data)
            callbacks.append(cb)

        for cb in callbacks:
            cb.waitForSuccess()

    timer2(func, "set     %7d           znodes " % (options.znode_count))

def delete_nodes(s):
    def func():
        callbacks = []
        for j in xrange(options.znode_count):
            cb = zkclient.DeleteCallback()
            cb.cv.acquire()
            s.adelete(child_path(j), cb)
            callbacks.append(cb)

        for cb in callbacks:
            cb.waitForSuccess()

    timer2(func, "deleted %7d permanent znodes " % (options.znode_count))

def get_zk_servers():
    return options.cluster

if __name__ == '__main__':
    data = options.znode_size * "x"
    servers = get_zk_servers()

    session_get = ZKClient(servers, options.timeout)
    session_set = ZKClient(servers, options.timeout)

    session_set.create(options.root_znode,
        "smoketest root, delete after test done, created %s" % (datetime.datetime.now().ctime()))

    create_nodes(session_set)
    for x in xrange(options.watch_multiple):
        add_wathches(session_get)
    set_nodes(session_set, data)
    delete_nodes(session_set) 

    time.sleep(10)
    session_set.delete(options.root_znode)
    session_get.close()
    session_set.close()
    print 'watch test complete'

