#!/usr/bin/env python3
# coding: utf-8
# File: phantomjs_name_comid.py
# Author: lxw
# Date: 6/9/17 4:02 PM

import codecs
import datetime
import requests
import time


class TYCNameComID:
    """
    爬取tianyancha上的Patent和Copyright数据, 这些数据可以直接通过json请求的方式抓取到, 但这些数据需要公司对应的一个ID来索引, 所以需要先抓取这个ID
    """
    def timestamp_to_date(timestamp):
        """ 
        :param timestamp: 待转换的时间戳, 是秒级的, 不能是毫秒级的, 毫秒级的需要是小数
        :return: 
        """
        # Method 1:
        # timestamps = [1496996532.815, 1474300800, 1440086400, 1494415679]
        if timestamp > 1600000000:  # time.time() * 1000
            timestamp = timestamp / 1000.0
        date_array = datetime.datetime.utcfromtimestamp(timestamp)
        date_str = date_array.strftime("%Y-%m-%d %H:%M:%S")
        print(date_str)

    def tianyancha(self):
        """
        not working
        :return: 
        """
        # url = "http://www.tianyancha.com/search?key=中国工商银行股份有限公司&checkFrom=searchBox"
        url = "http://www.tianyancha.com/search?key=%E4%B8%AD%E5%9B%BD%E5%B7%A5%E5%95%86%E9%93%B6%E8%A1%8C%E8%82%A1%E4%BB%BD%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8&checkFrom=searchBox"
        resp = requests.get(url=url)
        with codecs.open("/home/lxw/Desktop/demo.html", "w", encoding="utf-8") as f:
            # f.write(resp.text.encode("utf-8"))
            # f.write(resp.text.encode("utf-8"))
            f.write(resp.text)

    def tianyancha_name_comid(self):
        # url = "http://www.tianyancha.com/v2/search/%E5%8C%97%E4%BA%AC%E7%99%BE%E5%BA%A6%E7%BD%91%E8%AE%AF%E7%A7%91%E6%8A%80%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8.json?"
        # url = "http://www.tianyancha.com/v2/search/中国工商银行.json?"
        url = "http://www.tianyancha.com/v2/search/平安银行股份有限公司.json?"
        # headers = {"User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"}
        headers = {"User-Agent": "js"}
        resp = requests.get(url=url, headers=headers)
        # resp = requests.get(url=url)
        print(resp.text)
        print(resp.headers)

if __name__ == "__main__":
    main()
