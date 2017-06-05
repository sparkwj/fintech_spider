#!/usr/bin/env python3
# coding: utf-8
# File: cnki_patent.py
# Author: lxw
# Date: 5/26/17 4:03 PM

import scrapy
import time


class CnkiPatentSpider(scrapy.Spider):
    name = "cnki_patent"
    current_time = int(time.time() * 1000)
    url = "http://xiujinniu.com/xiujinniu/index.php"    # 测试User-Agent和IP代理是否可用

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse, method="GET")

    def parse(self, response):
        print(response.text)
        # self.check_user_agent_proxy(response)
