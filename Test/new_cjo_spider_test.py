#!/usr/bin/env python
# coding=utf-8
#File Name: new_cjo_spider_test.py
#Author: lxw
#Date: Fri 16 Jun 2017 11:20:45 AM CST

from pyvirtualdisplay import Display
import random
import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.proxy import ProxyType
import time
from fake_useragent import UserAgent

from Spiders.CJOSpider.get_proxy import get_proxy


class NewCJOSpider:
    ua = UserAgent()
    headers = {
        "Host": "wenshu.court.gov.cn",
        "Pragma": "no-cache",
        "Referer": "http://wenshu.court.gov.cn/content/content?DocID=f42dfa1f-b5ca-4a22-a416-a74300f61906",
        "User-Agent": ua.random
    }
    # TIMEOUT = 120
    TIMEOUT = 60
    cases_per_page = 20
    proxies = {}
    doc_id_list = [
        "4a5c7734-fbb6-447b-a036-02191d3ee2b7", "27241ed4-619d-4d0e-a18c-a74500f0e6ca", "d6a12c3c-cdb5-4147-8fc3-a74500f0e6eb",
        "1c83095f-396a-442c-831b-a74500f0e6ae", "5b19caf4-3858-4796-b241-a74500f0e702"
    ]
    doc_id = random.choice(doc_id_list)
    index_url = "http://wenshu.court.gov.cn/"
    parent_url = "http://wenshu.court.gov.cn/content/content?DocID=" + doc_id
    url = "http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID=" + doc_id

    def get_driver_chrome(self):
        # chromedriver
        options = webdriver.ChromeOptions()
        proxy = get_proxy()
        # NOTE: 这里"http"和"https"一定要都写，不能只写http或者是只写https
        self.proxies["http"] = proxy
        self.proxies["https"] = proxy
        if proxy:
            options.add_argument('--proxy-server=' + proxy)

        display = Display(visible=0, size=(800, 800))
        display.start()
        driver = webdriver.Chrome(executable_path=r"/home/lxw/Software/chromedriver_selenium/chromedriver", chrome_options=options)
        
        """
        # PhantomJS: Not working. why?
        driver = webdriver.PhantomJS(executable_path=r"/home/lxw/Downloads/phantomjs/phantomjs-2.1.1-linux-x86_64/bin/phantomjs")
        proxy = webdriver.Proxy()
        proxy.proxy_type = ProxyType.MANUAL
        proxy_str = get_proxy()
        if proxy_str:
            proxy.http_proxy = proxy_str
        # 将代理设置添加到webdriver.DesiredCapabilities.PHANTOMJS中
        proxy.add_to_capabilities(webdriver.DesiredCapabilities.PHANTOMJS)
        driver.start_session(webdriver.DesiredCapabilities.PHANTOMJS)
        """

        # 设置超时时间
        driver.set_page_load_timeout(self.TIMEOUT)
        driver.set_script_timeout(self.TIMEOUT)  # 这两种设置都进行才有效
        return driver

    def test_proxy(self):
        driver = self.get_driver_chrome()
        driver.implicitly_wait(30)
        driver.get("http://xiujinniu.com/xiujinniu/index.php")
        print(driver.page_source)

    def get_cookie_by_selenium(self):
        driver = self.get_driver_chrome()
        driver.implicitly_wait(60)
        """
        driver.get(self.parent_url)
        # driver.get("http://xiujinniu.com/xiujinniu/index.php")
        driver.find_element_by_class_name("content_main")
        """
        # self.index_url is OK, 得到的Cookie和通过访问doc_id得到的Cookie形式是一样的，并且能够正确获取到所需要的数据
        driver.get(self.index_url)
        driver.find_element_by_id("nav")
        # driver.find_element_by_xpath("/html/body")
        # print(driver.page_source)
        cookie_list = driver.get_cookies()
        cookie_str_list = []
        for cookie_dict in cookie_list:
            cookie_str_list.append("{0}={1};".format(cookie_dict["name"], cookie_dict["value"]))
        cookie_str = " ".join(cookie_str_list)
        print("Cookie str:", cookie_str)
        # time.sleep(1000)
        driver.quit()
        return cookie_str

    def get_cookie_by_requests(self):   # NO
        """
        NOTE: 下面的Cookie伪造不行， 因为Cookie中还有几个其他的字段不知道是怎么构造的
        """
        proxy = get_proxy()
        proxies = {}
        proxies["http"] = proxy
        proxies["https"] = proxy
        # resp = requests.get("http://xiujinniu.com/xiujinniu/index.php", proxies=proxies, headers=self.headers)
        resp = requests.get(self.index_url, proxies=proxies, headers=self.headers)
        # resp = requests.get(self.parent_url, proxies=proxies, headers=self.headers)
        # print(resp.text)
        cookie_dict = dict(resp.cookies)
        cookie_list = ["Hm_lpvt_3f1a54c5a86d62407544d433f6418ef5={0}; Hm_lvt_3f1a54c5a86d62407544d433f6418ef5={0}".format(int(time.time()))]
        for key, value in cookie_dict.items():
            cookie_list.append("{0}={1};".format(key, value))
        cookie_str = " ".join(cookie_list)
        print(cookie_str)
        # 通过index_url获取到的Cookie是不全的，必须通过访问doc_id详情页面获取Cookie

        # 可用的Cookie形式如下：
        print("---------\n", "FSSBBIl1UgzbN7N80T=1BxDCAWQIuPmHXsTUT6xDtENw.icd8kyKJHvxblMsefOynmCogIlM7EImGahnmKpyF.gi4T16wvKKvoU7OJucbYbo5cX888YPTOyARuSz.J6CfeDMhiQFBaLI01rIhcABy9UfdFFPl63x8O5tR2.KRBpmWleFac.3IbYE4s3nklAEMegCVnhMXlNBDTcBYAy29.3iJkkpAnuBnEXHCUfdGViS0GWDIBq6_rmGt79OxxveWCgM4jHlBh1jOnQ37x8x2s6CyauK1J3TS9TDIy_5MOkfdNEvGISbMdsb_JcFHtIUuCZ7stB41qe6svK_iELhs5V; _gscs_2116842793=978637234xxwv013|pv:1; _gscu_2116842793=978637233f0ihw13; Hm_lpvt_3f1a54c5a86d62407544d433f6418ef5=1497863724; Hm_lvt_3f1a54c5a86d62407544d433f6418ef5=1497863724; _gscbrs_2116842793=1; FSSBBIl1UgzbN7N80S=rSE4ZY4eEGNUDbJKn2Kn.MXUf5FU9Bnazz_tnfUvrIVFiCqA4iVYVmw5P2347Sd.;")
        return cookie_str
        """
        # NOTE: 相当于不用Cookie直接访问doc_id详情页，是不行的(再次验证必须得用Cookie来访问)
        proxy = get_proxy()
        proxies = {}
        proxies["http"] = proxy
        proxies["https"] = proxy
        # resp = requests.get("http://xiujinniu.com/xiujinniu/index.php", proxies=proxies, headers=self.headers)
        resp = requests.get(self.parent_url, proxies=proxies, headers=self.headers)
        print(resp.text)
        """

    def crawl_doc_id_content(self, cookie_str):
        if not cookie_str:
            return
        self.headers["Cookie"] = cookie_str
        # print(self.headers)
        proxy = get_proxy()
        proxies = {}
        proxies["http"] = proxy
        proxies["https"] = proxy
        resp = requests.get(url=self.url, proxies=proxies, headers=self.headers)
        # resp = requests.get(url=self.url, headers=self.headers)    # NOTE: 没有使用代理(或者是使用其他的代理)，都可以通过Cookie直接爬取，这就意味着反爬信息完全依赖Cookie来实现
        print(resp.text)

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


if __name__ == '__main__':
    spider = NewCJOSpider()
    spider.test_proxy()
    exit(0)
    print("After exit(0).")
    # spider.test_proxy()
    # NOTE: cookie 没法重复使用(访问某个页面后，把cookie_str拷贝出来，立即访问其他页面就不行，但在程序中直接使用就可以)
    cookie_str = spider.get_cookie_by_selenium()    # OK
    # NO # cookie_str = "FSSBBIl1UgzbN7N80T=1zd9Go1xqkzybCXXMDpo6mUcXgYxfpfisjHwS_WM3zz0Qn4h39nfW.Grms9W3Iu75e86teCNWaI8AwussIXb3NDHN85dg1_PH.A9hFxSw3kEK5ID0wt6TnklqLe83OHdf2iugi0_bEdH3vK7Q0OH14qDIH6RUPhRTXTKPejV2xVf7Y2jwjj_VMf3dvnZ1sEG8LBhM76idLbYWHKnDlI_b8TO7fuiwCJ3QBcYFbVwm96KtV.cK6Y85gGZxvF7Sn0KX.dUpsQOH0F41vGHE7V.kE8CJMwUsTtNc3L0s4BDTfcR0Uq; _gscs_2116842793=97924849d2pere98|pv:1; _gscu_2116842793=97924849igk2mr98; Hm_lpvt_3f1a54c5a86d62407544d433f6418ef5=1497924849; Hm_lvt_3f1a54c5a86d62407544d433f6418ef5=1497924849; _gscbrs_2116842793=1; FSSBBIl1UgzbN7N80S=g46T.qSv48zDjMZuQa9uhwdU.PThlezspRI3ozIyTlN864f6G2Ra72EC6Z2QiZ4b;"
    spider.crawl_doc_id_content(cookie_str)
    spider.crawl_basic_info(cookie_str)

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
# 使用不同的代理，可以借用其他代理的Cookie成功抓取到数据
    cookie_str = spider.get_cookie_by_selenium()
    spider.crawl_doc_id_content(cookie_str)
    spider.crawl_basic_info(cookie_str)
    
