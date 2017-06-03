#!/usr/bin/env python3
# coding: utf-8
# File: cnki_patent_spider_wo_scrapy.py
# Author: lxw
# Date: 6/1/17 1:58 PM

from requests import Request
from requests import Session
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time

from Spiders.CNKI_Patent.get_proxy import get_proxy
"""
这种方法没有做出来，主要的问题：
1. 使用cookie伪造，只保留"Cookie": 'ASP.NET_SessionId=zo3yryqlt55ktqni20qac0od; SID_kns=123112; RsPerPage=50;'三个字段即可， 但存在过期的问题
是否能查到需要的数据（随着url切换数据切换）还没有进一步测试
2. 通过网上的获取cookie的方法总是无法请求成功，提示没有找到用户
"""


class CNKIPatentSpider:
    """
    TODO: 要放到本地去解析, 不要直接解析. 直接把源码插入到数据库中,而不是只存储解析之后的数据
    """
    s = Session()
    headers = {
        # "Connection": "keep-alive",
        # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Host": "kns.cnki.net",
        # "Origin": "http://cnki.net",
        # "Pragma": "no-cache",
        # "Referer": "http://cnki.net/",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        # "Cookie": 'ASP.NET_SessionId=zo3yryqlt55ktqni20qac0od; SID_kns=123112; RsPerPage=50;'   # OK
        # "Cookie": "ASP.NET_SessionId=tauzlgdlxbqdx1zx1cmay3fx; SID_kns=123107; RsPerPage=50;"
    }
    proxies = {}
    TIMEOUT = 60

    def get_driver_chrome(self):
        options = webdriver.ChromeOptions()
        ua = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6"
        proxy = get_proxy()
        # NOTE: 这里"http"和"https"一定要都写，不能只写http或者是只写https
        self.proxies["http"] = proxy
        self.proxies["https"] = proxy
        if proxy:
            options.add_argument('--proxy-server=' + proxy)
        driver = webdriver.Chrome(executable_path=r"/home/lxw/Software/chromedirver_selenium/chromedriver", chrome_options=options)
        # 设置超时时间
        driver.set_page_load_timeout(self.TIMEOUT)
        driver.set_script_timeout(self.TIMEOUT)  # 这两种设置都进行才有效
        return driver

    def get_cookie(self):
        driver = self.get_driver_chrome()
        driver.get("http://kns.cnki.net/kns/brief/default_result.aspx")
        cookie_list = driver.get_cookies()
        print(type(cookie_list), cookie_list)
        cookie_str_list = []
        for cookie_dict in cookie_list:
            cookie_str_list.append("{0}={1};".format(cookie_dict["name"], cookie_dict["value"]))
        cookie_str = " ".join(cookie_str_list)
        print("Cookie str:", cookie_str)
        driver.quit()
        return cookie_str

        post_data = {
            "txt_1_sel": "SQR$%=|",
            "txt_1_value1": "万科股份有限公司",
            "txt_1_special1": "%",
            "txt_extension": "xls",
            "expertvalue": "",
            "cjfdcode": "",
            "currentid": "txt_1_value1",
            "dbJson": "coreJson",
            "dbPrefix": "SCDB",
            "db_opt": "SCOD",
            "db_value": "",
            "hidTabChange": "",
            "hidDivIDS": "",
            "singleDB": "SCOD",
            "db_codes": "",
            "singleDBName": "专利",
            "againConfigJson": "false",
            "action": "scdbsearch",
            "ua": "1.11",
        }
        # req = Request("POST", url="http://kns.cnki.net/kns/brief/default_result.aspx", data=post_data, headers=self.headers)
        req = Request("GET", url="http://kns.cnki.net/kns/brief/default_result.aspx", headers=self.headers)
        prepped = self.s.prepare_request(req)

        resp = self.s.send(prepped, proxies=self.proxies)
        # print(resp.text)
        cookie_dict = dict(resp.cookies)
        print("Site cookie:", cookie_dict)
        cookie_str = self.gen_cookie(cookie_dict)
        print("Cookie str:", cookie_str)
        return cookie_str


    def gen_cookie(self, cookie_dict):
        cookie_list = []
        for key, value in cookie_dict.items():
            cookie_list.append("{0}={1};".format(key, value))
        cookie_str = " ".join(cookie_list)
        return cookie_str

    def crawl(self):
        # TODO: RsPerPage看下最大是多少, 至少可以50
        # self.headers["Cookie"] is essential. But the "Cookie" seemed not working(always using the Chromium's cookie(history, and the result has nothing to do with the url below). Why?)
        # self.headers["Cookie"] = 'RsPerPage=50; ASP.NET_SessionId=tauzlgdlxbqdx1zx1cmay3fx; SID_kns=123107;'    # cookie有很大的关系，cookie必须有而且要全，只有这三个可以得到数据，但得到的是历史数据，不是真正请求的数据
        self.headers["Cookie"] = self.get_cookie()
        print("self.headers:", self.headers)

        # url = "http://kns.cnki.net/kns/brief/brief.aspx?pagename=ASP.brief_default_result_aspx&dbPrefix=SCOD&dbCatalog=%E4%B8%AD%E5%9B%BD%E5%AD%A6%E6%9C%AF%E6%96%87%E7%8C%AE%E7%BD%91%E7%BB%9C%E5%87%BA%E7%89%88%E6%80%BB%E5%BA%93&ConfigFile=SCDBINDEX.xml&research=off&t={0}&keyValue=%E4%B8%AD%E5%9B%BD%E5%B7%A5%E5%95%86%E9%93%B6%E8%A1%8C&S=1&queryid=11&skuakuid=11&turnpage=1&recordsperpage=50".format(int(time.time()*1000))    # OK    # 就是curernt_time, 不是增加20分钟
        url = "http://kns.cnki.net/kns/brief/brief.aspx?pagename=ASP.brief_default_result_aspx&dbPrefix=SCOD&dbCatalog=中国学术文献网络出版总库&ConfigFile=SCDBINDEX.xml&research=off&t={0}&keyValue=中国建设银行&S=1&queryid=11&skuakuid=11&turnpage=1&recordsperpage=50".format(int(time.time() * 1000))  # OK
        # url = urllib.parse.quote(url, safe=":/=?&")

        data = {
            "pagename":"ASP.brief_default_result_aspx",
            "dbPrefix":"SCOD",
            "dbCatalog":"中国学术文献网络出版总库",
            "ConfigFile":"SCDBINDEX.xml",
            "research":"off",
            "t": repr(int(time.time()*1000)),
            "keyValue":"刘晓伟",
            "S":"1"
        }

        req = Request("GET", url=url, data=data, headers=self.headers)
        prepped = self.s.prepare_request(req)
        resp = self.s.send(prepped, proxies=self.proxies)
        print("--" * 30)
        print(resp.text)
        print("--" * 30)
        print(resp.request._cookies)    # []
        print(resp.cookies)    # []
        # 平安银行股份有限公司


if __name__ == "__main__":
    spider = CNKIPatentSpider()
    spider.crawl()
    # spider.get_cookie()
