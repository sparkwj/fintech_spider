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

import calendar
import datetime
from fake_useragent import UserAgent
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
import time

abspath = os.path.abspath(__file__)
current_dir = os.path.dirname(abspath)
parent_dir = os.path.dirname(current_dir)
grand_dir = os.path.dirname(parent_dir)
# sys.path.append("/home/lxw/IT/projects/fintech_spider")
# sys.path.append("/home/lxw/IT/projects/fintech_spider/Spiders")
# sys.path.append("/home/lxw/IT/projects/fintech_spider/Spiders/CJODocIDSpider")
sys.path.append(grand_dir)
sys.path.append(parent_dir)
sys.path.append(current_dir)

from Spiders.CJOSpider.get_proxy import get_proxy
from Spiders.CJOSpider.utils import generate_logger
from Spiders.CJOSpider.utils import generate_output_logger


class CJOSpider_New():
    """
    w/o Scrapy.
    裁判文书网改版后，原有的爬取策略无法继续使用(必须使用Cookie和代理： 没有Cookie无法爬取； 没有代理非常容易被封，不再是输入验证码可以解封的)
    1. Selenium爬取doc_id案件详情信息, 只是为了获取Cookie
    2. 使用Cookie信息，构建POST请求抓取数据
    """
    error_logger = generate_logger("new_cjo_error")
    exceed_crawl_limit_logger = generate_output_logger("new_CJOSpiderExceedCrawlLimit")
    proxies = {}
    TIMEOUT = 120
    url_prefix = "http://wenshu.court.gov.cn/content/content?DocID="
    url = "http://wenshu.court.gov.cn/List/ListContent"

    # 应该每个进程单独创建ConnectionPool(这儿的只有主进程可以使用)
    pool = redis.ConnectionPool(host="192.168.1.29", port=6379, db=0)
    redis_uri = redis.Redis(connection_pool=pool)
    redis_key = "TASKS_HASH"

    doc_id_list = [
        "4a5c7734-fbb6-447b-a036-02191d3ee2b7", "27241ed4-619d-4d0e-a18c-a74500f0e6ca", "d6a12c3c-cdb5-4147-8fc3-a74500f0e6eb",
        "1c83095f-396a-442c-831b-a74500f0e6ae", "5b19caf4-3858-4796-b241-a74500f0e702"
    ]

    ua = UserAgent()

    cases_per_page = 20
    CRAWL_LIMIT = 2000  # 2000  裁判文书网以POST请求的方式最多允许爬取100页（每页最多20条）；如果直接请求网页，最多请求25页（每页最多20条）
    CASE_CATEGORY = ["刑事案件", "民事案件", "行政案件", "赔偿案件", "执行案件"]    # 案件类型
    COURT_CATEGORY = ["最高法院", "高级法院", "中级法院", "基层法院"]   # 法院层级
    # filter according to DATE: 按照"日期"(每年/每月/每天)进行过滤("当事人"+"案件类型"+"法院层级"+"日期")
    # 每年: 裁判年份:2017    每月/每天: 裁判日期:2017-05-01 TO 2017-05-31/裁判日期:2017-05-01 TO 2017-05-01
    DOC_CATEGORY = ["判决书", "裁定书", "调解书", "决定书", "通知书", "批复", "答复", "函", "令", "其他"]  # 文书类型
    JUDGE_PROCEDURE = ["一审", "二审", "再审", "复核", "刑罚变更", "再审审查与审判监督", "其他"]   # 审判程序

    DIGIT_DICT = {1: "01", 2: "02", 3: "03", 4: "04", 5: "05", 6: "06", 7: "07", 8: "08", 9: "09"}  # 月份, 只处理单个的数字即可

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
        # NOTE: 这儿的try...except...finally 是必须的，否则一旦这儿出错或者发生超时，都会导致浏览器窗口无法关闭（还得写crontab去定期杀掉defunct的chromium）
        driver = None
        try:
            driver = self.get_chrome_driver()
            if not driver:
                return ""
            driver.implicitly_wait(60)
            driver.get(self.url_prefix + random.choice(self.doc_id_list))
            driver.find_element_by_class_name("content_main")
            cookie_list = driver.get_cookies()
            cookie_str_list = []
            for cookie_dict in cookie_list:
                cookie_str_list.append("{0}={1};".format(cookie_dict["name"], cookie_dict["value"]))
            cookie_str = " ".join(cookie_str_list)
            print("Cookie str:", cookie_str)
        except Exception as e:
            self.error_logger.error("lxw get_cookie_by_selenium Exception: {0}\n{1}\n\n".format(e, "--"*30))
            return ""
        else:
            return cookie_str
        finally:
            if driver:
                driver.quit()

    # def crawl_basic_info(self, cookie_str):
    def crawl_by_post(self, cookie_str, param, index):
        """
        :param cookie_str: the cookie string
        :param param: "POST" parameters
        :param index: page number (MUST BE INTEGER)
        :return:  ""(Error) or response.text(OK)
        """
        if not cookie_str:
            return ""
        post_data = {
            # "Param": "案件类型:刑事案件,法院层级:高级法院",
            "Param": param,
            "Index": index,
            "Page": self.cases_per_page,
            "Order": "法院层级",
            "Direction": "asc",
        }
        headers = {
            "Host": "wenshu.court.gov.cn",
            "Referer": "http://wenshu.court.gov.cn/List/List",
            "Cookie": cookie_str,
            "User-Agent": self.ua.random
        }
        # print("headers:", headers)
        s = requests.Session()
        try:
            req = requests.Request("POST", url=self.url, data=post_data, headers=headers)
            prepped = s.prepare_request(req)
            proxy = get_proxy()
            proxies = {
                "http": proxy,
                "https": proxy,
            }
            response = s.send(prepped, proxies=proxies, timeout=60)
            # response = s.send(prepped, timeout=60)    # NOTE: 没有使用代理(或者是使用其他的代理)，都可以通过Cookie直接爬取，这就意味着反爬信息完全依赖Cookie来实现
        except Exception as e:
            self.error_logger.error("lxw Exception: {0}\nparam: {1}\n{2}\n\n".format(e, param, "--"*30))
            return ""
        else:
            return response.text

    def test_proxy(self):
        driver = self.get_chrome_driver()
        driver.implicitly_wait(30)
        driver.get("http://xiujinniu.com/xiujinniu/index.php")
        print(driver.page_source)

    def process_response(self, text, data):
        """
        :param text: response.text. a json string.
        :param data: data is a dict which is used to set/get fileds in redis.
        """
        # 每个进程单独创建ConnectionPool
        pool_process = redis.ConnectionPool(host="192.168.1.29", port=6379, db=0)
        redis_uri_process = redis.Redis(connection_pool=pool_process)
        redis_key_process = "TASKS_HASH"
        # redis_uri_process.hset(redis_key_process, name, "0_0")    # left_right. Only care about "left".
        try:
            text_str = json.loads(text)
            text_list = json.loads(text_str)  # json.loads() twice, don't know why.
            # text_list: [{'Count': '0'}] or [{'Count': '1'},{'裁判要旨段原文': '本院认为，被告人王某为他人吸食毒品提供场所，其行为已构成容留他人吸毒罪，依法应予惩处。泰兴市人民检察院对被告人王某犯容留他人吸毒罪的指控成立，本院予以支持。被告人王某自动投案并如实供述自己的罪行，是自首，依法可以从轻处罚。被告人王某具有犯罪前科和多次吸毒劣迹，可酌情从重处罚。被告人王某主动向本院缴纳财产刑执行保证金，可酌情从轻处罚。关于辩护人提出“被告人王某具有自首、主动缴纳财产刑执行保证金等法定和酌定从轻处罚的情节，建议对被告人王某从轻处罚”的辩护意见，经查属实，本院予以采纳。依照《中华人民共和国刑法》第三百五十四条、第三百五十七条第一款、第六十七条第一款之规定，判决如下', '不公开理由': '', '案件类型': '1', '裁判日期': '2017-02-21', '案件名称': '王某容留他人吸毒罪一审刑事判决书', '文书ID': 'f42dfa1f-b5ca-4a22-a416-a74300f61906', '审判程序': '一审', '案号': '（2017）苏1283刑初44号', '法院名称': '江苏省泰兴市人民法院'}]
            # text_list == []. 当请求参数有错误时才会出现text_list == [], 如data: {'Param': '当事人:深赤湾', 'Index': "'1'", 'Page': '20', 'Order': '法院层级', 'Direction': 'asc', 'case_parties': '000022', 'abbr_full_category': 'abbr', 'crawl_date': '2017-05-28'} (Index:类型错误)
            total_count = int(text_list[0]["Count"])
            print("Count:", total_count)
            redis_data = {
                "Param": data["Param"],
                "Index": repr(int(data["Index"])),    # must be repr(int())
                "case_parties": data["case_parties"],
                "abbr_full_category": data["abbr_full_category"]
            }
            redis_data_str = json.dumps(redis_data)

            if total_count == 0:
                # self.actual_output_logger.info(json.dumps(data, ensure_ascii=False))  # 记录成功抓取的（包括数目为0的）
                redis_uri_process.hset(redis_key_process, redis_data_str, "-2_0")     # [抓取完成]count == 0, 后续无需再抓取
                return
            elif total_count > self.CRAWL_LIMIT:
                redis_uri_process.hset(redis_key_process, redis_data_str, "-3_0")      # [抓取完成]无效抓取 count > CRAWL_LIMIT,需要添加新的过滤条件
                # 理论上来说只有data["Index"] == 1的情况下才会进这里来，如果data["Index"] != 1, 说明在爬取的过程中网站的数据又增加了（使用当前的过滤条件组合无法将查询结果限定到self.CRAWL_LIMIT条以内），对于这种情况以后通过爬取新的日期的数据来补充，不要也不应该在这里补充（如果在这里补充，之前爬取并入库的数据就没法撤销了，导致数据重复、数据缺失等一系列问题）
                if int(data["Index"]) != 1:
                    self.error_logger.critical("lxw_CRITICAL_ERROR: Count > CRAWL_LIMIT. data[\"Index\"]({0}) should == 1, but not. 这可能是网站数据更新的原因. data: {1}. 当事人的所有相关数据应该全部删除, 并重新爬取.\n{2}\n\n".format(data["Index"], json.dumps(data, ensure_ascii=False), "--"*30))
                    # return  # 不要return，继续入库
                else:
                    # 依靠 多个过滤条件 将查询结果限定到self.CRAWL_LIMIT条以内，具体过滤条件的过滤顺序参见 Spiders/CJOSpider/README.md
                    """
                    1)以公司名称(简称/全称)作为"当事人"过滤条件进行爬取
                    2)若1)中的"当事人"超过CJOSpider.CRAWL_LIMIT，则再按照"案件类型"进行过滤("当事人"+"案件类型")
                    3)若2)中的"案件类型"超过CJOSpider.CRAWL_LIMIT，则再按照"法院层级"进行过滤("当事人"+"案件类型"+"法院层级")
                    4)若3)中的"法院层级"超过CJOSpider.CRAWL_LIMIT，则再按照"日期"(每年/每月/每天)进行过滤("当事人"+"案件类型"+"法院层级"+"日期")
                    每年: 裁判年份:2017    每月/每天: 裁判日期:2017-05-01 TO 2017-05-31/裁判日期:2017-05-01 TO 2017-05-01
                    5)若4)中的"日期"超过CJOSpider.CRAWL_LIMIT，则再按照"文书类型"进行过滤("当事人"+"案件类型"+"法院层级"+"日期"+"文书类型")
                    6)若5)中的"文书类型"超过CJOSpider.CRAWL_LIMIT，则再按照"审判程序"进行过滤("当事人"+"案件类型"+"法院层级"+"日期"+"文书类型"+"审判程序")
                    """
                    origin_param_list = data["Param"].split(",")
                    length = len(origin_param_list)
                    if length == 1:    # 只有"当事人"，改用"当事人"+"案件类型"进行筛选
                        for category in self.CASE_CATEGORY:
                            temp_param = "{0},案件类型:{1}".format(data["Param"], category)
                            self.into_redis(redis_uri_process, redis_key_process, temp_param, int(data["Index"]), data["case_parties"], data["abbr_full_category"])   # 写 消息队列 Redis(TASKS_HASH)
                        return
                    elif length == 2:   # "当事人"+"案件类型"，改用"当事人"+"案件类型"+"法院层级"进行筛选
                        for category in self.COURT_CATEGORY:
                            temp_param = "{0},法院层级:{1}".format(data["Param"], category)
                            self.into_redis(redis_uri_process, redis_key_process, temp_param, int(data["Index"]), data["case_parties"], data["abbr_full_category"])   # 写 消息队列 Redis(TASKS_HASH)
                        return
                    elif length == 3:   # "当事人"+"案件类型"+"法院层级"，改用"当事人"+"案件类型"+"法院层级"+"日期"进行筛选
                        """
                        按照"日期"(每年/每月/每天)进行过滤("当事人"+"案件类型"+"法院层级"+"日期")
                        每年: 裁判年份:2017    每月/每天: 裁判日期:2017-05-01 TO 2017-05-31/裁判日期:2017-05-01 TO 2017-05-01
                        """
                        for year in self.get_year():    # 改用"当事人"+"案件类型"+"法院层级"+"裁判年份"进行筛选
                            temp_param = "{0},裁判年份:{1}".format(data["Param"], year)
                            self.into_redis(redis_uri_process, redis_key_process, temp_param, int(data["Index"]), data["case_parties"], data["abbr_full_category"])   # 写 消息队列 Redis(TASKS_HASH)
                        return
                    elif length == 4:
                        param_date = origin_param_list[3]  # param:  "裁判日期:2016-02-07 TO 2016-02-07,案件类型:刑事案件"
                        if "裁判年份" in param_date: # 改用"当事人"+"案件类型"+"法院层级"+"裁判日期"(每月)进行筛选
                            # 绕过每个月天数不一样，1月和12月比较特殊: 0101-0201, 0202-0301, 0302-0401, ..., 1002-1101, 1102-1201, 1202-1231
                            param_year = param_date.split(":")[1]
                            for month_param in self.get_month_param(param_year):  # 改用"当事人"+"案件类型"+"法院层级"+"裁判日期"(每月)进行筛选
                                origin_param_list[3] = "裁判日期:{0}".format(month_param)
                                # temp_param = "{0},裁判年份:{1}".format(data["Param"], year)
                                temp_param = ",".join(origin_param_list)
                                self.into_redis(redis_uri_process, redis_key_process, temp_param, int(data["Index"]), data["case_parties"], data["abbr_full_category"])   # 写 消息队列 Redis(TASKS_HASH)
                            return  # essential
                        elif "裁判日期" in param_date:   # 改用"当事人"+"案件类型"+"法院层级"+"裁判日期"(每天)进行筛选
                            param_day_list = param_date.split(":")[1].split(" TO ")
                            if param_day_list[0] == param_day_list[1]:  # 已经是“每天”的情况了，需要增加"文书类型"进行筛选
                                pass
                            else:
                                year = int(param_day_list[0].split("-")[0])
                                for year_month_date in self.get_date(year):  # 改用"当事人"+"案件类型"+"法院层级"+"裁判日期"(每天)进行筛选
                                    origin_param_list[3] = "裁判日期:{0} TO {0}".format(year_month_date)
                                    temp_param = ",".join(origin_param_list)
                                    self.into_redis(redis_uri_process, redis_key_process, temp_param, int(data["Index"]), data["case_parties"], data["abbr_full_category"])   # 写 消息队列 Redis(TASKS_HASH)
                                return  # essential
                        # "当事人"+"案件类型"+"法院层级"+"日期"，改用"当事人"+"案件类型"+"法院层级"+"日期"+"文书类型"进行筛选
                        for category in self.DOC_CATEGORY:
                            temp_param = "{0},文书类型:{1}".format(data["Param"], category)
                            self.into_redis(redis_uri_process, redis_key_process, temp_param, int(data["Index"]), data["case_parties"], data["abbr_full_category"])   # 写 消息队列 Redis(TASKS_HASH)
                        return
                    elif length == 5:   # "当事人"+"案件类型"+"法院层级"+"日期"+"文书类型"，改用"当事人"+"案件类型"+"法院层级"+"日期"+"文书类型"+"审判程序"进行筛选
                        # NOTE: "赔偿案件" 和 "执行案件" 不能使用审判程序进行筛选，网页上就是这样的
                        if "赔偿案件" in origin_param_list[1] or "执行案件" in origin_param_list[1]:
                            # 无法再精确，先把这self.CRAWL_LIMIT条数据入库，并把超过self.CRAWL_LIMIT的情况(data)，单独输出到文件中
                            self.exceed_crawl_limit_logger.error(json.dumps(data, ensure_ascii=False))
                        else:
                            for category in self.JUDGE_PROCEDURE:
                                temp_param = "{0},审判程序:{1}".format(data["Param"], category)
                                self.into_redis(redis_uri_process, redis_key_process, temp_param, int(data["Index"]), data["case_parties"], data["abbr_full_category"])   # 写 消息队列 Redis(TASKS_HASH)
                            return
                    else:
                        # 无法再精确，先把这self.CRAWL_LIMIT条数据入库，并把超过self.CRAWL_LIMIT的情况(data)，单独输出到文件中
                        self.exceed_crawl_limit_logger.error(json.dumps(data, ensure_ascii=False))
                        # DO NOT return.    # 继续下面的入库操作，先把这self.CRAWL_LIMIT条数据入库
            else:   # total_count > 0 && total_count < self.CRAWL_LIMIT
                # 不能直接yield next_index=True, 需判断是否需要yield，像count=3和count=11这种显然不需要yield下一页
                # Just continue to run the following code
                pass

            # 如果有下一页的cases需要爬取，那么继续爬取下一页
            index = int(data["Index"])
            # NOTE: 提速：第一次进来的时候（Index==1的时候）就把所有后面的页面请求全部发出去；
            # 其他情况下（Index>1）进来时都不再重复发出下面的请求
            # 能够显著提高速度，并且能够提高抓取成功率: 某一页抓取错误不会影响后面的页面数据的抓取
            if index == 1:
                quotient, remainder = divmod(total_count, self.cases_per_page)
                while index <= quotient:
                    if index < quotient:
                        self.into_redis(redis_uri_process, redis_key_process, data["Param"], index+1, data["case_parties"], data["abbr_full_category"])   # 写 消息队列 Redis(TASKS_HASH)
                    else:   # index == quotient
                        if remainder != 0:
                            self.into_redis(redis_uri_process, redis_key_process, data["Param"], index+1, data["case_parties"], data["abbr_full_category"])   # 写 消息队列 Redis(TASKS_HASH)
                    index += 1

            # 把当前Index的self.cases_per_page条cases入库
            # 每个进程一个MongoClient
            conn = pymongo.MongoClient("192.168.1.36", 27017)
            db = conn.scrapy    # dbname: scrapy
            result_dict = {}
            for case_dict in text_list[1:]:
                """
                case_dict: {'裁判要旨段原文': '本院认为，被告人王某为他人吸食毒品提供场所，其行为已构成容留他人吸毒罪，依法应予惩处。泰兴市人民检察院对被告人王某犯容留他人吸毒罪的指控成立，本院予以支持。被告人王某自动投案并如实供述自己的罪行，是自首，依法可以从轻处罚。被告人王某具有犯罪前科和多次吸毒劣迹，可酌情从重处罚。被告人王某主动向本院缴纳财产刑执行保证金，可酌情从轻处罚。关于辩护人提出“被告人王某具有自首、主动缴纳财产刑执行保证金等法定和酌定从轻处罚的情节，建议对被告人王某从轻处罚”的辩护意见，经查属实，本院予以采纳。依照《中华人民共和国刑法》第三百五十四条、第三百五十七条第一款、第六十七条第一款之规定，判决如下', '不公开理由': '', '案件类型': '1', '裁判日期': '2017-02-21', '案件名称': '王某容留他人吸毒罪一审刑事判决书', '文书ID': 'f42dfa1f-b5ca-4a22-a416-a74300f61906', '审判程序': '一审', '案号': '（2017）苏1283刑初44号', '法院名称': '江苏省泰兴市人民法院'}
                """
                result_dict["abstract"] = case_dict.get("裁判要旨段原文", "")
                result_dict["reason_not_public"] = case_dict.get("不公开理由", "")
                result_dict["case_category"] = case_dict.get("案件类型", "")
                result_dict["judge_date"] = case_dict.get("裁判日期", "")
                result_dict["case_name"] = case_dict.get("案件名称", "")
                result_dict["doc_id"] = case_dict.get("文书ID", "")
                result_dict["judge_procedure"] = case_dict.get("审判程序", "")
                result_dict["case_num"] = case_dict.get("案号", "")
                result_dict["court_name"] = case_dict.get("法院名称", "")
                result_dict["case_parties"] = data.get("case_parties", "")
                result_dict["abbr_full_category"] = data.get("abbr_full_category", "")
                result_dict["crawl_date"] = datetime.datetime.now().strftime("%Y-%m-%d")    # 爬取日期
                # 说明: 爬取日期按理说应该以"发出请求"的时间为准
                # 但"发出请求"(在各个Middlewares中)时, crawl_date不能加到POST数据中;
                # 也不能以"产生请求"的时间代替, 因为产生请求的时间,并不一定发出该请求
                # 因此相比之下, 得到响应的时间与真正发出请求的时间更近
                self.into_mongo(db, result_dict)
            # self.actual_output_logger.info(json.dumps(data, ensure_ascii=False))  # 记录所有成功抓取并入库的
            # redis_uri_process.hset(redis_key_process, redis_data_str, "-1_0")     # [抓取完成] 正确抓取到所需要的数据

        except json.JSONDecodeError as jde:
            if "<title>502</title>" in text:
                self.error_logger.error("The website returns 502\n{0}\n\n".format("--"*30))
            elif "remind" in text:
                self.error_logger.error("Bad news: the website block the spider\n{0}\n\n".format("--"*30))
                time.sleep(10)  # IP代理被禁用了，休息会儿等会儿新的代理
            else:
                self.error_logger.error("lxw_JSONDecodeError_NOTE:{0}\ntext: {1}\n{2}\n\n".format(jde, text, "--"*30))
            # 针对这些抓取不成功的case, 不用对redis做任何修改， 下次会再次重新抓取
            # self.into_redis(redis_uri_process, redis_key_process, data["Param"], int(data["Index"]), data["case_parties"], data["abbr_full_category"])   # 写 消息队列 Redis(TASKS_HASH)
        except Exception as e:
            self.error_logger.error("lxw_Exception_NOTE:{0}\ntext: {1}\n{2}\n\n".format(e, text, "--"*30))
            # 针对这些抓取不成功的case, 不用对redis做任何修改， 下次会再次重新抓取
            # self.into_redis(redis_uri_process, redis_key_process, data["Param"], int(data["Index"]), data["case_parties"], data["abbr_full_category"])   # 写 消息队列 Redis(TASKS_HASH)

    def get_year(self):
        year_list = [year for year in range(1996, 2018)]
        for year in year_list:
            yield year

    def get_month_param(self, year):
        """
        # 此函数与get_year()/get_date()不一样，此函数直接返回param中“裁判日期”（每月）对应的值
        # 绕过每个月天数不一样，1月和12月比较特殊: 0101-0201, 0202-0301, 0302-0401, ..., 1002-1101, 1102-1201, 1202-1231
        """
        for month in range(1, 13):  # Jan - Dec
            next_month = month + 1
            if month in self.DIGIT_DICT:
                month = self.DIGIT_DICT[month]
            if next_month in self.DIGIT_DICT:
                next_month = self.DIGIT_DICT[next_month]
            if month == "01":   # str
                yield "{0}-01-01 TO {0}-02-01".format(year)
            elif month == 12:   # int
                yield "{0}-12-02 TO {0}-12-31".format(year)
            else:
                yield "{0}-{1}-02 TO {0}-{2}-01".format(year, month, next_month)

    def get_date(self, year):
        """        
        :param year: type(year): int 
        :return: str
        """
        # year_list = [year for year in range(1996, 2018)]
        # print(year_list)
        for month in range(1, 13):  # Jan - Dec
            date_list = list(range(calendar.monthrange(year, month)[1] + 1)[1:])
            if month in self.DIGIT_DICT:
                month = self.DIGIT_DICT[month]
            for date in date_list:
                if date in self.DIGIT_DICT:
                    date = self.DIGIT_DICT[date]
                yield "{0}-{1}-{2}".format(year, month, date)
                # yield "1996-01-10"    # 1
                # yield "1996-02-07"    # 1
                # yield "2016-02-07"    # 4

    def into_redis(self, redis_uri, redis_key, param, index, code, category):
        """
        :param param: "POST" parameters
        :param index: page number (must be integer)
        :param code: company code
        :param category: abbr_single/abbr/full (abbr_single: 简称in全称; abbr: 使用简称; full: 使用全称)
        """
        # Redis中多余的字段一概不存
        data = {
            "Param": param,    # param: "当事人:工商银行",
            "Index": repr(index),
            "case_parties": code,   # 当事人
            "abbr_full_category": category,  # 使用全称还是简称, 标志位
        }
        # name = json.dumps(data, ensure_ascii=False)   # utf-8
        name = json.dumps(data)  # unicode
        print(name)     # TODO: check name
        redis_uri.hset(redis_key, name, "0_0")    # left_right. Only care about "left".
        """
        TASKS_HASH
        >= 0: 初始值(未爬取)/未爬取成功
        -1: 爬取成功
        """

    def into_mongo(self, db, data_dict):
        print("data_dict:", data_dict)
        db["cjo0620"].insert(data_dict)

    def crawl_basic_info(self, param, index, case_parties, category):
        """
        :param param: "POST" parameters
        :param index: page number (MUST BE INTEGER)
        :param case_parties: company code
        :param category: abbr_single/abbr/full (abbr_single: 简称in全称; abbr: 使用简称; full: 使用全称)
        """
        cookie_str = self.get_cookie_by_selenium()
        text = self.crawl_by_post(cookie_str, param, index)
        if text:
            data = {
                "Param": param,
                "Index": index,
                "Page": self.cases_per_page,
                "Order": "法院层级",
                "Direction": "asc",
                "case_parties": case_parties,    # parties: 当事人
                "abbr_full_category": category    # 使用全称还是简称, 标志位
            }
            self.process_response(text, data)

    def operate(self):
        count = 0
        continue_flag = True
        while continue_flag:
            continue_flag = False
            pool = multiprocessing.Pool(processes=1)    # TODO: IP代理数目是6, 所以这里把进程数目也设置为6
            for item in self.redis_uri.hscan_iter(self.redis_key):
                # print(type(item), item)    # <class 'tuple'> (b'{"Param": "\\u5f53\\u4e8b\\u4eba:\\u4e2d\\u56fd\\u77f3\\u6cb9\\u5316\\u5de5\\u80a1\\u4efd\\u6709\\u9650\\u516c\\u53f8", "Index": "12", "case_parties": "600028", "abbr_full_category": "full"}', b'-1_0'
                left_right = item[1].decode("utf-8").split("_")
                flag_code = int(left_right[0])  # we only care about left_right[0]
                if flag_code >= 0:    # 未请求或未请求成功    # {0: 初始值, 未爬取;    负值: 爬取成功;    > 0: 未爬取成功, 爬取的次数;}
                    continue_flag = True
                    data_dict_str = item[0].decode("utf-8")
                    data_dict = json.loads(data_dict_str)
                    pool.apply_async(self.crawl_basic_info, (data_dict["Param"], int(data_dict["Index"]), data_dict["case_parties"], data_dict["abbr_full_category"],))

            pool.close()
            pool.join()
            print("第{0}轮执行完成.".format(count))
            count += 1
            break


if __name__ == "__main__":
    cjo = CJOSpider_New()
    cjo.operate()