Process finished with exit code 0
/home/lxw/IT/program/LXW_VIRTUALENV/py361scrapy133/bin/python /home/lxw/IT/projects/fintech_spider/Test/new_cjo_spider_test.py
Using IP proxy: 119.5.77.211:23032
Cookie str: FSSBBIl1UgzbN7N80T=1BxDCAWQIuPmHXsTUT6xDtENw.icd8kyKJHvxblMsefOynmCogIlM7EImGahnmKpyF.gi4T16wvKKvoU7OJucbYbo5cX888YPTOyARuSz.J6CfeDMhiQFBaLI01rIhcABy9UfdFFPl63x8O5tR2.KRBpmWleFac.3IbYE4s3nklAEMegCVnhMXlNBDTcBYAy29.3iJkkpAnuBnEXHCUfdGViS0GWDIBq6_rmGt79OxxveWCgM4jHlBh1jOnQ37x8x2s6CyauK1J3TS9TDIy_5MOkfdNEvGISbMdsb_JcFHtIUuCZ7stB41qe6svK_iELhs5V; _gscs_2116842793=978637234xxwv013|pv:1; _gscu_2116842793=978637233f0ihw13; Hm_lpvt_3f1a54c5a86d62407544d433f6418ef5=1497863724; Hm_lvt_3f1a54c5a86d62407544d433f6418ef5=1497863724; _gscbrs_2116842793=1; FSSBBIl1UgzbN7N80S=rSE4ZY4eEGNUDbJKn2Kn.MXUf5FU9Bnazz_tnfUvrIVFiCqA4iVYVmw5P2347Sd.;
Using IP proxy: 122.236.166.99:56671
$(function() {
    var jsonHtmlData = "{\"Title\":\"张春发与被执行人海林市长汀镇双丰村村民委员会买卖合同纠纷一案执行裁定书\",\"PubDate\":\"2017-03-29\",\"Html\":\"<a type='dir' name='WBSB'></a><div style='TEXT-ALIGN: center; LINE-HEIGHT: 25pt; MARGIN: 0.5pt 0cm; FONT-FAMILY: 宋体; FONT-SIZE: 22pt;'>黑龙江省海林市人民法院</div><a type='dir' name='AJJBQK'></a><div style='TEXT-ALIGN: center; LINE-HEIGHT: 30pt; MARGIN: 0.5pt 0cm; FONT-FAMILY: 仿宋; FONT-SIZE: 26pt;'>执 行 裁 定 书</div><div style='TEXT-ALIGN: right; LINE-HEIGHT: 30pt; MARGIN: 0.5pt 0cm;  FONT-FAMILY: 仿宋;FONT-SIZE: 16pt; '>(2017)黑1083执121号</div><div style='LINE-HEIGHT: 25pt;TEXT-ALIGN:justify;TEXT-JUSTIFY:inter-ideograph; TEXT-INDENT: 30pt; MARGIN: 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;'>申请执行人张春发，男，汉族，农民，住所地黑龙江省海林市长汀镇双丰村。</div><div style='LINE-HEIGHT: 25pt;TEXT-ALIGN:justify;TEXT-JUSTIFY:inter-ideograph; TEXT-INDENT: 30pt; MARGIN: 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;'>被执行人海林市长汀镇双丰村村民委员会，住所地黑龙江省海林市长汀镇双丰村。</div><div style='LINE-HEIGHT: 25pt;TEXT-ALIGN:justify;TEXT-JUSTIFY:inter-ideograph; TEXT-INDENT: 30pt; MARGIN: 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;'>法定代表人刘景泰，该村委会主任。</div><a type='dir' name='CPYZ'></a><div style='LINE-HEIGHT: 25pt;TEXT-ALIGN:justify;TEXT-JUSTIFY:inter-ideograph; TEXT-INDENT: 30pt; MARGIN: 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;'>本院依据已经发生法律效力的（2017）黑1083民初107号民事判决书，责令被执行人履行义务，但被执行人海林市长汀镇双丰村村民委员会至今未履行生效法律文书确定的义务。依照《中华人民共和国民事诉讼法》第二百四十三条、《最高人民法院关于人民法院民事执行中查封、扣押、冻结财产的规定》第三十一条，裁定如下：</div><a type='dir' name='PJJG'></a><div style='LINE-HEIGHT: 25pt;TEXT-ALIGN:justify;TEXT-JUSTIFY:inter-ideograph; TEXT-INDENT: 30pt; MARGIN: 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;'>一、扣划海林市长汀镇双丰村村民委员会银行存款10201.79元。</div><div style='LINE-HEIGHT: 25pt;TEXT-ALIGN:justify;TEXT-JUSTIFY:inter-ideograph; TEXT-INDENT: 30pt; MARGIN: 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;'>本裁定送达后即发生法律效力。</div><a type='dir' name='WBWB'></a><div style='TEXT-ALIGN: right; LINE-HEIGHT: 25pt; MARGIN: 0.5pt 72pt 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;'>审判员　　陈富友</div><br/><div style='TEXT-ALIGN: right; LINE-HEIGHT: 25pt; MARGIN: 0.5pt 72pt 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;'>二〇一七年二月二十四日</div><div style='TEXT-ALIGN: right; LINE-HEIGHT: 25pt; MARGIN: 0.5pt 72pt 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;'>书记员　　曹　宇</div>\"}";
    var jsonData = eval("(" + jsonHtmlData + ")");
    $("#contentTitle").html(jsonData.Title);
    $("#tdFBRQ").html("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;发布日期：" + jsonData.PubDate);
    var jsonHtml = jsonData.Html.replace(/01lydyh01/g, "\'");
    $("#DivContent").html(jsonHtml);

    //初始化全文插件
    Content.Content.InitPlugins();
    //全文关键字标红
    Content.Content.KeyWordMarkRed();
});
Using IP proxy: 101.206.147.229:16975
"[{\"Count\":\"4878597\"},{\"裁判要旨段原文\":\"本院认为，被告人王某为他人吸食毒品提供场所，其行为已构成容留他人吸毒罪，依法应予惩处。泰兴市人民检察院对被告人王某犯容留他人吸毒罪的指控成立，本院予以支持。被告人王某自动投案并如实供述自己的罪行，是自首，依法可以从轻处罚。被告人王某具有犯罪前科和多次吸毒劣迹，可酌情从重处罚。被告人王某主动向本院缴纳财产刑执行保证金，可酌情从轻处罚。关于辩护人提出“被告人王某具有自首、主动缴纳财产刑执行保证金等法定和酌定从轻处罚的情节，建议对被告人王某从轻处罚”的辩护意见，经查属实，本院予以采纳。依照《中华人民共和国刑法》第三百五十四条、第三百五十七条第一款、第六十七条第一款之规定，判决如下\",\"不公开理由\":\"\",\"案件类型\":\"1\",\"裁判日期\":\"2017-02-21\",\"案件名称\":\"王某容留他人吸毒罪一审刑事判决书\",\"文书ID\":\"f42dfa1f-b5ca-4a22-a416-a74300f61906\",\"审判程序\":\"一审\",\"案号\":\"（2017）苏1283刑初44号\",\"法院名称\":\"江苏省泰兴市人民法院\"},{\"裁判要旨段原文\":\"本院认为，自诉人庞某某的撤诉申请符合法律规定，依法应予准许。依照《中华人民共和国刑事诉讼法》第二百零五条第一款第（二）项、第二百零六条第一款、《最高人民法院关于适用的解释》第二百七十二条之规定，裁定如下\",\"不公开理由\":\"\",\"案件类型\":\"1\",\"裁判日期\":\"2017-03-07\",\"案件名称\":\"奚某某、张某某重婚罪一审刑事裁定书\",\"文书ID\":\"7ef23f41-b6c5-4c24-acfb-a74300f618d7\",\"审判程序\":\"一审\",\"案号\":\"（2016）苏1283刑初663号\",\"法院名称\":\"江苏省泰兴市人民法院\"},{\"裁判要旨段原文\":\"本院认为，被告人徐某某在道路上醉酒驾驶机动车，其行为已构成危险驾驶罪，依法应予惩处。泰兴市人民检察院对被告人徐某某犯危险驾驶罪的指控成立，本院予以支持。被告人徐某某归案后如实供述自己的犯罪事实，依法可以从轻处罚。被告人徐某某醉酒后驾驶机动车发生单方交通事故，且负事故的全部责任，可对其酌情从重处罚。被告人徐某某主动缴纳财产刑执行保证金，可酌情从轻处罚。依照经2011年《中华人民共和国刑法修正案（八）》修正的《中华人民共和国刑法》第一百三十三条之一第一款、第六十七条第三款之规定，判决如下\",\"不公开理由\":\"\",\"案件类型\":\"1\",\"裁判日期\":\"2017-02-20\",\"案件名称\":\"徐某某危险驾驶罪一审刑事判决书\",\"文书ID\":\"6f6df8be-6f2b-4113-89fb-a74300f618e5\",\"审判程序\":\"一审\",\"案号\":\"（2017）苏1283刑初46号\",\"法院名称\":\"江苏省泰兴市人民法院\"},{\"裁判要旨段原文\":\"本院认为，被告人李某某以非法占有为目的，伙同他人秘密窃取他人财物，数额较大，其行为已构成盗窃罪，且系共同犯罪，依法应予惩处。泰兴市人民检察院对被告人李某某犯盗窃罪的指控成立，本院予以支持。被告人李某某曾因故意犯罪被判处有期徒刑，在刑罚执行完毕后五年内再犯应当判处有期徒刑以上刑罚之罪，是累犯，应当从重处罚。被告人李某某犯罪后自动投案并如实供述了自己的罪行，是自首，依法可从轻处罚。被告人李某某伙同他人采取破坏性手段实施盗窃造成他人财产损失，可酌情从重处罚。被告人李某某的亲属主动退出违法所得，可酌情从轻处罚。依照《中华人民共和国刑法》第二百六十四条、第六十五条第一款、第六十七条第一款之规定，判决如下\",\"不公开理由\":\"\",\"案件类型\":\"1\",\"裁判日期\":\"2017-02-20\",\"案件名称\":\"李某某盗窃罪一审刑事判决书\",\"文书ID\":\"0165f4c4-1ee2-458e-a1d5-a74300f618ee\",\"审判程序\":\"一审\",\"案号\":\"（2017）苏1283刑初43号\",\"法院名称\":\"江苏省泰兴市人民法院\"},{\"裁判要旨段原文\":\"本院经审查认为，宋皓通过个人借款、协调有业务关系及无业务关联的房地产开发公司借款及帮助申请贷款等多种途径为贵州新世纪集团房地产开发有限公司开发＆ｌｄｑｕｏ;世纪佳苑＆ｒｄｑｕｏ;、＆ｌｄｑｕｏ;世纪雅苑＆ｒｄｑｕｏ;两房地产项目提供启动资金、项目运营资金，并承担资金风险。原判认为宋皓没有实际出资，而是利用职务便利为请托人黄某某谋取利益，以合作投资名义收取＆ｌｄｑｕｏ;干股＆ｒｄｑｕｏ;的理由不充分。且宋皓的部分行为与其职务无关，原判未予考虑。综上，原判认定宋皓犯受贿罪的部分事实不清，证据不足。宋皓的申诉符合《中华人民共和国刑事诉讼法》第二百四十二条第（二）项、第（三）项规定的应当重新审判条件。据此，依照《中华人民共和国刑事诉讼法》第二百四十三条第二款、二百四十四条的规定，决定如下\",\"案件类型\":\"1\",\"裁判日期\":\"2014-12-29\",\"案件名称\":\"宋皓犯受贿罪刑事决定书\",\"文书ID\":\"8252121f-8260-4241-b707-018d52d151ca\",\"审判程序\":\"再审\",\"案号\":\"（2012）刑监字第182-1号\",\"法院名称\":\"最高人民法院\"},{\"裁判要旨段原文\":\"根据《中华人民共和国刑事诉讼法》第二十六条和《最高人民法院、最高人民检察院、公安部办理毒品犯罪案件适用法律若干问题的意见》第一条的规定，决定如下\",\"案件类型\":\"1\",\"裁判日期\":\"2015-01-28\",\"案件名称\":\"邓玉玲犯非法持有毒品罪刑事决定书\",\"文书ID\":\"afcea010-7f0b-4f89-9a0a-3023dfbefed2\",\"审判程序\":\"其他\",\"案号\":\"（2015）刑立他字第8号\",\"法院名称\":\"最高人民法院\"},{\"裁判要旨段原文\":\"本院经审查认为，原判认定王某某明知所借款项为公款、与国家工作人员共谋挪用公款的犯罪事实不清，证据不足，申诉人王某某的申诉符合《中华人民共和国刑事诉讼法》第二百四十二条第（二）项、第（三）项规定的应当重新审判条件。据此，依照《中华人民共和国刑事诉讼法》第二百四十三条第二款、二百四十四条的规定，决定如下\",\"案件类型\":\"1\",\"裁判日期\":\"2015-10-22\",\"案件名称\":\"王守仁犯挪用公款罪刑事决定书\",\"文书ID\":\"029bb843-b458-4d1c-8928-fe80da403cfe\",\"审判程序\":\"再审\",\"案号\":\"（2015）刑监字第27号\",\"法院名称\":\"最高人民法院\"},{\"裁判要旨段原文\":\"本院经审查认为，申诉人方义的申诉符合《中华人民共和国刑事诉讼法》第二百四十二条规定的应当重新审判情形，决定如下\",\"案件类型\":\"1\",\"裁判日期\":\"2014-07-21\",\"案件名称\":\"方职务侵占罪申诉刑事决定书\",\"文书ID\":\"5d9f09e0-d105-4a05-8634-31b811f2c9c9\",\"审判程序\":\"再审\",\"案号\":\"（2014）刑监字第11号\",\"法院名称\":\"最高人民法院\"},{\"裁判要旨段原文\":\"本院经审查认为，申诉人的申诉符合《中华人民共和国刑事诉讼法》第二百四十二条第（二）项规定的应当重新审判情形。据此，依照《中华人民共和国刑事诉讼法》第二百四十三条第二款的规定，决定如下\",\"案件类型\":\"1\",\"裁判日期\":\"2013-12-30\",\"案件名称\":\"王某某合同诈骗指令再审决定书\",\"文书ID\":\"9aed51ab-f8b3-4f20-bf6e-06d8960c53d0\",\"审判程序\":\"再审审查与审判监督\",\"案号\":\"（2013）刑监字第59号\",\"法院名称\":\"最高人民法院\"},{\"裁判要旨段原文\":\"本院认为，被告人李良酒后无端滋事，持刀在公共场所行凶，致3人死亡、1人重伤、2人轻伤、3人轻微伤，其行为已构成故意杀人罪，且犯罪情节极其恶劣，后果严重，社会危害大，应依法惩处。第一审判决、第二审裁定认定的事实清楚，证据确实、充分，定罪准确，量刑适当。审判程序合法。依照《中华人民共和国刑事诉讼法》第二百三十五条、第二百三十九条和《最高人民法院关于适用〈中华人民共和国刑事诉讼法〉的解释》第三百五十条第（一）项的规定，裁定如下\",\"案件类型\":\"1\",\"裁判日期\":\"2013-06-24\",\"案件名称\":\"李良故意杀人死刑复核案刑事裁定书\",\"文书ID\":\"f073d26d-b647-11e3-84e9-5cf3fc0c2c18\",\"审判程序\":\"其他\",\"案号\":\"无\",\"法院名称\":\"最高人民法院\"},{\"裁判要旨段原文\":\"本院认为，被告人崔昌贵、李占勇伙同他人贩卖、运输、制造“麻古”、氯胺酮，其行为已构成贩卖、运输、制造毒品罪。被告人杨林渠伙同他人贩卖、制造“麻古”，其行为已构成贩卖、制造毒品罪。被告人赵建东伙同他人贩卖、运输、制造氯胺酮，其行为已构成贩卖、运输、制造毒品罪。被告人刘文涛伙同他人贩卖、运输、制造“麻古”，伙同他人贩卖、运输氯胺酮，其行为已构成贩卖、运输、制造毒品罪。崔昌贵、李占勇、赵建东、刘文涛伙同他人制造毒品并进行贩卖、运输，杨林渠参与制造毒品并进行贩卖，五人在共同犯罪中均起主要作用，均系主犯，均应按照其所参与的全部犯罪处罚。崔昌贵参与制造、贩卖、运输“麻古”约137.097千克、氯胺酮约545.915千克；李占勇参与制造、贩卖、运输“麻古”约120.129千克、氯胺酮约351千克；杨林渠参与制造、贩卖“麻古”约105千克；赵建东参与制造、贩卖、运输氯胺酮约537.469千克；刘文涛参与制造、贩卖、运输“麻古”约36.929千克、氯胺酮约359千克，五被告人参与毒品犯罪的数量均特别巨大，且系长期从事源头性的毒品犯罪，大部分毒品已流入社会，社会危害极大，罪行极其严重。李占勇曾因犯罪被判刑，刑满释放后又犯罪，赵建东曾因犯罪被判处缓刑，缓刑考验期满后又犯罪，主观恶性深，人身危险性大。对五被告人均应依法惩处。第一审、第二审判决认定的事实清楚，证据确实、充分，定罪准确，量刑适当。审判程序合法。依照《中华人民共和国刑事诉讼法》第二百三十五条、第二百三十九条和《最高人民法院关于适用〈中华人民共和国刑事诉讼法〉的解释》第三百五十条第（一）项的规定，裁定如下\",\"案件类型\":\"1\",\"裁判日期\":\"2013-06-24\",\"案件名称\":\"崔昌贵等贩卖、运输、制造毒品、杨林渠贩卖、制造毒品死刑复核刑事裁定书\",\"文书ID\":\"f08d44ee-b647-11e3-84e9-5cf3fc0c2c18\",\"审判程序\":\"其他\",\"案号\":\"无\",\"法院名称\":\"最高人民法院\"},{\"裁判要旨段原文\":\"本院认为，被告人石超饮酒、吸食毒品后，因琐事持刀行凶，故意非法剥夺他人生命，致二人死亡、一人轻伤，其行为已构成故意杀人罪。犯罪手段残忍，情节、后果特别严重，应依法惩处。第一审判决、第二审裁定认定的事实清楚，证据确实、充分，定罪准确，量刑适当。审判程序合法。依照《中华人民共和国刑事诉讼法》第二百三十五条、第二百三十九条和《最高人民法院关于适用〈中华人民共和国刑事诉讼法〉的解释》第三百五十条第（一）项的规定，裁定如下\",\"案件类型\":\"1\",\"裁判日期\":\"2013-03-25\",\"案件名称\":\"石超故意杀人死刑复核刑事裁定书\",\"文书ID\":\"eff41ee8-b647-11e3-84e9-5cf3fc0c2c18\",\"审判程序\":\"其他\",\"案号\":\"无\",\"法院名称\":\"最高人民法院\"},{\"案件类型\":\"1\",\"裁判日期\":\"2013-10-31\",\"案件名称\":\"吴道凤故意杀人死刑复核刑事裁定书\",\"文书ID\":\"9dd14db5-2326-4120-ab7a-2a210b0af043\",\"审判程序\":\"其他\",\"案号\":\"无\",\"法院名称\":\"最高人民法院\"},{\"裁判要旨段原文\":\"本院认为，被告人王小军故意非法剥夺他人生命，其行为已构成故意杀人罪。王小军曾因犯罪被判处刑罚，刑满释放后不思悔改，又先后两次故意杀人作案，杀死一人，致一人重伤，足见其主观恶性深，人身危险性大，犯罪情节特别恶劣，犯罪后果和罪行极其严重，应依法惩处。第一审判决、第二审裁定认定的事实清楚，证据确实、充分，定罪准确，量刑适当。审判程序合法。依照《中华人民共和国刑事诉讼法》第二百三十五条、第二百三十九条和《最高人民法院关于适用〈中华人民共和国刑事诉讼法〉的解释》第三百五十条第（一）项的规定，裁定如下\",\"案件类型\":\"1\",\"裁判日期\":\"2013-07-15\",\"案件名称\":\"王小军故意杀人死刑复核刑事裁定书\",\"文书ID\":\"f05b8b81-b647-11e3-84e9-5cf3fc0c2c18\",\"审判程序\":\"其他\",\"案号\":\"无\",\"法院名称\":\"最高人民法院\"},{\"裁判要旨段原文\":\"本院认为，被告人李新功奸淫不满十四周岁的幼女，以及违背妇女意志，采用暴力手段强行与妇女发生性关系的行为均已构成强奸罪；猥亵不满十四周岁的幼女的行为又构成猥亵儿童罪，应依法予以并罚。李新功指使未成年人为其寻找犯罪对象，强奸、奸淫幼女多人，情节恶劣并造成了其他严重后果，还猥亵幼女，社会影响恶劣，危害极大，均应依法惩处。第一审判决、第二审裁定除原判认定的第二起事实外，其余认定的事实清楚，证据确实、充分，定罪准确，量刑适当。审判程序合法。依照《中华人民共和国刑事诉讼法》第二百三十五条、第二百三十九条和《最高人民法院关于适用＜中华人民共和国刑事诉讼法＞的解释》第三百五十条第（二）项的规定，判决如下\",\"案件类型\":\"1\",\"裁判日期\":\"2013-04-12\",\"案件名称\":\"李新功强奸、猥亵儿童死刑复核刑事判决书\",\"文书ID\":\"efea2774-b647-11e3-84e9-5cf3fc0c2c18\",\"审判程序\":\"其他\",\"案号\":\"无\",\"法院名称\":\"最高人民法院\"},{\"裁判要旨段原文\":\"本院认为，被告人王青志以非法占有为目的，采取暴力手段劫取他人财物，其行为已构成抢劫罪。王青志经预谋后入户抢劫，抢劫数额巨大，并致二人死亡，犯罪性质恶劣，手段残忍，情节、后果特别严重，社会危害性极大，应依法惩处。第一审判决、第二审裁定认定的事实清楚，证据确实、充分，定罪准确，量刑适当。审判程序合法。依照《中华人民共和国刑事诉讼法》第二百三十五条、第二百三十九条和《最高人民法院关于适用＜中华人民共和国刑事诉讼法＞的解释》第三百五十条第（一）项的规定，裁定如下\",\"案件类型\":\"1\",\"裁判日期\":\"2013-02-25\",\"案件名称\":\"王青志抢劫死刑复核刑事裁定书\",\"文书ID\":\"eff7f53c-b647-11e3-84e9-5cf3fc0c2c18\",\"审判程序\":\"其他\",\"案号\":\"无\",\"法院名称\":\"最高人民法院\"},{\"裁判要旨段原文\":\"本院认为，被告人罗浩敏因赌博欠债，将自己多套经济适用房变卖后，又以申请廉租房为由纠缠他人，并为采取极端行为作了精心准备，以胁迫和暴力手段劫取他人财物，其行为已构成抢劫罪；遭到反抗后实施爆炸并持刀行凶，致一人死亡、一人轻微伤，其行为构成故意杀人罪，应予并罚。犯罪性质恶劣，动机卑劣，情节、后果特别严重，社会危害性极大，应依法惩处。罗浩敏虽主动投案，但所犯罪行极其严重，不足以从轻处罚。第一审判决、第二审裁定认定的事实清楚，证据确实、充分，定罪准确，量刑适当。审判程序合法。依照《中华人民共和国刑事诉讼法》第二百三十五条、第二百三十九条和《最高人民法院关于适用〈中华人民共和国刑事诉讼法〉的解释》第三百五十条第（一）项的规定，裁定如下\",\"案件类型\":\"1\",\"裁判日期\":\"2013-12-20\",\"案件名称\":\"罗浩敏故意杀人、抢劫死刑复核刑事裁定书\",\"文书ID\":\"f096e352-b647-11e3-84e9-5cf3fc0c2c18\",\"审判程序\":\"其他\",\"案号\":\"无\",\"法院名称\":\"最高人民法院\"},{\"裁判要旨段原文\":\"本院认为，被告人乐永飞因犯故意杀人罪，被判处死刑缓期二年执行，剥夺政治权利终身。在死刑缓期执行期间，乐永飞因琐事持木棍击打黄某某头部，致黄某某轻伤，其行为已构成故意伤害罪。乐永飞在死刑缓期执行期间又故意犯罪，经查证属实，依法应执行死刑。第一审判决、第二审裁定认定的事实清楚，证据确实、充分，定罪准确，量刑适当。审判程序合法。依照《中华人民共和国刑事诉讼法》第二百五十条第二款和《最高人民法院关于适用\u003c中华人民共和国刑事诉讼法\u003e的解释》第三百五十条第（一）项的规定，裁定如下\",\"案件类型\":\"1\",\"裁判日期\":\"2013-03-15\",\"案件名称\":\"乐永飞死刑缓期执行期间又犯故意伤害罪死刑复核刑事裁定书\",\"文书ID\":\"f06ab91c-b647-11e3-84e9-5cf3fc0c2c18\",\"审判程序\":\"其他\",\"案号\":\"无\",\"法院名称\":\"最高人民法院\"},{\"裁判要旨段原文\":\"本院认为，被告人许留军在实施盗窃过程中，为了抗拒抓捕，致被害人死亡，其行为已构成抢劫罪。许留军抢劫犯罪致人死亡，情节特别恶劣，罪行极其严重，无法定或酌定从轻处罚情节，应依法惩处。第一审判决、第二审裁定认定的事实清楚，证据确实、充分，定罪准确，量刑适当。审判程序合法。依照《中华人民共和国刑事诉讼法》第二百三十五条、第二百三十九条和《最高人民法院关于适用\u003c中华人民共和国刑事诉讼法\u003e的解释》第三百五十条第（一）项的规定，裁定如下\",\"案件类型\":\"1\",\"裁判日期\":\"2013-09-26\",\"案件名称\":\"许留军抢劫死刑复核案刑事裁定书\",\"文书ID\":\"f0750746-b647-11e3-84e9-5cf3fc0c2c18\",\"审判程序\":\"其他\",\"案号\":\"无\",\"法院名称\":\"最高人民法院\"},{\"裁判要旨段原文\":\"本院认为，被告人马哈买提江·达吾来提故意非法剥夺他人生命，故意伤害他人身体（致人死亡），还以非法占有为目的使用暴力劫取、秘密窃取他人财物，违反出入境管理而偷越国境，其行为已分别构成故意杀人罪、故意伤害罪、抢劫罪、盗窃罪和偷越国境罪，应依法数罪并罚。马哈买提江·达吾来提故意杀人致死四人，故意伤害致死一人，抢劫致二人重伤，其中入户抢劫一次，盗窃财物数额巨大，犯罪后为逃避刑罚而偷越国境。马哈买提江·达吾来提抢劫犯罪虽有自首情节，且其主动交代一起杀人犯罪事实，对其抢劫、故意杀人二起犯罪可从轻处罚，但其所犯故意杀人罪情节特别恶劣，手段特别残忍，罪行极其严重，社会危害性极大，不足以对其从轻处罚，应依法惩处。第一审判决、第二审裁定认定的事实清楚，证据确实、充分，定罪准确，量刑适当。审判程序合法。依照《中华人民共和国刑事诉讼法》第二百三十五条、第二百三十九条和《最高人民法院关于适用〈中华人民共和国刑事诉讼法〉的解释》第三百五十条第（一）项的规定，裁定如下\",\"案件类型\":\"1\",\"裁判日期\":\"2013-03-20\",\"案件名称\":\"马哈买提江·达吾来提故意杀人、故意伤害、抢劫、盗窃、偷越国境死刑复核案刑事裁定书\",\"文书ID\":\"f074f302-b647-11e3-84e9-5cf3fc0c2c18\",\"审判程序\":\"其他\",\"案号\":\"无\",\"法院名称\":\"最高人民法院\"}]"

