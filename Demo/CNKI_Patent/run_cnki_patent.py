#!/usr/bin/env python3
# coding: utf-8
# File: run_cnki_patent.py
# Author: lxw
# Date: 5/26/17 4:06 PM

# Supporting:
# 0. PhantomJS/Selenium # 默认不使用PhantomJS, 注释掉了, 如果使用需要在middlewares中让注释掉的内容生效, 并且禁用ProxyMiddleware(Selenium使用代理的方式与不使用Selenium不一样)
# 1. User-Agent
# 2. IP Proxy(Redis)


from scrapy import cmdline
import sys

sys.path.append("/home/lxw/IT/projects/fintech_spider")
sys.path.append("/home/lxw/IT/projects/fintech_spider/Spiders/CNKI_Patent")

cmdline.execute("scrapy crawl cnki_patent -L WARNING".split())

# redis-cli -h 192.168.1.29
# mongo 192.168.1.36:27017