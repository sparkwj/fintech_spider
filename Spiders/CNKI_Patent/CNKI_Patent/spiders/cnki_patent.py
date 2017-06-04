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
    # url = 'http://www.cnki.net/'
    # url = "http://www.ip138.com/ua.asp"    # 查看当前请求的User-Agent和所使用的IP
    url = "http://xiujinniu.com/xiujinniu/index.php"
    # url = "http://kns.cnki.net/kns/brief/brief.aspx?pagename=ASP.brief_default_result_aspx&dbPrefix=SCOD&dbCatalog=%e4%b8%ad%e5%9b%bd%e5%ad%a6%e6%9c%af%e6%96%87%e7%8c%ae%e7%bd%91%e7%bb%9c%e5%87%ba%e7%89%88%e6%80%bb%e5%ba%93&ConfigFile=SCDBINDEX.xml&research=off&t={0}&keyValue=%E5%B9%B3%E5%AE%89%E9%93%B6%E8%A1%8C%E8%82%A1%E4%BB%BD%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8&S=1".format(current_time)
    # url = "http://kns.cnki.net/kns/brief/default_result.aspx"   # No
    # url = "http://kns.cnki.net/kns/brief/default_result.aspx"

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse, method="GET")

    def parse(self, response):
        print(response.text)
        # self.check_user_agent_proxy(response)

    def check_user_agent_proxy(self, response):
        tbody_list = response.xpath('//table')
        print(type(tbody_list), tbody_list)
        trs = tbody_list[2]
        td_list = trs.xpath('./tbody/tr/td')
        for td in td_list:
            print(td.xpath("string(.)").extract_first().replace("\n", " ").replace("  ", ""))