Process finished with exit code 0
"""
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
124.16.136.100估计是被封了，10次里有8次查不出来. 更换到其他网络（手机4G网络）速度很快

20170618 23:10 Output:
/home/lxw/IT/program/LXW_VIRTUALENV/py361scrapy133/bin/python /home/lxw/IT/projects/fintech_spider/Test/new_cjo_spider_test.py
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml"><head><meta http-equiv="X-UA-Compatible" content="IE=8" /><meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" /><meta http-equiv="X-UA-Compatible" content="IE=EmulateIE8" /><title>
	
        王某容留他人吸毒罪一审刑事判决书
        - 全文页 - 中国裁判文书网
</title><link rel="shortcut icon" href="/favicon.ico" type="image/x-icon" /><link rel="bookmark" href="/favicon.ico" type="image/x-icon" /><link href="/Assets/css/Admin.css" rel="stylesheet" type="text/css" /><link href="/Assets/css/User.css" rel="stylesheet" type="text/css" /><link href="/Assets/css/Index.css" rel="stylesheet" type="text/css" /><link href="/Assets/css/List.css" rel="stylesheet" type="text/css" /><link href="/Assets/css/Menu.css" rel="stylesheet" type="text/css" /><link href="/Assets/css/MainIndex.css" rel="stylesheet" type="text/css" />
    <meta name="renderer" content="webkit" /><!--[if lt IE 9]><script>document.createElement("section")</script><![endif]--><script src="//hm.baidu.com/hm.js?3f1a54c5a86d62407544d433f6418ef5"></script><script type="text/javascript" async="" src="http://static.gridsumdissector.com/js/Clients/GWD-002808-030F33/gs.js"></script><script type="text/javascript" src="/4QbVtADbnLVIc/d.FxJzG50F.js?D9PVtGL=e5191a"></script><script type="text/javascript">var _$eT=window,_$sj=top,_$q8=opener,_$kt,_$sQ,_$fu,_$sL,_$zk,_$x4=String.fromCharCode,_$xT=[],_$yt,_$yQ,_$lS,_$wh,_$ct,_$rl,_$tC,_$wO=_$eT.Error;var _$v4,_$b0,_$cQ;var _$tQ=1;_$f6();_$eT[_$x4(101,118,97,108)](_$cO(_$t1('mScBdId1eg4by76`TeugShBfzo.rNcva2COdfAI`wtMiRgUsYisepuH`Juhsxro_m`karh`l0gGtJSFr}ne`oremihar[o)elavpnyisclut`acslre `allcdlwvt` phnt`moOacienmrtnCop`JehTdmPo`tlsston`epvTls$lt#`_omatSeooaee`___suger@eeaaultv`.hprrtSgetcijeIntmeeb``SOBe`nr`ao``rcttt`p:`oxtcdconriSiene esyaokopppyirdAxAfSOFjrcb.un`emtTdec`iAtaecaeuatl`vd`beg$M`tt`bos`uo`tcilg`fnorCsatCedo`rphl``opli``tsneltNfNizeU liBhScFiutoe`a5`Za_lgrCp0aneafXn7tjoLeba9(P{Gn8tQvFc3dK]V`1xAzi5WFtqEcDlt___`rgmrvtIlec`l_sc_a`sayretcIneo`euwe3ixtysgmbd6aV`_owtCc`latce'),_$t1('JIut5VUsWGHEqircneIcISkDvj2KDjNihTPxF9Kc7J8whL0Mabjfnffecdklmmmbjmfogqmekhifukpigbhimcmdunhkclbj')));_$uK();var _$yX=_$eI;var _$yG='T';var _$yZ='D';;;function _$pw(_$az){var _$mn=[],_$d6,_$d1,_$ea,_$dO='?'[_$ms](0);for(_$d6=0;_$d6&lt;_$az[_$qt];){_$d1=_$az[_$d6];if(_$d1&lt;0x80)_$ea=_$d1;else if(_$d1&lt;0xc0)_$ea=_$dO;else if(_$d1&lt;0xe0){_$ea=((_$d1&amp;0x3F)&lt;&lt;6)|(_$az[_$d6+1]&amp;0x3F);_$d6++ ;}else if(_$d1&lt;0xf0){_$ea=((_$d1&amp;0x0F)&lt;&lt;12)|((_$az[_$d6+1]&amp;0x3F)&lt;&lt;6)|(_$az[_$d6+2]&amp;0x3F);_$d6+=2;}else if(_$d1&lt;0xf8){_$ea=_$dO;_$d6+=3;}else if(_$d1&lt;0xfc){_$ea=_$dO;_$d6+=4;}else if(_$d1&lt;0xfe){_$ea=_$dO;_$d6+=5;}else _$ea=_$dO;_$d6++ ;_$mn.push(_$ea);}return _$c0(_$mn);};;;function _$uj(_$az,_$mn,_$d6,_$d1){var _$ea=Math.floor((_$mn+_$d6)/2);if(_$d1&gt;0){_$d1-- ;if(_$ea-_$mn&gt;=3)_$uj(_$az,_$mn,_$ea,_$d1);if(_$d6-_$ea&gt;=3)_$uj(_$az,_$ea,_$d6,_$d1);}for(var _$dO=_$mn;_$dO&lt;_$ea;_$dO+=2){var _$fy=_$az[_$dO];var _$av=_$d6-1-(_$dO-_$mn);_$az[_$dO]=_$az[_$av];_$az[_$av]=_$fy;}};_$gs();;function _$zf(_$az){var _$mn=_$ze(_$az);return _$pw(_$mn);}var _$sH;function _$vr(_$az,_$mn){if(_$eT._$yA)return;if(_$mn!==_$tC&amp;&amp;!_$mn)return;console[_$gu](_$az);}function _$c0(_$az,_$mn,_$d6){_$mn=_$mn||0;if(_$d6===_$tC)_$d6=_$az.length;var _$d1=[],_$ea;while(true){_$ea=_$mn+40960;if(_$ea&gt;=_$d6){_$d1.push(_$x4.apply(null,_$az.slice(_$mn,_$d6)));break;}else{_$d1.push(_$x4.apply(null,_$az.slice(_$mn,_$ea)));_$mn=_$ea;}}return _$d1.join('');}function _$pA(){_$se=_$eT[_$hF][_$mJ]()[_$bc](/[\r\n\s]/g,"")!==_$iJ;}function _$to(_$az){if(_$az===undefined||_$az==="")return;var _$mn=_$eT[_$u8][_$p7],_$d6;if(!_$sH)_$sH=_$mn.push;if(_$eT[_$gK])_$d6=_$eT[_$gK](_$az);else{var _$d1=_$eT[_$hF];_$d6=_$d1[_$i9](_$eT,_$az);}if(_$sH!==_$mn.push)_$mn.push=_$sH;return _$d6;}function _$dj(_$az,_$mn){_$v4|=_$az;if(_$mn)_$b0|=_$az;}function _$sV(_$az){var _$mn=[],_$d6;_$az=_$vg(_$az);for(_$d6=0;_$d6&lt;_$az[_$qt];_$d6++ )_$mn.push(_$az[_$ms](_$d6));return _$mn;}function _$tj(_$az){var _$mn=_$az[_$qt],_$d6=new Array(_$mn),_$d1,_$ea;for(_$d1=0;_$d1&lt;_$mn;_$d1++ ){_$ea=_$az[_$ms](_$d1);_$d6[_$d1]=_$yt[_$ea];}return _$d6.join('');}function _$gs(){_$u1=0;_$zk._$ys=_$v2();_$t5=_$zk._$ys;_$sS=_$t1('`n3jxKDRQZP8aGQtj8tgVWwLnpbP5EN`ptrwT17c`');_$sS=_$sS[_$nI]('`');_$vo=_$y8('WZ0r5A');_$dv=_$t1('212');_$dv=parseInt(_$dv);_$dj(4,0);_$dj(2,_$wn(7));_$e5=_$y8('xlGK');var _$az=_$zk[_$kw];if(_$az){_$zk[_$kw]=false;_$cS(_$az);}_$zk._$yi=_$v2();if(_$zk._$yi-_$zk._$ys&gt;12000){_$dj(1,1);_$vN(13,1);}else _$dj(1,0);_$dj(8,0);_$dj(16,0);}function _$y4(_$az){var _$mn=_$ze(_$az),_$d6=(_$mn[0]&lt;&lt;8)+_$mn[1],_$d1=_$mn[_$qt],_$ea;for(_$ea=2;_$ea&lt;_$d1;_$ea+=2){_$mn[_$ea]^=(_$d6&gt;&gt;8)&amp;0xFF;if(_$ea+1&lt;_$d1)_$mn[_$ea+1]^=_$d6&amp;0xFF;_$d6++ ;}return _$mn[_$mE](2);}function _$v2(){return new Date()[_$bD]();}function _$s5(_$az){for(var _$mn,_$d6,_$d1=_$az[_$qt]-1;_$d1&gt;0;_$d1-- ){_$mn=Math[_$oV](_$hl()*_$d1);_$d6=_$az[_$d1];_$az[_$d1]=_$az[_$mn];_$az[_$mn]=_$d6;}return _$az;}function _$uK(){_$kt=_$fL;_$kt=_$kt[_$nI]('');_$sQ=_$eT[_$hM];_$fu=_$sj[_$jj];if(_$q8)_$sL=_$q8[_$jj];else _$sL=null;_$hl=_$eT[_$f5][_$lK];_$ct=_$eT[_$kj];_$rl=_$eT[_$ni];_$zk=_$eT[_$dT];_$lS=_$eT[_$cx];if(_$lS)try{_$lS[_$mP]=_$mP;_$lS[_$mh](_$mP);_$lS[_$uN]=_$cx;}catch(_$az){_$lS=_$tC;}if(!_$v4&amp;&amp;!_$b0){_$b0=0;_$v4=0;_$cQ=0;}_$eT[_$hD]=_$eT[_$hD]||(function(){var _$mn={};_$mn[_$gu]=function(){};return _$mn;})();if(!_$zk){_$zk=new Object();_$eT[_$dT]=_$zk;}_$wh=_$ze(_$c2);}function _$m7(_$az,_$mn){var _$d6=_$az.length,_$d1=new Array(Math.ceil(_$az.length/_$mn)),_$ea=0,_$dO=0;for(;_$dO&lt;_$d6;_$dO+=_$mn,_$ea++ )_$d1[_$ea]=_$az.substr(_$dO,_$mn);return _$d1;}function _$cO(_$az,_$mn){_$az=_$az.split('`');_$mn=_$m7(_$mn,2);var _$d6=_$x4(95,36);for(var _$d1=0;_$d1&lt;_$mn.length;_$d1++ )_$mn[_$d1]=_$d6+_$mn[_$d1];;var _$ea=[_$x4(118,97,114,32)];for(var _$d1=0;_$d1&lt;_$az.length;_$d1++ ){if(_$d1&gt;0)_$ea.push(',');_$ea.push(_$mn[_$d1]+'="'+_$az[_$d1]+'"');}_$ea.push(';');return _$ea.join('');}function _$y8(_$az){return _$pw(_$y4(_$az),_$dj(2,_$wn(9)));}function _$ze(_$az){var _$mn=_$az[_$qt],_$d6=new Array(Math[_$oV](_$mn*3/4));var _$d1,_$ea,_$dO,_$fy;var _$av=0,_$oc=0,_$kA=_$mn-3;for(_$av=0;_$av&lt;_$kA;_$av=_$av+4){_$d1=_$xT[_$az[_$ms](_$av)];_$ea=_$xT[_$az[_$ms](_$av+1)];_$dO=_$xT[_$az[_$ms](_$av+2)];_$fy=_$xT[_$az[_$ms](_$av+3)];_$d6[_$oc++ ]=(_$d1&lt;&lt;2)|(_$ea&gt;&gt;4);_$d6[_$oc++ ]=((_$ea&amp;15)&lt;&lt;4)|(_$dO&gt;&gt;2);_$d6[_$oc++ ]=((_$dO&amp;3)&lt;&lt;6)|_$fy;}if(_$av&lt;_$mn){_$d1=_$xT[_$az[_$ms](_$av)];_$ea=_$xT[_$az[_$ms](_$av+1)];_$d6[_$oc++ ]=(_$d1&lt;&lt;2)|(_$ea&gt;&gt;4);if(_$av+2&lt;_$mn){_$dO=_$xT[_$az[_$ms](_$av+2)];_$d6[_$oc++ ]=((_$ea&amp;15)&lt;&lt;4)|(_$dO&gt;&gt;2);}}return _$d6;}function _$vg(_$az){return unescape(encodeURIComponent(_$az));}function _$wn(_$az){var _$mn=_$wO&amp;&amp;new _$wO();if(_$mn){var _$d6=_$mn[_$cr];if(!_$d6)return;var _$d1=_$d6[_$mJ]();var _$ea=_$d1[_$nI]('\n');_$d1=_$ea[_$kq]();if(_$d1===''&amp;&amp;_$ea[_$qt]&gt;0)_$d1=_$ea[_$kq]();if(_$d1[_$li](_$dc)!== -1||_$p5(_$d1,_$ee)||_$d1===_$fc){_$vN(_$az,1);return true;}}}function _$y5(_$az,_$mn){if(typeof _$az===_$bG)_$az=_$sV(_$az);if(!_$mn)_$mn=_$kt;var _$d6='',_$d1;for(_$d1=0;_$d1&lt;_$az[_$qt];_$d1=_$d1+3){_$d6+=_$mn[_$az[_$d1]&gt;&gt;2];_$d6+=_$mn[((_$az[_$d1]&amp;3)&lt;&lt;4)|(_$az[_$d1+1]&gt;&gt;4)];if(_$az[_$d1+1]!==_$tC)_$d6+=_$mn[((_$az[_$d1+1]&amp;15)&lt;&lt;2)|(_$az[_$d1+2]&gt;&gt;6)];else{}if(_$az[_$d1+2]!==_$tC)_$d6+=_$mn[_$az[_$d1+2]&amp;63];}return _$d6;}function _$pP(_$az,_$mn){var _$d6=_$az[_$mn]&amp;0xf0;if((_$d6&amp;0x80)===0)return 1;if((_$d6&amp;0xc0)===0x80)return 2;if((_$d6&amp;0xe0)===0xc0)return 3;if((_$d6&amp;0xf0)===0xe0)return 4;;}function _$vN(_$az,_$mn){if(!_$lS)return;if(typeof _$az===_$k0)_$az=String(_$az);var _$d6=_$sP(_$az);if(_$d6)_$mn=parseInt(_$d6)+_$mn;_$az=_$ih+_$y5(_$az);_$lS[_$az]=_$mn;}function _$mD(_$az){var _$mn=_$az[_$qt],_$d6=new Array(_$mn),_$d1,_$ea;for(_$d1=0;_$d1&lt;_$mn;_$d1++ ){_$ea=_$az[_$ms](_$d1);if(_$ea&gt;=32&amp;&amp;_$ea&lt;127)_$d6[_$d1]=_$yQ[_$ea-32];else _$d6[_$d1]=_$az[_$fS](_$d1);}return _$d6.join('');}function _$rZ(){return _$y8('pg3bZcM6WeazBnM7xjmnavhZQXzn.kHkQ7xndvtZQ.mnCUhKQXzn6otdQ.Jn.UhfhwJna6tjQ7xnG6h_Qzznn6hphQYn6164MzmnGc6mQNwnCaH3hIen2cCQQBGzS16iQNTX5ohRhIqzgvtxQ79zupXrQL9M01CwhRRXLcC.hIlX4cCtxF7z4PC0M5Zu_qijWdlzOP6nm.2zfKCGM_0k_1ClW49zZnKPx3GzZcKBWdwzgKnAhjz0Sb5iqyWzvn6YW_ZzSkHrWZLznsUq3Jqz0kiMMMWkC1CcW4EkNnUA8jZ26b4hMZLuGqirW4pX2siJERJBnU1ZEPG53n3GklZZFkS8319j3sSWt2mf8CZBkD9ZWkaTkcZXtkayt2lCK1lu862PWcmS8nZZKUpTHkZZIPrw3KxPwOS83pTfkaaxi97WYASMko0WQCmu3vqZQsGIHmwXp6e.3VggVqSZt9VZFDmGkrEZUCl8hfWWqbliRA0WUqSNMTyBouEQiOLCtbZQtfLWJqa4MnqfoOxO3owBDAaY3KQ5QuRe3qECFPLStPVj3cNj3qGgHf9SED7WonlPR1SfoAaCifgjEs3TmlRfiCE5i2g_DPq8xOgWs1mJh2zfoKlVISV_Y1gdklV5sPLM3aWjEsLV3STODkyY3VLGUu3sRArBokOE8_G5LDdfh7pf4k.iIeEj.uOj3eY2gn.bW7lnCbdfiXmGZ6B13Xg5TuM68ZLVC1DZhXQGXkOj3hL_S6Xz3MGVdk.x3LzfySvE3Q0jP1.6EW7geps8iLr2_k._hNGCdv5135V__s.1iJROuCkftzZnPpsrDRg_6KdatLLVekOJtLg_5OjWwIVGZKKIiEfG41.PitajzPDh35LR.kj9i.9X9nt4WB9XN1FQtXG_vDk0EHqg4CduH.yOPKd4RI0Xds.Hw37GXcF83.fTSPcX3_A_.D5eMeTTSOjmIZxPjPkQmtQXfpbkhNxBSp1fxjTBzcoURQS4uu_b3zgC7ChRE3Q4xOzViYwfIu7gM2Vu8byLi0f5JkZSwDJ0FPQSmKGBwnwZmKTXMCpkRcZy3nZS3uS0xKyzJCz0HOZBWTW4IrGX8Ge9Y6yqEpgfQKERiAYfwOJY3VNOsDgKiSeXRCErxSEulbEtJTmXRrGK39lY8O2z3fEymOwtxSgGou2qwo3dD6Af3np93cl4woQGhsJ.3KWfEs7tMORfIPz68PYXcOJGWumXR6pvEsZJFkZqRoR9qDJBipNf3Kxg3ugvRvg0HCgfK6g4EkZulCyHhTRXmrVC3PEBUDElmVmG1keEIPgJYcQKhal3xnQmmsQyVcQVwcLdUnljJTmPsrVgIOJP1DEdRiW30s5j3erfnv4jmF3v7KsDIjTfyo_G3epP.uiXh5TOZpP_kMLy_sbNmQVYZuiu3_9vnDt_382_znIoiMWYakdrwH06nvsuiQg6CrOmILw0ZkIzRJx_dvjVJd25gfU88zWG6n8FEHT5yCHGEQSG_bs0J5AY9vs33wN5bn8wE8Ades8zRHYfPKiiEHE6.kHGJ_9y_pULW50d2o4Sx_AYZPo6DxT0eO8WHgVY218bW4lG4OiDhyEGfo1AWgVugv4j8L9JnbDbxZW3OfKzH4SfXSUiwxAYuU1iREq326_AmRmO7SOKWgGvznD1H_9B6KtIH_G4SojoiM7BCkvD3yqv2bxwE6WPxS3GwnE_8KmtwTReAOr3icxfKv0.iPZ9F6TNxlTP3kN_Msfv1D0zDuyexf74D0l_sUQvWc99McxXD6laYOpeEbl9V1AiMAQ0kC0oEveeqCqHhlyvYPxAJqGOwDwJIVa9FfzXxrqZpUT3tDE5kCxzD62zoDm0RaV9l6wG3ffvEuazIpx6icS231pekS7_8sVMlrzaDSGPlDqqib3Mw1WvEvx6QCrN3vEZI1AzR6q7HCrn3qSy8kS4WcrOif3WiOg0UOqG8VaaAka13qA01PErxkVZq6QKRTzPrr7UDayOtspK39zyWcWVD0zvhDwUhrrvtKriEufeYsa0MVaZXkum3tGZu6vIE.Waav8zEilPNvbzxhgg0nhLEzxfjCtOHXaPN1tyWhQOeukkw5mOys.Eht7Zuo8zWhYG4O.B3RlaafBKtHgKeniwHEVZZCH9iXV0TcufEBJebSMCMwQ_fpXxxENeCOkmEZZZnOu9WEJzeC8DEZNOnvvTmzlPnCovE_gZBcOOHtyyjSXDHh0OGOu5ijYyfu1Oijmy4OcOhhWZvnu_Edmeyns5ijEZL1hSDgRPZuP.hhq_5sc6E.mParBW3Nx6Lu.3Eg9_LbIJw477z11lRy906ujs3jx6uK8_330LzP1bi7W00v8gR_LO0OuHw4rv7u4lJWLGvu4KEnTOA1W_3V7OUcYhm6ASpnYVE2GPFszuDP3ehsTvxYaU16SfhVTCpbm7Ik3Owkz5E62OAvStRbZOwbaaEPJZUcm8R9AzQOTm8orPIPJn3S32RoRRxpTCqPxawGYZqnWh3TVzKKE1E69zck7IWK32rcTz8l72lu01D9q2Asm0HYl2R6aNJAyOin0X8DfCtvaA3GEThnT2HK3PMDmPJKmPokY2tALSkbWMIDSb8ofGtsgyIn0J36ESln9VmuVFiSLkJsJfWs2rJs3FH6GHDPaTDnYokSQ4W10g3rEFAfwoHAaUUKleWVZFqCWxImaykDl6JY0UUKEb3ALeJo3HRfeOVkKCEZZPnbcLxQQU7CFBIJa4ConnEdGPnrjaJFTg_u6538LOgcK08WEPubkLDzGUNPhnWQxggOD78tlfnsv7WINP_DuEh3zbgnU0MH2GaoPJ8xpOPCD13EygObMpDN2GeKkI3x2ZTn6LwBqzSCchhRlzavFiwXr7SKnsIJyfOsbx3tJCGfIyx3WUeCtYwB04OKDRi5eG7PioWR3FvDcKRjqz.sXxDBEFgrjkWMQygCnJ3hETGPKPx3ZOgcHCwjLP4OKO3Wf7PkCZmyAUfOCbMteZvcizmZVT9SjiWMgT2DiktFSgj6nbmymb.cCLi_zGabnNHwWFjsDsWQN7CctbhQE5ErTv31QPFugTxo7PJCplEbQjUfrI3KYdFPNYoszvYDwotPNbHu3Gib2vxOSgH9e.Wkxklkl_3uNoICTbHvzqRm3CsuyoQAp4Uo71Hrwb1Cm.t2f4K6mZIT3nr6e9xU7wpOyIlDZwr1p2xYqX1Dw8Hfm.FPpDRqT.VcNrQVrdUPySRc2bHDQAiORvJ1gWRS75xcy7hf9PHu308Sm.tD3yInyStKm0RPZAJK79iqw9r6Z6HqLwIqfCFC2vqoZZEOgXivmiiGgZpk3A3YfdiKYHxs0Alngh8uWnYu3cxYE5EngYh924of0iQ1qPmPgYWfEAlv73lqQ5tDVKtOmSokRYFez4NktdQ80ZBDBGcJ9jLP4lW.G2LUdmRJRvn11LI_anXc47');}function _$f6(){if(_$m7)/$/.test(_$ug());var _$az=new Array(32);for(var _$mn=0;_$mn&lt;32;_$mn++ )_$az[_$mn]=_$mn;_$az=_$c0(_$az).split('');var _$d6=new Array(129);for(var _$mn=127;_$mn&lt;256;_$mn++ )_$d6[_$mn-127]=_$mn;_$d6=_$c0(_$d6).split('');_$yt='I-M3DJ0rcufq%d\\1]B:b&amp;yTo2&lt;&gt;HFn};X |9v`[(V#A~Z*5.Cm^OWR{SN/E6pU)K$ztL@8e,jax\'7!lQg4s+w"k?P=i_GYh'.split('');_$yt=_$az.concat(_$yt.concat(_$d6));_$yQ='AmuI`,4kG^Msg!OY&amp;/8#qN[leC2?9y:wdJ1P$Z&lt;|; %_c"XSxoUW6]HT@}LF.0R{Ei3(-f*p~zhvnQ=7\\+\'rb)Dtj5aVB&gt;K'.split('');}function _$uB(_$az){return _$az[_$mJ]()[_$bv](/{\s*return\s*([A-Za-z0-9$_-]+);?\s*}/)[1];}function _$ui(_$az,_$mn){for(var _$d6=0;_$d6&lt;_$mn[_$qt];_$d6++ )_$az.push(_$mn[_$d6]);}function _$ug(){var _$az='ef ghi  jklmnoL U3F9\\_XM?Ep  q rs1PW\');A0@.7I&lt;JDC=:RV85-O6]t uv[ QG#`^BY,/K$%&amp;S(2!"4+TH&gt;*ZNacbd';for(var _$mn=0;_$mn&lt;32;_$mn++ )_$xT[_$mn]=0;for(_$mn=0;_$mn&lt;_$az.length;_$mn++ )_$xT[_$mn+32]=_$az.charCodeAt(_$mn)-33;}function _$wk(_$az,_$mn){if(!_$az){if(_$lS&amp;&amp;_$lS.$d==='1')debugger;if(_$mn)throw _$mn;else throw _$fn+_$az;}}function _$sP(_$az){if(!_$lS)return;if(typeof _$az===_$k0)_$az=String(_$az);_$az=_$ih+_$y5(_$az);return _$lS[_$az];}function _$cS(_$d6){var _$d1=_$v2();_$pA();_$d6=_$ze(_$d6);var _$ea=0;_$d1=_$v2();var _$dO=parseInt(_$y8('8ERHz97'));var _$fy=_$mH,_$av='u',_$oc='?',_$kA='E',_$rb="^";var _$k2=_$rZ();;function _$az(_$wY,_$jo){var _$jf,_$i3;for(var _$at=0;_$at&lt;_$wY;_$at++ ){_$jf=_$cb();_$i3=_$jf[1];switch(_$jf[0]){case 0:_$jo.push(_$kZ[_$i3]);break;case 1:_$mn(_$i3,_$jo);break;case 2:_$az(_$i3,_$jo);break;case 3:_$az(_$i3,_$jo);break;case 4:;_$jo.push(_$k2[_$i3]);break;case 5:_$jo.push(_$kv);_$jo.push(_$mD(_$y5(_$tj(_$kZ[_$i3]))));_$jo.push(_$av+_$rb);break;case 6:if(_$i3===0){_$jo.push(_$av);_$jo.push(_$jT);_$jo.push(_$av);}else if(_$i3===1){_$jo.push(_$av);_$jo.push(_$iv);_$jo.push(_$av);}else if(_$i3===2){var _$iR=_$eT[_$f5][_$oV]((_$v2()-_$t5)/1000);_$dv=_$dv+_$eT[_$f5][_$oV](_$eT[_$f5][_$gu](_$iR/5.88+1));_$jo.push(_$av);_$jo.push(_$mD(_$dv[_$mJ]()));_$jo.push(_$av);}else _$jo.push(_$fy);break;case 7:;_$jo.push(_$k2[_$i3+_$dO]);break;default:;}}}_$d1=_$v2();var _$kv=_$mD(_$uB(function(){return _$zf;})+'("');var _$ff=_$sK();var _$kZ=_$qD();_$d1=_$v2();_$ff=_$sK();;function _$qD(){var _$wY,_$jo,_$jf,_$i3;_$jo=_$ly();_$wY=_$ly();_$jf=_$j8(_$wY);var _$at=_$jf[_$nI](_$kA);_$jo=_$ly();for(var _$iR=0;_$iR&lt;_$jo;_$iR++ ){_$i3=_$ly();_$at.push(_$j8(_$i3));}return _$at;}var _$b6=_$ly();var _$jT=_$jp();var _$iv=_$k2[_$mW](_$dO*2,_$b6*2);_$k2=_$m7(_$k2,2);var _$nf=_$mD(_$jU);for(var _$xa=0;_$xa&lt;_$k2[_$qt];_$xa++ )_$k2[_$xa]=_$nf+_$k2[_$xa];var _$j1=parseInt(_$t1('903'));;function _$jp(){var _$wY=_$ly();return _$j8(_$wY);}if(_$j1&gt;=0&amp;&amp;_$eT[_$tj(_$k2[_$j1])])_$s5(_$k2);;function _$sK(){return _$d6[_$ea++ ];};_$d1=_$v2();_$ff=_$sK();var _$br=[];;function _$cb(){var _$wY=_$sK();if(_$wY&lt;8)return[_$wY,_$ly()];else return[_$wY&amp;0x7,((_$wY&gt;&gt;&gt;3)&amp;0x1F)-1];}_$az(_$ly(),_$br);_$d1=_$v2();_$to(_$tj(_$br.join('')));;function _$mn(_$wY,_$jo){var _$jf=_$ly(),_$i3,_$at,_$iR=[],_$nk=[],_$uY;for(_$i3=0;_$i3&lt;_$wY;_$i3++ ){_$at=_$ly();_$uY=[];_$az(_$at,_$uY);_$iR.push(_$uY);}for(_$i3=0;_$i3&lt;_$jf;_$i3++ ){_$at=_$ly();_$uY=[];_$az(_$at,_$uY);_$nk.push(_$uY);};_$s5(_$iR);_$i3=0;var _$gm=0;var _$eB=_$hl()%(_$jf-_$i3+1)%(_$wY-_$gm);for(var _$kS=0;_$kS&lt;_$jf;_$kS++ ){if(_$eB&lt;0&amp;&amp;_$gm&lt;_$wY){_$eB=_$hl()%(_$jf-_$i3)%(_$wY-_$gm);_$jo.push(_$oc);_$ui(_$jo,_$iR[_$gm]);_$gm++ ;}_$ui(_$jo,_$nk[_$kS]);_$eB-- ;_$i3++ ;}while(_$gm&lt;_$wY){_$ui(_$jo,_$iR[_$gm]);_$gm++ ;}}return;;function _$ly(){var _$wY=_$iB(_$d6,_$ea);_$ea+=_$pP(_$d6,_$ea);return _$wY;};;;function _$j8(_$wY){var _$jo=_$ea;_$ea+=_$wY;if(_$wY&lt;10240)return String[_$ak][_$jI](null,_$d6[_$mE](_$jo,_$ea));else return _$c0(_$d6,_$jo,_$ea);};}function _$p5(_$az,_$mn){return _$az[_$mE](0,_$mn[_$qt])===_$mn;}function _$iB(_$az,_$mn){var _$d6=_$az[_$mn];if((_$d6&amp;0x80)===0)return _$d6;if((_$d6&amp;0xc0)===0x80)return((_$d6&amp;0x3f)&lt;&lt;8)|_$az[_$mn+1];if((_$d6&amp;0xe0)===0xc0)return((_$d6&amp;0x1f)&lt;&lt;16)|(_$az[_$mn+1]&lt;&lt;8)|_$az[_$mn+2];if((_$d6&amp;0xf0)===0xe0)return((_$d6&amp;0xf)&lt;&lt;24)|(_$az[_$mn+1]&lt;&lt;16)|(_$az[_$mn+2]&lt;&lt;8)|_$az[_$mn+3];;}function _$t1(_$az){var _$mn=_$az.split('');_$uj(_$mn,0,_$mn.length,2);return _$mn.join('');}</script><script src="/Scripts/jquery-1.4.1.js" type="text/javascript"></script>
    
    <script src="/Assets/js/Lawyee.CPWSW.WinDrag.js" type="text/javascript"></script>
    <script src="/Assets/plugin/Lawyee.CPWSW.Content.Summary.js" type="text/javascript"></script>
    <script src="/Assets/plugin/Lawyee.CPWSW.Content.Function.js" type="text/javascript"></script>
    <script src="/Assets/plugin/Lawyee.CPWSW.Content.Directory.js" type="text/javascript"></script>
    <script src="/Assets/plugin/Lawyee.CPWSW.Content.RelateFiles.js" type="text/javascript"></script>
    
    <script src="/Assets/js/qrcode/qrcode.js" type="text/javascript"></script>
    
    <script src="/Assets/js/Lawyee.CPWSW.MobileApp.js" type="text/javascript"></script>
    <script src="/Assets/js/Lawyee.CPWSW.Content.js" type="text/javascript"></script>
    <script src="/Assets/js/Lawyee.CPWSW.User.js" type="text/javascript"></script>
    <script src="/Scripts/jquery.json-2.3.min.js" type="text/javascript"></script>
    <script src="/Assets/js/lawyee.namespace.root.js" type="text/javascript"></script>
    
    
    <script type="text/javascript" src="/Assets/js/libs/js/form/datePicker/WdatePicker.js"></script><link href="/Assets/js/libs/js/form/datePicker/skin/WdatePicker.css" rel="stylesheet" type="text/css" />
    
    <script src="/Assets/js/lawyee.namespace.root.js" type="text/javascript"></script>
    
    <script src="/Assets/js/Lawyee.CPWSW.WebsiteLog.js" type="text/javascript"></script>
    
    <script src="/Scripts/jquery.PrintArea.js" type="text/javascript"></script>
    <script src="/Assets/js/Lawyee.CPWSW.GridSum.js" type="text/javascript"></script>
        <script src="/Assets/js/Lawyee.CPWSW.BaiduStatic.js" type="text/javascript"></script>
    <script src="/CreateContentJS/CreateContentJS.aspx?DocID=f42dfa1f-b5ca-4a22-a416-a74300f61906" type="text/javascript"></script>
    <style type="text/css">
        .button
        {
            background: transparent url(/Assets/js/libs/skins/red/form/btn_bg.jpg) repeat scroll 0 0;
            border: 1px solid #cc3428;
            height: 24px;
            line-height: 22px;
            margin-right: 4px;
            min-width: 60px;
            color: White;
            cursor: pointer;
            background-color: #B91516;
        }
    </style>
    
<script src="http://bdimg.share.baidu.com/static/api/js/share.js?v=89860593.js?cdnversion=416054"></script><link rel="stylesheet" href="http://bdimg.share.baidu.com/static/api/css/share_style0_16.css?v=6aba13f0.css" /></head>
<body>
    <div class="main">
        <script src="../../Assets/js/Lawyee.CPWSW.ContentPageHead.js" type="text/javascript"></script>
        <div class="content_main">
                <div class="div_container">
                    <div style="height: 25px;">
                    </div>
                    <div class="content_tool_left ">
                        <div>
                            <div id="divTool_Dir" class="div_tool_dir" style="top: 30%;">
                            </div>
                        </div>
                    </div>
                    <div style="width: 70%; float: left;">
                        
                        <div class="relatefiles_container">
                            <div class="relatefiles_banner">
                                   <label title="关联文书仅以本网收录的裁判文书为依据，如果对此结果有疑义，请联系作出裁判文书的人民法院。">关联文书</label></div>
                            <div id="divRelateFiles" class="content_relatefiles">
                            </div>
                        </div>
                        <div id="divContent" class="div_doc_container">
                            <div id="Content">
                                <div id="contentTitle" style="text-align: center; line-height: 25pt; margin: 0.5pt 0cm;&#10;                                    font-family: 黑体; font-size: 18pt;">王某容留他人吸毒罪一审刑事判决书</div>
                                <div style="border-bottom: 1px dashed #BBBBBB; margin-bottom: 30px; height: 70px;">
                                    <div style="height: 20px; padding-top: 43px;">
                                        <table style="height: 20px; width: 100%;">
                                            <tbody><tr>
                                                <td style="font-size: 15px; font-family: '微软雅黑';text-align:left;" id="tdFBRQ">      发布日期：2017-03-28</td>
                                                <td>
                                                </td>
                                                <td id="con_llcs" style="font-size: 15px; font-family: '微软雅黑';">浏览：21648次</td>
                                                <td>
                                                    <ul>
                                                        <li style="display: inline;">
                                                            <img id="img_download" style="padding-top: 3px; cursor: pointer;" src="/Assets/img/content/download_small.png" alt="点击下载文书" onclick="lawyeeToolbar.Save.Html2Word();" data-bd-imgshare-binded="1" />  </li>
                                                        <li style="display: inline;">
                                                            <img id="img_print" style="padding-top: 3px; cursor: pointer;" src="/Assets/img/content/print_small.png" onclick="lawyeeToolbar.Print.PrintHtml()" alt="点击打印文书" data-bd-imgshare-binded="1" />
                                                        </li>
                                                    </ul>
                                                </td>
                                            </tr>
                                        </tbody></table>
                                    </div>
                                </div>
                                <div id="DivContent" style="TEXT-ALIGN: justify; text-justify: inter-ideograph; background: url('/Assets/img/content/bg_watermark.png') transparent;background-position-x: center;background-repeat: repeat-y;"><a type="dir" name="WBSB"></a><div style="TEXT-ALIGN: center; LINE-HEIGHT: 25pt; MARGIN: 0.5pt 0cm; FONT-FAMILY: 宋体; FONT-SIZE: 22pt;">江苏省泰兴市人民法院</div><div style="TEXT-ALIGN: center; LINE-HEIGHT: 30pt; MARGIN: 0.5pt 0cm; FONT-FAMILY: 仿宋; FONT-SIZE: 26pt;">刑 事 判 决 书</div><div style="TEXT-ALIGN: right; LINE-HEIGHT: 30pt; MARGIN: 0.5pt 0cm;  FONT-FAMILY: 仿宋;FONT-SIZE: 16pt; ">（2017）苏1283刑初44号</div><a type="dir" name="DSRXX"></a><div style="LINE-HEIGHT: 25pt;TEXT-ALIGN:justify;TEXT-JUSTIFY:inter-ideograph; TEXT-INDENT: 30pt; MARGIN: 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;">公诉机关泰兴市人民检察院。</div><div style="LINE-HEIGHT: 25pt;TEXT-ALIGN:justify;TEXT-JUSTIFY:inter-ideograph; TEXT-INDENT: 30pt; MARGIN: 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;">被告人王某，男，大专文化，个体经营，曾因寻衅滋事，于2007年8月7日被泰州市公安局高港分局行政拘留十日；因犯聚众斗殴罪、寻衅滋事罪，于2009年7月15日被本院判处有期徒刑三年九个月，2011年5月26日刑满释放；因吸毒，分别于2012年4月25日、2013年3月1日被泰兴市公安局行政拘留五日、十五日；因吸毒，于2013年3月11日被泰兴市公安局决定社区戒毒三年；因吸毒，于2016年10月21日被泰兴市公安局行政拘留十五日。因本案，于2016年11月5日被泰兴市公安局刑事拘留，同年12月12日被逮捕。</div><div style="LINE-HEIGHT: 25pt;TEXT-ALIGN:justify;TEXT-JUSTIFY:inter-ideograph; TEXT-INDENT: 30pt; MARGIN: 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;">辩护人蒋春林，江苏银杏树律师事务所律师。</div><a type="dir" name="SSJL"></a><div style="LINE-HEIGHT: 25pt;TEXT-ALIGN:justify;TEXT-JUSTIFY:inter-ideograph; TEXT-INDENT: 30pt; MARGIN: 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;">泰兴市人民检察院以泰检诉刑诉[2017]31号起诉书指控被告人王某犯容留他人吸毒罪，于2017年2月8日向本院提起公诉。本院依法适用简易程序，实行独任审判，公开开庭审理了本案。泰兴市人民检察院检察员孙乐、被告人王某及其辩护人蒋春林到庭参加诉讼。现已审理终结。</div><a type="dir" name="AJJBQK"></a><div style="LINE-HEIGHT: 25pt;TEXT-ALIGN:justify;TEXT-JUSTIFY:inter-ideograph; MARGIN: 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;">公诉机关指控：</div><div style="LINE-HEIGHT: 25pt;TEXT-ALIGN:justify;TEXT-JUSTIFY:inter-ideograph; TEXT-INDENT: 30pt; MARGIN: 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;">被告人王某于2016年9月底至10月12日期间，在其经营的店三楼，容留张某、范某采用冰壶烤吸的方式，吸食由张某提供的甲基苯丙胺（俗称“冰毒”）共3次。具体分述如下：</div><div style="LINE-HEIGHT: 25pt;TEXT-ALIGN:justify;TEXT-JUSTIFY:inter-ideograph; TEXT-INDENT: 30pt; MARGIN: 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;">1、2016年9月底的一天下午，被告人王某在上述地点三楼东侧房间内，容留张某采用冰壶烤吸的方式吸食由张某提供的冰毒1次。</div><div style="LINE-HEIGHT: 25pt;TEXT-ALIGN:justify;TEXT-JUSTIFY:inter-ideograph; TEXT-INDENT: 30pt; MARGIN: 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;">2、2016年10月初的一天下午，被告人王某在上述地点三楼东侧房间内，容留张某采用冰壶烤吸的方式吸食由张某提供的冰毒1次。</div><div style="LINE-HEIGHT: 25pt;TEXT-ALIGN:justify;TEXT-JUSTIFY:inter-ideograph; TEXT-INDENT: 30pt; MARGIN: 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;">3、2016年10月12日晚上，被告人王某在上述地点三楼西侧房间内，容留张某、范某采用冰壶烤吸的方式吸食由张某提供的冰毒1次。</div><div style="LINE-HEIGHT: 25pt;TEXT-ALIGN:justify;TEXT-JUSTIFY:inter-ideograph; TEXT-INDENT: 30pt; MARGIN: 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;">案发后，被告人王某自动投案，并如实供述了上述犯罪事实。</div><div style="LINE-HEIGHT: 25pt;TEXT-ALIGN:justify;TEXT-JUSTIFY:inter-ideograph; TEXT-INDENT: 30pt; MARGIN: 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;">审理中，被告人王某主动向本院缴纳财产刑执行保证金人民币6000元。</div><div style="LINE-HEIGHT: 25pt;TEXT-ALIGN:justify;TEXT-JUSTIFY:inter-ideograph; TEXT-INDENT: 30pt; MARGIN: 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;">上述事实，被告人王某在开庭审理过程中亦无异议，且有证人张某、范某、何某的证言，公安机关依法调取的常住人口登记表、行政处罚决定书、刑事判决书、释放证明，出具的接处警工作登记表、受案登记表、立案决定书、归案情况说明，制作的辨认笔录、现场勘验检查工作记录及拍摄的相关照片等证据证实，足以认定。</div><a type="dir" name="CPYZ"></a><div style="LINE-HEIGHT: 25pt;TEXT-ALIGN:justify;TEXT-JUSTIFY:inter-ideograph; TEXT-INDENT: 30pt; MARGIN: 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;">本院认为，被告人王某为他人吸食毒品提供场所，其行为已构成容留他人吸毒罪，依法应予惩处。泰兴市人民检察院对被告人王某犯容留他人吸毒罪的指控成立，本院予以支持。被告人王某自动投案并如实供述自己的罪行，是自首，依法可以从轻处罚。被告人王某具有犯罪前科和多次吸毒劣迹，可酌情从重处罚。被告人王某主动向本院缴纳财产刑执行保证金，可酌情从轻处罚。关于辩护人提出“被告人王某具有自首、主动缴纳财产刑执行保证金等法定和酌定从轻处罚的情节，建议对被告人王某从轻处罚”的辩护意见，经查属实，本院予以采纳。依照《中华人民共和国刑法》第三百五十四条、第三百五十七条第一款、第六十七条第一款之规定，判决如下：</div><a type="dir" name="PJJG"></a><div style="LINE-HEIGHT: 25pt;TEXT-ALIGN:justify;TEXT-JUSTIFY:inter-ideograph; TEXT-INDENT: 30pt; MARGIN: 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;">被告人王某犯容留他人吸毒罪，判处有期徒刑六个月，并处罚金人民币六千元。</div><div style="LINE-HEIGHT: 25pt;TEXT-ALIGN:justify;TEXT-JUSTIFY:inter-ideograph; TEXT-INDENT: 30pt; MARGIN: 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;">（刑期从判决执行之日起计算；判决执行以前先行羁押的，羁押一日折抵刑期一日，即自2016年11月5日起至2017年5月4日止）。</div><div style="LINE-HEIGHT: 25pt;TEXT-ALIGN:justify;TEXT-JUSTIFY:inter-ideograph; TEXT-INDENT: 30pt; MARGIN: 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;">如不服本判决，可在接到判决书的第二日起十日内，通过本院或者直接向江苏省泰州市中级人民法院提出上诉。书面上诉的，应当提交上诉状正本一份，副本两份。</div><a type="dir" name="WBWB"></a><div style="TEXT-ALIGN: right; LINE-HEIGHT: 25pt; MARGIN: 0.5pt 72pt 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;">审判员　　端学锋</div><br /><div style="TEXT-ALIGN: right; LINE-HEIGHT: 25pt; MARGIN: 0.5pt 72pt 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;">二〇一七年二月二十一日</div><div style="TEXT-ALIGN: right; LINE-HEIGHT: 25pt; MARGIN: 0.5pt 72pt 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;">书记员　　陆　玉</div><div style="LINE-HEIGHT: 25pt;TEXT-ALIGN:justify;TEXT-JUSTIFY:inter-ideograph; TEXT-INDENT: 30pt; MARGIN: 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;">附录：</div><div style="LINE-HEIGHT: 25pt;TEXT-ALIGN:justify;TEXT-JUSTIFY:inter-ideograph; TEXT-INDENT: 30pt; MARGIN: 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;">《中华人民共和国刑法》</div><div style="LINE-HEIGHT: 25pt;TEXT-ALIGN:justify;TEXT-JUSTIFY:inter-ideograph; TEXT-INDENT: 30pt; MARGIN: 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;">第三百五十四条容留他人吸食、注射毒品的，处三年以下有期徒刑、拘役或者管制，并处罚金。</div><div style="LINE-HEIGHT: 25pt;TEXT-ALIGN:justify;TEXT-JUSTIFY:inter-ideograph; TEXT-INDENT: 30pt; MARGIN: 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;">第三百五十七条第一款本法所称的毒品，是指鸦片、海洛因、甲基苯丙胺（冰毒）、吗啡、大麻、可卡因以及国家规定管制的其他能够使人形成瘾癖的麻醉药品和精神药品。</div><div style="LINE-HEIGHT: 25pt;TEXT-ALIGN:justify;TEXT-JUSTIFY:inter-ideograph; TEXT-INDENT: 30pt; MARGIN: 0.5pt 0cm;FONT-FAMILY: 仿宋; FONT-SIZE: 16pt;">第六十七条第一款犯罪以后自动投案，如实供述自己的罪行的，是自首。对于自首的犯罪分子，可以从轻或者减轻处罚。其中，犯罪较轻的，可以免除处罚。</div></div>
                            </div>
                        </div>
                    </div>
                    <div id="divTool" class="content_tool_right ">
                        <div>
                            <div id="divTool_Summary" class="right">
                            <ul><li class="attribute"><a href="#" class="outline tool_dir_common">概要</a><div class="info"><div class="con"><div class="icon"><img src="/Assets/img/content/content_directory_spot2.png" data-bd-imgshare-binded="1" /></div><div class="content_tool_common"> <div class="content_info_common">基本信息</div> </div><div class="relateinfo"><table class="table_info"><tbody><tr><th>  审理法院：</th><td><a target="_blank" href="/List/List?sorttype=1&amp;conditions=searchWord++法院名称+江苏省泰兴市人民法院+法院名称:江苏省泰兴市人民法院">江苏省泰兴市人民法院</a></td></tr><tr><th>  案件类型：</th><td><a target="_blank" href="/List/List?sorttype=1&amp;conditions=searchWord++案件类型+刑事案件+案件类型:刑事案件">刑事案件</a></td></tr><tr><th>  案由：</th><td><a target="_blank" href="/List/List?sorttype=1&amp;conditions=searchWord++案由+容留他人吸毒+案由:容留他人吸毒">容留他人吸毒</a></td></tr><tr><th>  审理程序：</th><td>一审</td></tr><tr><th>  裁判日期：</th><td>2017-02-21</td></tr><tr><th>  公诉机关：</th><td>泰兴市人民检察院</td></tr><tr><th>  当事人：</th><td>王某</td></tr></tbody></table></div><div class="content_tool_common"> <div class="content_info_common">法律依据</div> </div><div class="relateinfo">   <table> <tbody><tr>        <td clss="relate_doc_td2">  《中华人民共和国刑法》</td> </tr> <tr>        <td clss="relate_doc_td2">    <a name="actItem" href="javascript:void(0);">第三百五十四条</a></td> </tr> <tr>        <td clss="relate_doc_td2">    <a name="actItem" href="javascript:void(0);">第三百五十七条</a></td> </tr> <tr>        <td clss="relate_doc_td2">    <a name="actItem" href="javascript:void(0);">第六十七条</a></td> </tr>  </tbody></table></div><div class="icon"><img src="/Assets/img/content/content_directory_spot2.png" data-bd-imgshare-binded="1" /></div></div></div></li></ul></div>
                            <div id="divTool_Share" class="div_tool_share">
                            <div class="tool_share"><div class="">      <div class="bdsharebuttonbox bdshare-temp bdshare-button-style0-16" id="share" data-bd-bind="1497798593118"><img id="imgtool" src="/Assets/img/content/close.png" title="关闭" style="cursor: pointer;" data-bd-imgshare-binded="1" /><a title="通过中国司法案例网身份认证的会员（主要包括法官、律师、法律学者、法律院校学生）才能推荐裁判文书到中国司法案例网，经全体会员众筹投票，符合条件可收入最高人民法院司法案例库" id="btnalfx" href="javascript:void(0);"></a><a id="fx" title="点击进行分享" data-cmd="more" href="javascript:void(0);"></a></div><div class=""><a title="点击进行留言" id="comment" style="cursor:pointer;"><img src="../../Assets/img/content/content_comment.jpg" data-bd-imgshare-binded="1" /></a></div></div></div><div id="tdcShow" style="cursor:pointer;" class="totop"><img src="../../Assets/img/content/content_tdc_show.png" data-bd-imgshare-binded="1" /></div><div id="totop" class="totop"><a id="comment"><img src="../../Assets/img/content/content_totop.png" data-bd-imgshare-binded="1" /></a></div></div>
                        </div>
                    </div>
                    <div id="divNotice" class="content_notice">
                        <div class="content_notice_head">
                            公 告</div>
                        <div class="content_notice_body">
                                   一、本裁判文书库公布的裁判文书由相关法院录入和审核，并依据法律与审判公开的原则予以公开。若有关当事人对相关信息内容有异议的，可向公布法院书面申请更正或者下镜。
                            <br />        二、本裁判文书库提供的信息仅供查询人参考，内容以正式文本为准。非法使用裁判文书库信息给他人造成损害的，由非法使用人承担法律责任。
                            <br />        三、本裁判文书库信息查询免费，严禁任何单位和个人利用本裁判文书库信息牟取非法利益。
                            <br />        四、未经允许，任何商业性网站不得建立本裁判文书库的镜像（包括全部和局部镜像）。
                            <br />        五、根据有关法律规定，相关法院依法定程序撤回在本网站公开的裁判文书的，其余网站有义务免费及时撤回相应文书。
                        </div>
                    </div>
                <div id="divLawItems" class="divcontent_comment display_none" style="width:auto;height:480px;position: absolute;top:261px;"><div class="content_comment_head"><table><tbody><tr><td class="info">法律依据</td><td class="close"><img style="cursor: pointer;" alt="点击关闭" src="../../Assets/img/content/content_comment_close.png" onclick="$('#divLawItems').hide();" data-bd-imgshare-binded="1" /></td></tr></tbody></table></div><div class="content_lawitems_body" style="height:456px;overflow-y:auto;"><table id="comment_item_table"><tbody><tr class="comment_font">       <td>          《中华人民共和国刑法》       </td></tr><tr class="comment_font"><td>    第三百五十四条　容留他人吸食、注射毒品的，处三年以下有期徒刑、拘役或者管制，并处罚金。<br /></td></tr><tr class="comment_font"><td>    第三百五十七条　本法所称的毒品，是指鸦片、海洛因、甲基苯丙胺（冰毒）、吗啡、大麻、可卡因以及国家规定管制的其他能够使人形成瘾癖的麻醉药品和精神药品。<br />    毒品的数量以查证属实的走私、贩卖、运输、制造、非法持有毒品的数量计算，不以纯度折算。<br /></td></tr><tr class="comment_font"><td>    第六十七条　犯罪以后自动投案，如实供述自己的罪行的，是自首。对于自首的犯罪分子，可以从轻或者减轻处罚。其中，犯罪较轻的，可以免除处罚。<br />    被采取强制措施的犯罪嫌疑人、被告人和正在服刑的罪犯，如实供述司法机关还未掌握的本人其他罪行的，以自首论。<br />    犯罪嫌疑人虽不具有前两款规定的自首情节，但是如实供述自己罪行的，可以从轻处罚；因其如实供述自己罪行，避免特别严重后果发生的，可以减轻处罚。<br /></td></tr><tr class="comment_font"><td>    第六十七条　犯罪以后自动投案，如实供述自己的罪行的，是自首。对于自首的犯罪分子，可以从轻或者减轻处罚。其中，犯罪较轻的，可以免除处罚。<br />    被采取强制措施的犯罪嫌疑人、被告人和正在服刑的罪犯，如实供述司法机关还未掌握的本人其他罪行的，以自首论。<br /></td></tr><tr class="comment_font"><td><div class="lawitems_statement"><div class="statement_head">免责声明</div><div class="statement_body">      法律依据仅供参考，如有需要，请您在核实裁判文书与相应法律、法规版本后慎重使用，并自行承担法律后果。</div></div></td></tr></tbody></table></div></div></div>
                <div id="divContent_comment" class="divcontent_comment display_none" style="top: 30%;&#10;                    left: 30%;">
                    <div class="content_comment_head">
                        <table>
                            <tbody><tr>
                                <td class="info">
                                    我要留言
                                </td>
                                <td class="close">
                                    <img style="cursor: pointer;" onclick=" $('.divcontent_comment').hide();$('#comment').find('img:first').attr('src', '/Assets/img/content/content_comment.jpg');" alt="点击关闭留言框" src="/Assets/img/content/content_comment_close.png" data-bd-imgshare-binded="1" />
                                </td>
                            </tr>
                        </tbody></table>
                    </div>
                    <div class="content_comment_body">
                        <table>
                            <tbody><tr class="source_info comment_font">
                                <td style="width: 15%;">
                                    <div style="height: 100%;">
                                        留言来源：</div>
                                </td>
                                <td style="width: 85%;" id="tdSource">
                                    王某容留他人吸毒罪一审刑事判决书 （2017）苏1283刑初44号
                                </td>
                            </tr>
                            <tr class="comment_info comment_font">
                                <td>
                                    留言内容：
                                </td>
                                <td>
                                    <textarea id="commentArea" maxlength="200" style="width: 320px;"></textarea>(200字以内)
                                </td>
                            </tr>
                            <tr class="comment_btn">
                                <td style="text-align: center;" colspan="2">
                                    <input type="button" value="提交" class="button" onclick="Content.Comment.LeaveWords_Save();" />
                                          
                                    <input type="button" value="重置" class="button" onclick="Content.Comment.LeaveWords_Reset();" />
                                </td>
                            </tr>
                        </tbody></table>
                    </div>
                </div>
                <div id="divtdc" class="divcontent_comment display_none" style="top: 25%; left: 35%;&#10;                    width: 400px; height: 380px; background-color: #FFFFFF;">
                    <div class="content_comment_head">
                        <table>
                            <tbody><tr>
                                <td class="info">
                                    二维码
                                </td>
                                <td class="close">
                                    <img style="cursor: pointer;" onclick=" $('#divtdc').hide();" alt="点击关闭二维码扫描" src="/Assets/img/content/content_comment_close.png" data-bd-imgshare-binded="1" />
                                </td>
                            </tr>
                        </tbody></table>
                    </div>
                    <div class="content_comment_body">
                        <div id="tdc" style="height: 200px; width: 200px; margin: 50px 50px 50px 80px; text-align: center;">
                        <canvas width="240" height="240" style="display: none;"></canvas><img alt="Scan me!" style="display: block;" src="data:image/png;base64,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" data-bd-imgshare-binded="1" /></div>
                    </div>
                </div>
                <div id="divtdcApp" class="divcontent_comment display_none" style="top: 25%; left: 35%; width: 400px; height: 380px; background-color: rgb(255, 255, 255); z-index: 99999;"> <div class="content_comment_head"><table><tbody><tr><td class="info">APP二维码</td><td class="close"><img style="cursor: pointer;" onclick=" $('#divtdcApp').hide();" alt="点击关闭二维码扫描" src="/Assets/img/content/content_comment_close.png" data-bd-imgshare-binded="1" /></td></tr></tbody></table></div><div class="content_comment_body"><div id="tdcApp" style="height: 200px; width: 200px; margin: 20px 50px; text-align: center;"><img src="/MobilePage/images/cpwswApp.png" width="300px" heigth="300px" data-bd-imgshare-binded="1" /></div></div></div>
        </div>
        <script src="/Assets/js/Lawyee.CPWSW.PageFooter.js" type="text/javascript"></script> <div id="bottom" class="bottom">   <div class="container3" style="font-size:16px;margin-top:10px;font-weight:bold;">      中华人民共和国最高人民法院 版权所有<p></p>   </div>   <div class="container3" style="font-size:14px;margin-top:5px;font-weight:bold;">       地址：北京市东城区东交民巷27号    邮编：100745    总机：010-67550114      </div>   <div class="container3" style="font-size:14px;margin-top:5px;font-weight:bold;">       京ICP备05023036号   </div> <div class="container containerFisrt" style="padding-top:0px;margin-top:5px;">   |<a href="http://govinfo.nlc.gov.cn" target="_blank">中国政府公开信息整合服务平台</a>|<a href="http://www.ajxxgk.jcy.cn/html/index.html" target="_blank">人民检察院案件信息公开网</a>|  </div>   <div class="container">        |<a href="http://www.court.gov.cn/zgsplcxxgkw/" target="_blank">中国审判流程信息公开网</a>|<a href="http://shixin.court.gov.cn" target="_blank">中国执行信息公开网</a>|<a href="http://ipr.court.gov.cn" target="_blank">中国知识产权裁判文书网</a>|<a href="http://www.ccmt.org.cn" target="_blank">中国涉外商事海事审判网</a>|<a href="http://www.court.gov.cn/qgfyjxjszyjwzxxxw/" target="_blank">全国法院减刑、假释、暂予监外执行信息网</a>|    </div> </div>
    </div>
    <input type="hidden" id="hidDocID" value="f42dfa1f-b5ca-4a22-a416-a74300f61906" />
    <input type="hidden" id="hidRequireLogin" value="0" />
    <input type="hidden" id="hidCaseName" value="王某容留他人吸毒罪一审刑事判决书" />
    <input type="hidden" id="hidCaseNumber" value="（2017）苏1283刑初44号" />
    <input type="hidden" id="hidCaseInfo" value="{&quot;法院ID&quot;:&quot;-1&quot;,&quot;审判程序&quot;:&quot;一审&quot;,&quot;案号&quot;:&quot;（2017）苏1283刑初44号&quot;,&quot;法院地市&quot;:&quot;泰兴市&quot;,&quot;法院省份&quot;:&quot;江苏省&quot;,&quot;文本首部段落原文&quot;:&quot;&quot;,&quot;法院区域&quot;:&quot;&quot;,&quot;文书ID&quot;:&quot;f42dfa1f-b5ca-4a22-a416-a74300f61906&quot;,&quot;案件名称&quot;:&quot;王某容留他人吸毒罪一审刑事判决书&quot;,&quot;法院名称&quot;:&quot;江苏省泰兴市人民法院&quot;,&quot;裁判要旨段原文&quot;:&quot;&quot;,&quot;法院区县&quot;:&quot;&quot;,&quot;DocContent&quot;:&quot;&quot;,&quot;补正文书&quot;:&quot;2&quot;,&quot;诉讼记录段原文&quot;:&quot;泰兴市人民检察院以泰检诉刑诉［2017］31号起诉书指控被告人王某犯容留他人吸毒罪，于2017年2月8日向本院提起公诉。本院依法适用简易程序，实行独任审判，公开开庭审理了本案。泰兴市人民检察院检察员孙乐、被告人王某及其辩护人蒋春林到庭参加诉讼。现已审理终结&quot;,&quot;判决结果段原文&quot;:&quot;&quot;,&quot;文本尾部原文&quot;:&quot;&quot;,&quot;上传日期&quot;:&quot;\/Date(1490630400000)\/&quot;,&quot;案件类型&quot;:&quot;1&quot;,&quot;诉讼参与人信息部分原文&quot;:&quot;&quot;,&quot;文书类型&quot;:null,&quot;文书全文类型&quot;:&quot;1&quot;,&quot;裁判日期&quot;:null,&quot;结案方式&quot;:null,&quot;效力层级&quot;:null,&quot;不公开理由&quot;:&quot;&quot;,&quot;案件基本情况段原文&quot;:&quot;&quot;,&quot;附加原文&quot;:&quot;附录：&#10;《中华人民共和国刑法》&#10;第三百五十四条容留他人吸食、注射毒品的，处三年以下有期徒刑、拘役或者管制，并处罚金。&#10;第三百五十七条第一款本法所称的毒品，是指鸦片、海洛因、甲基苯丙胺（冰毒）、吗啡、大麻、可卡因以及国家规定管制的其他能够使人形成瘾癖的麻醉药品和精神药品。&#10;第六十七条第一款犯罪以后自动投案，如实供述自己的罪行的，是自首。对于自首的犯罪分子，可以从轻或者减轻处罚。其中，犯罪较轻的，可以免除处罚&quot;}" />
    <input type="hidden" id="hidCourt" value="江苏省泰兴市人民法院" />
    <input type="hidden" id="hidCaseType" value="1" />
    <input type="hidden" id="HidCourtID" value="-1" />
    <input type="hidden" id="hidPageType" value="CPWSW" />


<iframe frameborder="0" id="bdSharePopup_selectshare1497798593108bg" class="bdselect_share_bg" style="display:none;"></iframe><div id="bdSharePopup_selectshare1497798593108box" style="display:none;" share-type="selectshare" class="bdselect_share_box" data-bd-bind="1497798593107"><div class="selectshare-mod-triangle"><div class="triangle-border"></div><div class="triangle-inset"></div></div><div class="bdselect_share_head"><span>分享到</span><a href="http://www.baidu.com/s?wd=&amp;tn=SE_hldp08010_vurs2xrp" class="bdselect_share_dialog_search" target="_blank"><i class="bdselect_share_dialog_search_i"></i><span class="bdselect_share_dialog_search_span">百度一下</span></a><a class="bdselect_share_dialog_close"></a></div><div class="bdselect_share_content"><ul class="bdselect_share_list bdshare-button-style0-16"><div class="bdselect_share_partners"></div><a href="#" class="bds_more" data-cmd="more"></a></ul></div></div><div id="bdimgshare_1497798593127" class="sr-bdimgshare sr-bdimgshare-list sr-bdimgshare-16 sr-bdimgshare-black" style="height:36px;line-height:26px;font-size:12px;width:autopx;display:none;" data-bd-bind="1497798593127"><div class="bdimgshare-bg"></div><div class="bdimgshare-content bdsharebuttonbox bdshare-button-style0-16"><label class="bdimgshare-lbl">分享到：</label><a href="#" onclick="return false;" class="bds_qzone" data-cmd="qzone" hidefocus=""></a><a href="#" onclick="return false;" class="bds_tsina" data-cmd="tsina" hidefocus=""></a><a href="#" onclick="return false;" class="bds_tqq" data-cmd="tqq" hidefocus=""></a><a href="#" onclick="return false;" class="bds_renren" data-cmd="renren" hidefocus=""></a><a href="#" onclick="return false;" class="bds_weixin" data-cmd="weixin" hidefocus=""></a><a href="#" onclick="return false;" class="bds_more" data-cmd="more" hidefocus=""></a></div></div></body></html>
Cookie str: FSSBBIl1UgzbN7N80T=10w00qFXGsv9KaTMNkGoJb6QP1PnOFRAyGoGhRCqY_OjfEAF.wgIrV6ZIlBQuJZj0LWfWF.y88eP8YDVpWdIuayuB0Y5Ku.JDLrcp2GnftuYAaGZAahqRpUlBGpm9exeIXaLJfhNPOkc8xdVfCKZQiiYO99uw7pOEFrD1uiwAzPnzVsoB02uuIuK21re_ln1TyoVmHK8_ZO5i12QVc1AYtuIJzJcmr8BMKn2EUsMo.5pVgsLga_Ta4u8d.1dIopTxNu0U.WYeExRyXB3MxFYEkRDvLT6IFC6EfN0ovbEMIHs1b7v45jCO6Md9Hej7zPbzprhpys9Qo35nE7kbACLmueyp; _gscs_2116842793=97798592quzhos87|pv:1; _gscu_2116842793=97798592pst43j87; Hm_lpvt_3f1a54c5a86d62407544d433f6418ef5=1497798593; Hm_lvt_3f1a54c5a86d62407544d433f6418ef5=1497798593; _gscbrs_2116842793=1; FSSBBIl1UgzbN7N80S=kMATDyW1f7OFJPW__a8yQ9EhTWDjyvxoLnxJ8fd0oThlwhyP4WhBPVKslbMUZxGA;
"[{\"Count\":\"26\"},{\"裁判要旨段原文\":\"本院认为，上诉人陈旭豪违反海关法规，逃避海关监管，走私枪支7支、枪支零部件2件，其行为已构成走私武器罪。陈旭豪为少许报酬受他人雇请走私枪支入境，在共同犯罪中起次要作用，是从犯，依法应当减轻处罚。陈旭豪归案后认罪态度较好，依法可以从轻处罚。原审判决认定事实清楚，证据确实、充分，定罪准确，量刑适当，审判程序合法。陈旭豪的上诉理由不成立，不予采纳。依照《中华人民共和国刑法》第一百五十一条第一款、第二十七条、第六十一条、第六十七条第三款、第六十三条、第六十四条及《最高人民法院、最高人民检察院关于办理走私刑事案件适用法律若干问题的解释》第一条第二款及《中华人民共和国刑事诉讼法》第二百二十五条第一款第（一）项之规定，裁定如下\",\"不公开理由\":\"\",\"案件类型\":\"1\",\"裁判日期\":\"2017-04-01\",\"案件名称\":\"陈旭豪走私武器二审刑事裁定书\",\"文书ID\":\"0ce000b3-bacf-4af6-820d-a7680093cdc7\",\"审判程序\":\"二审\",\"案号\":\"（2017）粤刑终215号\",\"法院名称\":\"广东省高级人民法院\"},{\"裁判要旨段原文\":\"本院认为，该犯在死刑缓期执行期间，没有故意犯罪，符合减刑条件，应予减刑。依照《中华人民共和国刑法》第七十九条、第五十条、第五十七条第一款和《中华人民共和国刑事诉讼法》第二百五十条第二款的规定，裁定如下\",\"不公开理由\":\"\",\"案件类型\":\"1\",\"裁判日期\":\"2017-04-01\",\"案件名称\":\"罪犯曹永贩卖运输毒品罪刑罚变更刑事裁定书\",\"文书ID\":\"d7414944-781d-461e-96cf-a76f00ac7987\",\"审判程序\":\"刑罚变更\",\"案号\":\"（2017）云刑更25号\",\"法院名称\":\"云南省高级人民法院\"},{\"裁判要旨段原文\":\"本院认为，上诉人杨庆林故意非法剥夺他人生命，其行为已构成故意杀人罪。原审判决认定事实清楚，证据确实充分，定罪准确，量刑及附带民事部分判决适当。审判程序合法。但未认定杨庆林具有自首情节不当，本院予以纠正。依照《中华人民共和国刑事诉讼法》第二百二十五条第一款第（一）项及《中华人民共和国民事诉讼法》第一百七十条第一款第（一）项之规定，裁定如下\",\"不公开理由\":\"\",\"案件类型\":\"1\",\"裁判日期\":\"2017-04-01\",\"案件名称\":\"黄某1、王某1故意杀人二审刑事裁定书\",\"文书ID\":\"a2ad51a2-6b0a-4e45-be65-a7710123b9cd\",\"审判程序\":\"二审\",\"案号\":\"（2017）鄂刑终3号\",\"法院名称\":\"湖北省高级人民法院\"},{\"裁判要旨段原文\":\"本院认为，该犯在死刑缓期执行期间，没有故意犯罪，符合减刑条件，应予减刑。依照《中华人民共和国刑法》第七十九条、第五十条、第五十七条第一款和《中华人民共和国刑事诉讼法》第二百五十条第二款的规定，裁定如下\",\"不公开理由\":\"\",\"案件类型\":\"1\",\"裁判日期\":\"2017-04-01\",\"案件名称\":\"潘梅包走私、贩卖、运输、制造毒品刑罚变更刑事裁定书\",\"文书ID\":\"f9f56a85-559d-427b-872c-a77500957306\",\"审判程序\":\"刑罚变更\",\"案号\":\"（2017）云刑更35号\",\"法院名称\":\"云南省高级人民法院\"},{\"不公开理由\":\"涉及国家秘密的\",\"案件类型\":\"1\",\"裁判日期\":\"2017-04-01\",\"案件名称\":\"司金长等人杀人案二审裁定.doc\",\"文书ID\":\"41c167a0-7246-4c0d-b62a-a74c01012962\",\"审判程序\":\"二审\",\"案号\":\"（2016）豫刑终394号\",\"法院名称\":\"河南省高级人民法院\"},{\"裁判要旨段原文\":\"本院认为，该犯在死刑缓期执行期间，没有故意犯罪，符合减刑条件，应予减刑。依照《中华人民共和国刑法》第七十九条、第五十条、第五十七条第一款和《中华人民共和国刑事诉讼法》第二百五十条第二款的规定，裁定如下\",\"不公开理由\":\"\",\"案件类型\":\"1\",\"裁判日期\":\"2017-04-01\",\"案件名称\":\"罪犯罗启权运输毒品罪刑罚变更刑事裁定书\",\"文书ID\":\"bb1fa221-81bb-4a16-8104-a76f00ac7a34\",\"审判程序\":\"刑罚变更\",\"案号\":\"（2017）云刑更14号\",\"法院名称\":\"云南省高级人民法院\"},{\"裁判要旨段原文\":\"本院认为，该犯在死刑缓期执行期间，没有故意犯罪，符合减刑条件，应予减刑。依照《中华人民共和国刑法》第七十九条、第五十条、第五十七条第一款和《中华人民共和国刑事诉讼法》第二百五十条第二款的规定，裁定如下\",\"不公开理由\":\"\",\"案件类型\":\"1\",\"裁判日期\":\"2017-04-01\",\"案件名称\":\"罪犯孔令胜走私运输毒品罪刑罚变更刑事裁定书\",\"文书ID\":\"8c353e3e-ea71-44aa-b613-a76f00ac78f5\",\"审判程序\":\"刑罚变更\",\"案号\":\"（2017）云刑更15号\",\"法院名称\":\"云南省高级人民法院\"},{\"裁判要旨段原文\":\"本院认为，该犯在死刑缓期执行期间，没有故意犯罪，符合减刑条件，应予减刑。依照《中华人民共和国刑法》第七十九条、第五十条、第五十七条第一款和《中华人民共和国刑事诉讼法》第二百五十条第二款的规定，裁定如下\",\"不公开理由\":\"\",\"案件类型\":\"1\",\"裁判日期\":\"2017-04-01\",\"案件名称\":\"罪犯赵祝明故意杀人罪刑罚变更刑事裁定书\",\"文书ID\":\"02c3b305-a47a-4f92-8e79-a76f00ac7ab7\",\"审判程序\":\"刑罚变更\",\"案号\":\"（2017）云刑更13号\",\"法院名称\":\"云南省高级人民法院\"},{\"不公开理由\":\"涉及国家秘密的\",\"案件类型\":\"1\",\"裁判日期\":\"2017-04-01\",\"案件名称\":\"ＸＸＸ裁定.doc\",\"文书ID\":\"256df0d6-d019-4a8f-aea5-a74c01019ef3\",\"审判程序\":\"二审\",\"案号\":\"（2017）豫刑终105号\",\"法院名称\":\"河南省高级人民法院\"},{\"不公开理由\":\"涉及国家秘密的\",\"案件类型\":\"1\",\"裁判日期\":\"2017-04-01\",\"案件名称\":\"孙培山裁定.doc\",\"文书ID\":\"93204f10-83b7-48cc-a7b2-a74c01019e0e\",\"审判程序\":\"复核\",\"案号\":\"（2017）豫刑核98621855号\",\"法院名称\":\"河南省高级人民法院\"},{\"不公开理由\":\"涉及国家秘密的\",\"案件类型\":\"1\",\"裁判日期\":\"2017-04-01\",\"案件名称\":\"董中善故意杀人案二审裁定.doc\",\"文书ID\":\"c38eb8a0-d669-4095-abe1-a74c010126a0\",\"审判程序\":\"二审\",\"案号\":\"（2016）豫刑终72号\",\"法院名称\":\"河南省高级人民法院\"},{\"裁判要旨段原文\":\"本院认为，该犯在死刑缓期执行期间，没有故意犯罪，符合减刑条件，应予减刑。依照《中华人民共和国刑法》第七十九条、第五十条、第五十七条第一款和《中华人民共和国刑事诉讼法》第二百五十条第二款的规定，裁定如下\",\"不公开理由\":\"\",\"案件类型\":\"1\",\"裁判日期\":\"2017-04-01\",\"案件名称\":\"罪犯董书卯运输毒品罪刑罚变更刑事裁定书\",\"文书ID\":\"d51be5a0-929b-4083-9277-a76f00ac7a47\",\"审判程序\":\"刑罚变更\",\"案号\":\"（2017）云刑更11号\",\"法院名称\":\"云南省高级人民法院\"},{\"裁判要旨段原文\":\"本院认为，该犯在死刑缓期执行期间，没有故意犯罪，符合减刑条件，应予减刑。依照《中华人民共和国刑法》第七十九条、第五十条、第五十七条第一款和《中华人民共和国刑事诉讼法》第二百五十条第二款的规定，裁定如下\",\"不公开理由\":\"\",\"案件类型\":\"1\",\"裁判日期\":\"2017-04-01\",\"案件名称\":\"罪犯赵兴忠运输毒品罪刑罚变更刑事裁定书\",\"文书ID\":\"106204aa-184b-452e-a5b9-a76f00ac7a83\",\"审判程序\":\"刑罚变更\",\"案号\":\"（2017）云刑更19号\",\"法院名称\":\"云南省高级人民法院\"},{\"裁判要旨段原文\":\"本院认为，该犯在死刑缓期执行期间，没有故意犯罪，符合减刑条件，应予减刑。依照《中华人民共和国刑法》第七十九条、第五十条、第五十七条第一款和《中华人民共和国刑事诉讼法》第二百五十条第二款的规定，裁定如下\",\"不公开理由\":\"\",\"案件类型\":\"1\",\"裁判日期\":\"2017-04-01\",\"案件名称\":\"罪犯张国云运输毒品罪刑罚变更刑事裁定书\",\"文书ID\":\"824af755-070b-43f8-bc2d-a76f00ac792b\",\"审判程序\":\"刑罚变更\",\"案号\":\"（2017）云刑更17号\",\"法院名称\":\"云南省高级人民法院\"},{\"裁判要旨段原文\":\"本院认为，被告人尹二闯骑三轮摩托车搭载他人发生交通事故后因害怕承担医疗费而故意非法剥夺他人生命，其行为构成故意杀人罪，且致一人死亡，情节恶劣，罪行严重，依法应予惩处。鉴于尹二闯的亲属能主动报案，尹二闯被抓获后能够如实供述犯罪事实，故对其判处死刑，可不立即执行。原审判决认定事实清楚，证据确实、充分，定罪准确，量刑适当，审判程序合法。依照《中华人民共和国刑法》第二百三十二条、第四十八条、第五十七条第一款、第六十七条第三款和《中华人民共和国刑事诉讼法》第二百三十七条之规定，裁定如下\",\"不公开理由\":\"\",\"案件类型\":\"1\",\"裁判日期\":\"2017-04-01\",\"案件名称\":\"尹二闯故意杀人复核刑事裁定书\",\"文书ID\":\"776c0bfc-2103-4e5b-84ad-a77f00c9e85a\",\"审判程序\":\"复核\",\"案号\":\"（2017）鲁刑核6号\",\"法院名称\":\"山东省高级人民法院\"},{\"裁判要旨段原文\":\"本院认为，该犯在死刑缓期执行期间，没有故意犯罪，符合减刑条件，应予减刑。依照《中华人民共和国刑法》第七十九条、第五十条、第五十七条第一款和《中华人民共和国刑事诉讼法》第二百五十条第二款的规定，裁定如下\",\"不公开理由\":\"\",\"案件类型\":\"1\",\"裁判日期\":\"2017-04-01\",\"案件名称\":\"罪犯阿胜马日运输毒品罪刑罚变更刑事裁定书\",\"文书ID\":\"11b889c1-402a-4156-b657-a775009573ee\",\"审判程序\":\"刑罚变更\",\"案号\":\"（2017）云刑更30号\",\"法院名称\":\"云南省高级人民法院\"},{\"不公开理由\":\"人民法院认为不宜在互联网公布的其他情形\",\"案件类型\":\"1\",\"裁判日期\":\"2017-04-01\",\"案件名称\":\"裁定张伟.doc\",\"文书ID\":\"fc946510-696a-4783-85c2-a75200f99791\",\"审判程序\":\"二审\",\"案号\":\"（2016）豫刑终583号\",\"法院名称\":\"河南省高级人民法院\"},{\"不公开理由\":\"涉及国家秘密的\",\"案件类型\":\"1\",\"裁判日期\":\"2017-04-01\",\"案件名称\":\"王连社复核裁定书\",\"文书ID\":\"e4706c35-e6e5-4322-a1a6-a75c01183833\",\"审判程序\":\"复核\",\"案号\":\"（2017）豫刑核17011701号\",\"法院名称\":\"河南省高级人民法院\"},{\"裁判要旨段原文\":\"本院认为，该犯在死刑缓期执行期间，没有故意犯罪，符合减刑条件，应予减刑。依照《中华人民共和国刑法》第七十九条、第五十条、第五十七条第一款和《中华人民共和国刑事诉讼法》第二百五十条第二款的规定，裁定如下\",\"不公开理由\":\"\",\"案件类型\":\"1\",\"裁判日期\":\"2017-04-01\",\"案件名称\":\"江日照走私、贩卖、运输、制造毒品刑罚变更刑事裁定书\",\"文书ID\":\"99cc26eb-c5db-47dc-bb1c-a775009572e5\",\"审判程序\":\"刑罚变更\",\"案号\":\"（2017）云刑更32号\",\"法院名称\":\"云南省高级人民法院\"},{\"裁判要旨段原文\":\"本院认为，该犯在死刑缓期执行期间，没有故意犯罪，符合减刑条件，应予减刑。依照《中华人民共和国刑法》第七十九条、第五十条、第五十七条第一款和《中华人民共和国刑事诉讼法》第二百五十条第二款的规定，裁定如下\",\"不公开理由\":\"\",\"案件类型\":\"1\",\"裁判日期\":\"2017-04-01\",\"案件名称\":\"阿苦体火走私、贩卖、运输、制造毒品刑罚变更刑事裁定书\",\"文书ID\":\"f185dabd-2399-4f76-baf3-a77500957403\",\"审判程序\":\"刑罚变更\",\"案号\":\"（2017）云刑更33号\",\"法院名称\":\"云南省高级人民法院\"}]"

Process finished with exit code 0

"""