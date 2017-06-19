#!/usr/bin/env python3
# coding: utf-8
# File: CJODocIDSpider_wo_scrapy_new.py
# Author: lxw
# Date: 6/18/17 12:08 AM

"""
PyMongo is thread-safe[Frequently Asked Questions](http://api.mongodb.com/python/current/faq.html)
[Can concurrent processes write to a shared database?](https://stackoverflow.com/questions/30020944/can-concurrent-processes-write-to-a-shared-database)
# NOTE: So long as you make sure to create a separate database connection for each worker process,
# it's perfectly safe to have multiple processes accessing a database at the same time.

Redis:
[how to design multi-process program using redis in python](https://stackoverflow.com/questions/38980000/how-to-design-multi-process-program-using-redis-in-python#)
Each instance of the program should spawn its own ConnectionPool.

*/5 * * * * pg defunct|awk '{print $2}'|xargs kill -9
"""

import multiprocessing
import pymongo
import re
import redis
from selenium import webdriver
import sys
# import time

sys.path.append("/home/lxw/IT/projects/fintech_spider")
sys.path.append("/home/lxw/IT/projects/fintech_spider/Spiders")
sys.path.append("/home/lxw/IT/projects/fintech_spider/Spiders/CJODocIDSpider")

from Spiders.CJODocIDSpider.get_proxy import get_proxy
from Spiders.CJODocIDSpider.utils import generate_logger


class CJODocIDSpider_New():
    """
    w/o Scrapy.
    裁判文书网改版后使用Selenium直接爬取doc_id案件详情信息
    """
    error_logger = generate_logger("new_cjodocid_error")
    proxies = {}
    TIMEOUT = 120
    # headers = {"Host": "wenshu.court.gov.cn"}      # need Host, Referer, User-Agent. the latter two keys will be add below.
    url_prefix = "http://wenshu.court.gov.cn/content/content?DocID="
    js_url_prefix = "http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID="

    # 应该每个进程单独创建ConnectionPool(这儿的只有主进程可以使用)
    pool = redis.ConnectionPool(host="192.168.1.29", port=6379, db=0)
    redis_uri = redis.Redis(connection_pool=pool)
    redis_key = "DOC_ID_HASH"

    def get_chrome_driver(self):
        options = webdriver.ChromeOptions()
        proxy = get_proxy()
        # proxy = "120.26.215.154:3128"
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

    def test_proxy(self):
        driver = self.get_chrome_driver()
        driver.implicitly_wait(30)
        driver.get("http://xiujinniu.com/xiujinniu/index.php")

    def get_doc_id_detail(self, doc_id):
        """
        def get_cookie(self):
        这里直接是通过这个函数获取到网页的源代码, 这个函数可以作为TASKS_HASH的get_cookie()函数
        """
        # print("in get_doc_id_detail().")
        try:
            driver = self.get_chrome_driver()
            if not driver:
                return
            driver.implicitly_wait(60)
            url = self.url_prefix + doc_id
            driver.get(url)
            driver.find_element_by_class_name("content_main")
            url = self.js_url_prefix + doc_id    # 直接访问js_url_prefix + doc_id是不行的，必须得先访问url_prefix + doc_id得到Cookie后再访问js_url_prefix + doc_id
            driver.get(url)
            driver.find_element_by_xpath("/html/body")
            # return driver.page_source
            self.process_page_source(doc_id, driver.page_source)
            driver.quit()
        except Exception as e:
            self.error_logger.error("lxw Exception: {0}\ndocid: {1}\n{2}\n\n".format(e, doc_id, "--"*30))
        """
        cookie_list = driver.get_cookies()
        cookie_str_list = []
        for cookie_dict in cookie_list:
            cookie_str_list.append("{0}={1};".format(cookie_dict["name"], cookie_dict["value"]))
        cookie_str = " ".join(cookie_str_list)
        print("Cookie str:", cookie_str)
        time.sleep(3)
        driver.quit()
        return cookie_str
        """

    def process_page_source(self, doc_id, page_source):
        # print("in process_page_source().")
        if "<title>502</title>" in page_source:
            return
        elif "remind" in page_source:
            return

        try:
            json_data = ""
            match_result = re.finditer(r"jsonHtmlData.*?jsonData", page_source, re.S)
            for m in match_result:
                data = m.group(0)
                right_index = data.rfind("}")
                left_index = data.find("{")
                json_data = data[left_index + 1:right_index]
                break  # this is essential. Only the first match is what we want.
            if json_data == "":
                self.error_logger.error("doc_id: {0}. re.finditer() got nothing. page_source: {1}\n{2}\n\n".format(doc_id, page_source, "--"*30))
            else:   # Success
                case_details_json = "\"{" + json_data + "}\""
                cjo_docid_dict = {}
                cjo_docid_dict["doc_id"] = doc_id
                cjo_docid_dict["case_details_json"] = case_details_json
                self.into_mongo(cjo_docid_dict)
                # 每个进程单独创建ConnectionPool
                pool_process = redis.ConnectionPool(host="192.168.1.29", port=6379, db=0)
                redis_uri_process = redis.Redis(connection_pool=pool_process)
                redis_key_process = "DOC_ID_HASH"
                # redis_uri_process.hset(redis_key_process, doc_id, "-1")  # Success 只有成功是需要设置的，不成功的不需要设置
        except Exception as e:
            self.error_logger.error("lxw_Exception_NOTE: {0}. page_source: {1}\n{2}\n\n".format(e, page_source, "--"*30))

    def into_mongo(self, data_dict):
        print("data_dict:", data_dict)
        conn = pymongo.MongoClient("192.168.1.36", 27017)
        db = conn.scrapy    # dbname: scrapy
        db["cjo_docid_0618"].insert(data_dict)

    def operate(self):
        count = 0
        continue_flag = True
        while continue_flag:
            continue_flag = False
            pool = multiprocessing.Pool(processes=6)    # IP代理数目是6, 所以这里把进程数目也设置为6
            for item in self.redis_uri.hscan_iter(self.redis_key):
                # print(type(item), item)    # <class 'tuple'> (b'd6613396-b7d1-4199-ae4e-b3b36fdd7fda', b'0')
                doc_id = item[0].decode("utf-8")
                flag = int(item[1].decode("utf-8"))  # {0: initial value;    -1: Done;    >0: timestamp}

                if flag != -1:    # 没有执行成功
                    continue_flag = True
                    pool.apply_async(self.get_doc_id_detail, (doc_id,))

            pool.close()
            pool.join()
            print("第{0}轮执行完成.".format(count))
            count += 1

if __name__ == "__main__":
    cjo_docid = CJODocIDSpider_New()
    # cjo_docid.get_doc_id_detail()
    # cjo_docid.test_proxy()
    cjo_docid.operate()
