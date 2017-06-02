#!/usr/bin/env python3
# coding: utf-8
# File: cnki_patent_spider_wo_scrapy.py
# Author: lxw
# Date: 6/1/17 1:58 PM

import requests
import selenium
import time
from Spiders.CNKI_Patent.get_proxy import get_proxy


class CNKIPatentSpider:
    """
    要放到本地去解析, 不要直接解析. 直接把源码插入到数据库中,而不是只存储解析之后的数据
    """
    s = requests.Session()
    headers = {
        "Connection": "keep-alive",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Host": "kns.cnki.net",
        "Origin": "http://cnki.net",
        "Pragma": "no-cache",
        "Referer": "http://cnki.net/",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        # "Cookie": 'ASP.NET_SessionId=zo3yryqlt55ktqni20qac0od; SID_kns=123112; RsPerPage=50;'   # OK
        # "Cookie": "ASP.NET_SessionId=tauzlgdlxbqdx1zx1cmay3fx; SID_kns=123107; RsPerPage=50;"
    }
    proxies = {}

    def get_cookie(self):
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
        resp = requests.post(url="http://kns.cnki.net/kns/brief/default_result.aspx", data=post_data, headers=self.headers)
        # print(resp.text)
        cookie_dict = dict(resp.cookies)
        print("Site cookie:", cookie_dict)
        # cookie = "ASP.NET_SessionId={0}; SID_kns={1}; RsPerPage=50;".format(cookie["ASP.NET_SessionId"], cookie["SID_kns"])
        # print("Forged cookie:", cookie)
        del cookie_dict["Ecp_LoginStuts"]
        cookie_str = self.gen_cookie(cookie_dict)
        print("Cookie str:", cookie_str)
        return cookie_str
        prepped = self.s.prepare_request(req)
        proxy = get_proxy()
        # NOTE: 这里"http"和"https"一定要都写，不能只写http或者是只写https
        self.proxies["http"] = proxy
        self.proxies["https"] = proxy
        resp = self.s.send(prepped, proxies=self.proxies)
        # print(resp.text)
        cookie = dict(resp.cookies)
        print("Site cookie:", cookie)
        cookie = "ASP.NET_SessionId={0}; SID_kns={1}; RsPerPage=50;".format(cookie["ASP.NET_SessionId"], cookie["SID_kns"])
        print("Forged cookie:", cookie)
        return cookie

    def gen_cookie(self, cookie_dict):
        """
        根据cookiejar对象生成cookie字符串
        cookiejar:cookielib.CookieJar()对象
        additional:附加的用于生成cookie字符串的键值对字典
        """
        cookie_list = []
        for key, value in cookie_dict.items():
            cookie_list.append("{0}={1};".format(key, value))

        cookie_str = " ".join(cookie_list)
        return cookie_str

    def crawl(self):
        # TODO: RsPerPage看下最大是多少, 至少可以50
        # self.headers["Cookie"] = self.get_cookie()
        self.headers["Cookie"] = 'RsPerPage=50; ASP.NET_SessionId=tauzlgdlxbqdx1zx1cmay3fx; SID_kns=123107;'
        self.headers["Referer"] = "http://kns.cnki.net/kns/brief/default_result.aspx"
        del self.headers["Origin"]
        print(self.headers)
        # url = "http://kns.cnki.net/kns/brief/brief.aspx?pagename=ASP.brief_default_result_aspx&dbPrefix=SCOD&dbCatalog=%E4%B8%AD%E5%9B%BD%E5%AD%A6%E6%9C%AF%E6%96%87%E7%8C%AE%E7%BD%91%E7%BB%9C%E5%87%BA%E7%89%88%E6%80%BB%E5%BA%93&ConfigFile=SCDBINDEX.xml&research=off&t={0}&keyValue=%E4%B8%AD%E5%9B%BD%E5%B7%A5%E5%95%86%E9%93%B6%E8%A1%8C&S=1&queryid=11&skuakuid=11&turnpage=1&recordsperpage=50".format(int(time.time()*1000))    # OK    # 就是curernt_time, 不是增加20分钟
        url = "http://kns.cnki.net/kns/brief/brief.aspx?pagename=ASP.brief_default_result_aspx&dbPrefix=SCOD&dbCatalog=中国学术文献网络出版总库&ConfigFile=SCDBINDEX.xml&research=off&t={0}&keyValue=中国建设银行&S=1&queryid=11&skuakuid=11&turnpage=1&recordsperpage=50".format(int(time.time() * 1000))  # OK
        # url = urllib.parse.quote(url, safe=":/=?&")
        print(url)
        req = requests.Request("GET", url=url, headers=self.headers)
        prepped = self.s.prepare_request(req)
        resp = self.s.send(prepped, proxies=self.proxies)
        print("--" * 30)
        print(resp.text)
        print("--" * 30)
        print(resp.request._cookies)    # []  why?
        # 平安银行股份有限公司


if __name__ == "__main__":
    spider = CNKIPatentSpider()
    spider.crawl()
    # spider.get_cookie()



