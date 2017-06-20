#!/usr/bin/env python3
# coding: utf-8
# File: CJOSpider_wo_scrapy_new.py
# Author: lxw
# Date: 6/18/17 10:05 PM

"""
PyMongo is thread-safe[Frequently Asked Questions](http://api.mongodb.com/python/current/faq.html)
[Can concurrent processes write to a shared database?](https://stackoverflow.com/questions/30020944/can-concurrent-processes-write-to-a-shared-database)
# NOTE: So long as you make sure to create a separate database connection for each worker process,
# it's perfectly safe to have multiple processes accessing a database at the same time.

Redis:
[how to design multi-process program using redis in python](https://stackoverflow.com/questions/38980000/how-to-design-multi-process-program-using-redis-in-python#)
Each instance of the program should spawn its own ConnectionPool.

返回的结果有可能是：
1. 正确值
2. 空白
3. 乱码js

1. 比较短的案例：
"4a5c7734-fbb6-447b-a036-02191d3ee2b7",
"27241ed4-619d-4d0e-a18c-a74500f0e6ca",
"d6a12c3c-cdb5-4147-8fc3-a74500f0e6eb",
"1c83095f-396a-442c-831b-a74500f0e6ae",
"5b19caf4-3858-4796-b241-a74500f0e702",
【下面的不短】
"1a6ebb9e-f279-4cc4-a989-a74500b820bb",
"28f1ce2b-269f-430e-bd4e-a75100f915de",
"29c6d854-14f9-492f-ae6c-a74500b82091",
"5365d386-e69b-4af9-9c21-a75100f912d5",
"a72c6c87-d7ef-44a7-b5d1-a75100f91467"
"""

import json
import multiprocessing
import os
import pymongo
import random
import re
import redis
import requests
from selenium import webdriver
import sys
# import time

abspath = os.path.abspath(__file__)
current_dir = os.path.dirname(abspath)
# print("current_dir:", current_dir)
parent_dir = os.path.dirname(current_dir)
# print("parent_dir:", parent_dir)
grand_dir = os.path.dirname(parent_dir)
# print("grand_dir:", grand_dir)
# sys.path.append("/home/lxw/IT/projects/fintech_spider")
# sys.path.append("/home/lxw/IT/projects/fintech_spider/Spiders")
# sys.path.append("/home/lxw/IT/projects/fintech_spider/Spiders/CJODocIDSpider")
sys.path.append(grand_dir)
sys.path.append(parent_dir)
sys.path.append(current_dir)

from Spiders.CJOSpider.get_proxy import get_proxy
from Spiders.CJOSpider.utils import generate_logger


