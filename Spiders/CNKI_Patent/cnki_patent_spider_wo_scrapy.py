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
1. 必须先获取Cookie, 然后才能查询(获取Cookie的url是http://kns.cnki.net/kns/request/SearchHandler.ashx)
"""


class CNKIPatentSpider:
    """
    TODO: 要放到本地去解析, 不要直接解析. 直接把源码写入到文件中,而不是只存储解析之后的数据
    """
    s = Session()
    headers = {
        "Host": "kns.cnki.net",
        "Referer": "http://kns.cnki.net/kns/brief/default_result.aspx",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6"
    }
    proxies = {}
    TIMEOUT = 60

    def get_driver_chrome(self):
        options = webdriver.ChromeOptions()
        # ua = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6"
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

    def get_cookie_by_selenium(self):
        company_name = "百度在线网络技术"
        # company_name = "中国工商银行"
        driver = self.get_driver_chrome()
        """
        # 这个url请求没有必要
        driver.get("http://kns.cnki.net/kns/brief/default_result.aspx")
        cookie_list = driver.get_cookies()        
        cookie_str_list = []
        for cookie_dict in cookie_list:
            cookie_str_list.append("{0}={1};".format(cookie_dict["name"], cookie_dict["value"]))
        cookie_str = " ".join(cookie_str_list)
        print("Cookie str:", cookie_str)
        """
        # 这个url请求不可缺少, 否则会出现"对不起，服务器上不存在此用户！可能已经被剔除或参数错误"
        time_str = time.strftime("%c", time.localtime())
        time_list = time_str.split()  # ['Mon', 'Jun', '5', '10:29:33', '2017']
        time_param = "{0} {1} {2:02} {3} {4} GMT+0800 (CST)".format(time_list[0], time_list[1], int(time_list[2]),
                                                                    time_list[4], time_list[3])
        url = "http://kns.cnki.net/kns/request/SearchHandler.ashx?action=&NaviCode=*&ua=1.11&PageName=ASP.brief_default_result_aspx&DbPrefix=SCOD&DbCatalog=中国学术文献网络出版总库&ConfigFile=SCDBINDEX.xml&db_opt=SCOD&txt_1_sel=SQR$=|&txt_1_value1={0}&txt_1_special1=%&his=0&parentdb=SCDB&__={1}".format(company_name, time_param)
        driver.get(url)
        cookie_list = driver.get_cookies()
        cookie_str_list = []
        for cookie_dict in cookie_list:
            cookie_str_list.append("{0}={1};".format(cookie_dict["name"], cookie_dict["value"]))
        cookie_str = " ".join(cookie_str_list)
        print("Cookie str:", cookie_str)

        """        
        url = "http://kns.cnki.net/kns/brief/brief.aspx?pagename=ASP.brief_default_result_aspx&dbPrefix=SCOD&dbCatalog=中国学术文献网络出版总库&ConfigFile=SCDBINDEX.xml&research=off&t={0}&keyValue={1}&S=1&queryid=11&skuakuid=11&turnpage=1&recordsperpage=50".format(
            int(time.time() * 1000), company_name)  # OK
        driver.get(url)
        cookie_list = driver.get_cookies()
        cookie_str_list = []
        for cookie_dict in cookie_list:
            cookie_str_list.append("{0}={1};".format(cookie_dict["name"], cookie_dict["value"]))
        cookie_str = " ".join(cookie_str_list)
        print("Cookie str:", cookie_str)
        print(driver.page_source)
        """
        driver.quit()
        return cookie_str

    def get_cookie_by_requests(self):
        """
        原理主要看get_cookie_by_selenium(), get_cookie_by_requests()是根据get_cookie_by_selenium()改出来的
        """
        company_name = "中国互联网络信息中心"    # 83
        # company_name = "百度在线网络技术"
        # company_name = "中国工商银行"

        # 这个url请求不可缺少, 否则会出现"对不起，服务器上不存在此用户！可能已经被剔除或参数错误"
        time_str = time.strftime("%c", time.localtime())
        time_list = time_str.split()  # ['Mon', 'Jun', '5', '10:29:33', '2017']
        time_param = "{0} {1} {2:02} {3} {4} GMT+0800 (CST)".format(time_list[0], time_list[1], int(time_list[2]),
                                                                    time_list[4], time_list[3])
        url = "http://kns.cnki.net/kns/request/SearchHandler.ashx?action=&NaviCode=*&ua=1.11&PageName=ASP.brief_default_result_aspx&DbPrefix=SCOD&DbCatalog=中国学术文献网络出版总库&ConfigFile=SCDBINDEX.xml&db_opt=SCOD&txt_1_sel=SQR$=|&txt_1_value1={0}&txt_1_special1=%&his=0&parentdb=SCDB&__={1}".format(company_name, time_param)

        proxy = get_proxy()
        self.proxies["http"] = proxy
        self.proxies["https"] = proxy
        req = Request("GET", url=url, headers=self.headers)
        prepped = self.s.prepare_request(req)
        if proxy:
            resp = self.s.send(prepped, proxies=self.proxies)
        else:
            # resp = self.s.send(prepped)
            # 必须得用代理, 否则IP会被封, 所以必须用代理去请求
            print("No Proxy Available. Program Exits.")
            exit(0)

        return self.gen_cookie(dict(resp.cookies))

    def gen_cookie(self, cookie_dict):
        cookie_list = []
        for key, value in cookie_dict.items():
            cookie_list.append("{0}={1};".format(key, value))
        cookie_str = " ".join(cookie_list)
        return cookie_str

    def crawl(self):
        """
        NOTE:
            1. self.headers["Cookie"]必须要设置, 否则就会提示"对不起，服务器上不存在此用户！可能已经被剔除或参数错误"
            2. 无论url怎么设置都无所谓, 完全按照self.headers["Cookie"]的值返回结果
        """
        # self.headers["Cookie"] = self.get_cookie_by_selenium()
        self.headers["Cookie"] = self.get_cookie_by_requests()
        company_name = "中国工商银行"    # url中的company_name其实没有必要, 完全通过cookie中的值得到查询结果
        timestamp = int(time.time() * 1000)    # url中的timestamp其实没有必要, 完全通过cookie中的值得到查询结果
        # url = "http://kns.cnki.net/kns/brief/brief.aspx?pagename=ASP.brief_default_result_aspx&dbPrefix=SCOD&dbCatalog=%E4%B8%AD%E5%9B%BD%E5%AD%A6%E6%9C%AF%E6%96%87%E7%8C%AE%E7%BD%91%E7%BB%9C%E5%87%BA%E7%89%88%E6%80%BB%E5%BA%93&ConfigFile=SCDBINDEX.xml&research=off&t={0}&keyValue=%E4%B8%AD%E5%9B%BD%E5%B7%A5%E5%95%86%E9%93%B6%E8%A1%8C&S=1&queryid=11&skuakuid=11&turnpage=1&recordsperpage=50".format(timestamp)    # OK    # 就是curernt_time, 不是增加20分钟
        # url = "http://kns.cnki.net/kns/brief/brief.aspx"    # NO.  NOTE: 与url中具体的参数无关, 但必须有这些参数
        # url中的RsPerPage最大是50, 不能再多了
        url = "http://kns.cnki.net/kns/brief/brief.aspx?pagename=ASP.brief_default_result_aspx&dbPrefix=SCOD&dbCatalog=中国学术文献网络出版总库&ConfigFile=SCDBINDEX.xml&research=off&t={0}&keyValue={1}&S=1&queryid=11&skuakuid=11&turnpage=1&recordsperpage=50".format(timestamp, company_name)  # OK
        """
        # NOTE: 没有必要, 完全使用headers中的cookie
        data = {
            "pagename":"ASP.brief_default_result_aspx",
            "dbPrefix":"SCOD",
            "dbCatalog":"中国学术文献网络出版总库",
            "ConfigFile":"SCDBINDEX.xml",
            "research":"off",
            "t": repr(timestamp),
            "keyValue":"平安银行股份有限公司",
            "S":"1"
        }
        """
        req = Request("GET", url=url, headers=self.headers)
        prepped = self.s.prepare_request(req)
        # resp = self.s.send(prepped, proxies=self.proxies)    # TODO: 这里连proxies也可以不用, 但是否会封我们的IP?  先不用看是否会被封(先不用代理), 如果被封了再加上代理, 感觉应该不会被封, 应该是按照Cookie去反爬的, Cookie中携带着IP信息
        resp = self.s.send(prepped)
        print("\n", "----" * 30)
        print("----" * 30, "\n")
        print(resp.text)


if __name__ == "__main__":
    spider = CNKIPatentSpider()
    spider.crawl()
    # spider.get_cookie_by_selenium()
    # spider.get_cookie_by_requests()
