#!/usr/bin/env python3
# coding: utf-8
# File: redis_ops.py
# Author: lxw
# Date: 6/7/17 3:07 PM

import redis
from Spiders.CNKIPatentSpider.settings import HOST
from Spiders.CNKIPatentSpider.settings import PORT
from Spiders.CNKIPatentSpider.settings import KEY_NAME


class RedisClient:
    pool = redis.ConnectionPool(host=HOST, port=PORT, db=0)
    # [redis连接对象是线程安全的](http://www.cnblogs.com/clover-siyecao/p/5600078.html)
    # [redis是单线程的](https://stackoverflow.com/questions/17099222/are-redis-operations-on-data-structures-thread-safe)
    REDIS_URI = redis.Redis(connection_pool=pool)

    def into_redis(self, field, value):
        """
        :param field: str
        :param value: str
        :return: None
        """
        # into_redis(): 若field已存在, 就是修改它的值; 如果field不存在, 就是增加这个新的field
        self.REDIS_URI.hset(KEY_NAME, field, value)

    def get_redis_uri(self):
        return self.REDIS_URI

    @classmethod
    def get_redis_host(cls):
        return HOST

    @classmethod
    def get_redis_key_name(cls):
        return KEY_NAME
