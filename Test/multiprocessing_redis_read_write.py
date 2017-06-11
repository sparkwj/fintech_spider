#!/usr/bin/env python3
# coding: utf-8
# File: multiprocessing_redis_read_write.py
# Author: lxw
# Date: 6/11/17 3:29 PM

import multiprocessing
import os
import redis
import time


class RedisMultiprocessReadWrite:
    pool = redis.ConnectionPool(host="127.0.0.1", port=6379, db=0)
    # [redis连接对象是线程安全的](http://www.cnblogs.com/clover-siyecao/p/5600078.html)
    # [redis是单线程的](https://stackoverflow.com/questions/17099222/are-redis-operations-on-data-structures-thread-safe)
    REDIS_URI = redis.Redis(connection_pool=pool)
    REDIS_KEY = "MULTIPROCESSING_TEST_HASH"

    def initialize_redis(self):
        for i in range(20):
            self.REDIS_URI.hset(self.REDIS_KEY, str(i), "0")

    def redis_check_in(self, field):
        # print("pid: {0}, id(REDIS_URI):{1}".format(os.getpid(), id(self.REDIS_URI)))
        print("pid: {0}".format(os.getpid()))
        result = self.REDIS_URI.hexists(self.REDIS_KEY, field)
        print("{0} in redis: {1}".format(field, result))
        time.sleep(5)

    def test_multiprocessing_read_write(self):
        pool = multiprocessing.Pool(processes=6)  # IP代理数目是6, 所以这里把进程数目也设置为6
        for i in range(0, 30, 2):
            pool.apply_async(self.redis_check_in, (i,))

        pool.close()
        pool.join()


if __name__ == '__main__':
    rmrw = RedisMultiprocessReadWrite()
    rmrw.initialize_redis()
    rmrw.test_multiprocessing_read_write()