class CJOSpider_New():
    """
    w/o Scrapy.
    裁判文书网改版后，爬取策略无法直接使用
    Selenium直接爬取doc_id案件详情信息
    """
    error_logger = generate_logger("new_cjo_error")
    proxies = {}
    TIMEOUT = 120
    # headers = {"Host": "wenshu.court.gov.cn"}      # need Host, Referer, User-Agent. the latter two keys will be add below.
    url_prefix = "http://wenshu.court.gov.cn/content/content?DocID="

    # 应该每个进程单独创建ConnectionPool(这儿的只有主进程可以使用)
    pool = redis.ConnectionPool(host="192.168.1.29", port=6379, db=0)
    redis_uri = redis.Redis(connection_pool=pool)
    redis_key = "TASKS_HASH"

    doc_id_list = [
        "4a5c7734-fbb6-447b-a036-02191d3ee2b7", "27241ed4-619d-4d0e-a18c-a74500f0e6ca", "d6a12c3c-cdb5-4147-8fc3-a74500f0e6eb",
        "1c83095f-396a-442c-831b-a74500f0e6ae", "5b19caf4-3858-4796-b241-a74500f0e702"
    ]

    cases_per_page = 20

    def get_chrome_driver(self):
        # chromedriver
        options = webdriver.ChromeOptions()
        proxy = get_proxy()
        # NOTE: 这里"http"和"https"一定要都写，不能只写http或者是只写https
        self.proxies["http"] = proxy
        self.proxies["https"] = proxy
        if proxy:
            options.add_argument('--proxy-server=' + proxy)
        else:
            return None    # proxy is essential
        driver = webdriver.Chrome(executable_path=r"/home/lxw/Software/chromedriver_selenium/chromedriver", chrome_options=options)

        # 设置超时时间
        driver.set_page_load_timeout(self.TIMEOUT)
        driver.set_script_timeout(self.TIMEOUT)  # 这两种设置都进行才有效
        return driver

    def get_cookie_by_selenium(self):
        driver = self.get_chrome_driver()
        driver.implicitly_wait(60)
        driver.get(self.url_prefix + random.choice(self.doc_id_list))
        driver.find_element_by_class_name("content_main")
        cookie_list = driver.get_cookies()
        cookie_str_list = []
        for cookie_dict in cookie_list:
            cookie_str_list.append("{0}={1};".format(cookie_dict["name"], cookie_dict["value"]))
        cookie_str = " ".join(cookie_str_list)
        print("Cookie str:", cookie_str)
        driver.quit()
        return cookie_str

    def test_proxy(self):
        driver = self.get_chrome_driver()
        driver.implicitly_wait(30)
        driver.get("http://xiujinniu.com/xiujinniu/index.php")
        print(driver.page_source)

    def into_mongo(self, data_dict):
        print("data_dict:", data_dict)
        conn = pymongo.MongoClient("192.168.1.36", 27017)
        db = conn.scrapy    # dbname: scrapy
        db["cjo0620"].insert(data_dict)

    def crawl_basic_info(self, cookie_str):
        if not cookie_str:
            return
        url = "http://wenshu.court.gov.cn/List/ListContent"
        data = {
            # "Param": "案件类型:刑事案件,裁判日期:2017-04-01 TO 2017-04-01,法院层级:高级法院", # OK
            "Param": "案件类型:刑事案件",   # OK: 4875654
            # "Param": "裁判日期:1996-01-10 TO 1996-01-10",# "1996-01-10": 1, "1996-02-07": 1
            "Index": 1,   # NOTE: 还是只能爬取前100页的数据, 超过100页的爬取不到
            "Page": self.cases_per_page,
            "Order": "法院层级",
            "Direction": "asc",
        }

        s = requests.Session()

        try:
            headers = {
                "Host": "wenshu.court.gov.cn",
                "Referer": "http://wenshu.court.gov.cn/List/List",
                "Cookie": cookie_str
            }
            # print("headers", headers)
            req = requests.Request("POST", url=url, data=data, headers=headers)
            prepped = s.prepare_request(req)
            proxy = get_proxy()
            proxies = {
                "http": proxy,
                "https": proxy,
            }
            response = s.send(prepped, proxies=proxies, timeout=60)
            # response = s.send(prepped, timeout=60)    # NOTE: 没有使用代理(或者是使用其他的代理)，都可以通过Cookie直接爬取，这就意味着反爬信息完全依赖Cookie来实现
        except Exception as e:
            print("lxw_Exception", e)
        else:
            print(response.text)

    def crawl_by_post(self, cookie_str, param, index, code, category):
        """
        :param param: "POST" parameters
        :param index: page number (MUST BE INTEGER)
        :param code: company code
        :param category: abbr_single/abbr/full (abbr_single: 简称in全称; abbr: 使用简称; full: 使用全称)
        # :param flag_code: flag_code to be transported to middlewares.
        :return: 
        """
        if not cookie_str:
            return
        post_data = {
            # "Param": "案件类型:刑事案件,法院层级:高级法院",
            "Param": param,
            "Index": repr(index),
            "Page": repr(self.cases_per_page),
            "Order": "法院层级",
            "Direction": "asc",
        }

        url = "http://wenshu.court.gov.cn/List/ListContent"
        data = {
            # "Param": "案件类型:刑事案件,裁判日期:2017-04-01 TO 2017-04-01,法院层级:高级法院", # OK
            "Param": "案件类型:刑事案件",   # OK: 4875654
            # "Param": "裁判日期:1996-01-10 TO 1996-01-10",# "1996-01-10": 1, "1996-02-07": 1
            "Index": 1,   # NOTE: 还是只能爬取前100页的数据, 超过100页的爬取不到
            "Page": self.cases_per_page,
            "Order": "法院层级",
            "Direction": "asc",
        }

        s = requests.Session()

        try:
            headers = {
                "Host": "wenshu.court.gov.cn",
                "Referer": "http://wenshu.court.gov.cn/List/List",
                "Cookie": cookie_str
            }
            # print("headers", headers)
            req = requests.Request("POST", url=url, data=data, headers=headers)
            prepped = s.prepare_request(req)
            proxy = get_proxy()
            proxies = {
                "http": proxy,
                "https": proxy,
            }
            response = s.send(prepped, proxies=proxies, timeout=60)
            # response = s.send(prepped, timeout=60)    # NOTE: 没有使用代理(或者是使用其他的代理)，都可以通过Cookie直接爬取，这就意味着反爬信息完全依赖Cookie来实现
        except Exception as e:
            print("lxw_Exception", e)
        else:
            print(response.text)
        return

    def operate(self):
        count = 0
        continue_flag = True
        while continue_flag:
            continue_flag = False
            pool = multiprocessing.Pool(processes=1)    # TODO: IP代理数目是6, 所以这里把进程数目也设置为6
            for item in self.redis_uri.hscan_iter(self.redis_key):
                print(type(item), item)    # <class 'tuple'> (b'{"Param": "\\u5f53\\u4e8b\\u4eba:\\u5927\\u667a\\u6167", "Index": "1", "case_parties": "601519", "abbr_full_category": "abbr_single"}', b'0')
                left_right = item[1].decode("utf-8").split("_")
                flag_code = int(left_right[0])  # we only care about left_right[0]
                if flag_code >= 0:    # 未请求或未请求成功    # {0: 初始值, 未爬取;    负值: 爬取成功;    > 0: 未爬取成功, 爬取的次数;}
                    continue_flag = True
                    data_dict_str = item[0].decode("utf-8")
                    data_dict = json.loads(data_dict_str)
                    yield self.yield_formrequest(data_dict["Param"], int(data_dict["Index"]), data_dict["case_parties"], data_dict["abbr_full_category"], flag_code)
                    # TODO: pool.apply_async(self.get_doc_id_detail, (doc_id,))

            pool.close()
            pool.join()
            print("第{0}轮执行完成.".format(count))
            count += 1


if __name__ == "__main__":
    cjo = CJOSpider_New()
    # cjo.operate()


