# FinTech Spider
**_FinTech(i.e. Financial Technology)_**

"**FinTech Spider**" is a spider based on [Scrapy](https://scrapy.org/) to crawl a large number of financial data on the Internet.

The data crawled by "**FinTech Spider**" has been used by [嗅金牛](http://xiujinniu.com/xiujinniu/index.php), [数知源](http://datazhiyuan.com/datazhiyuan/index.php).


### Structrue of "FinTech Spider"
_Only important dirs & files are listed here._

| Directory/File | Author | Usage |
|------|:------:|------|
| **README.md** | [lxw](https://github.com/lxw0109) | The document for this project |
| | |
| **Anti_Anti_Spider/** | [hee](https://github.com/hee0624) | 验证码识别（滑块验证码/字符验证码） |
| | |
| **Demo/** |  | Some Demonstrations(e.g. PhantomJS/Proxies, etc.) |
| Demo/ArticleSpider/ | [hee](https://github.com/hee0624) | A demo for Scrapy spider project about lagou,zhihu,jobbol|
| Demo/CNKI_Patent/ | [lxw](https://github.com/lxw0109) | A demo for Scrapy spiders project which supports Selenium/PhantomJS/User-Agent/IP-Proxy |
| Demo/geetestcrack.py | [hee](https://github.com/hee0624) | 滑块验证码识别 |
| Demo/phantomjs_proxy.py | [lxw](https://github.com/lxw0109) | Add IP proxy in PhantomJS |
| Demo/user_agent.txt | [hee](https://github.com/hee0624) | A large number of User-Agents |
| | |
| **Spiders/** |  | The Spiders directory stores Python scripts that crawl data we need from the Internet) |
| Spiders/CJODocIDSpider/ | [lxw](https://github.com/lxw0109) | (w/ scrapy)Spiders for crawling data(case details) from [中国裁判文书网](http://wenshu.court.gov.cn/)(China Judgements Online) |
| Spiders/CJOSpider/ | [lxw](https://github.com/lxw0109) | (w/ scrapy)Spiders for crawling data(basic info) from [中国裁判文书网](http://wenshu.court.gov.cn/)(China Judgements Online) |
| Spiders/CninfoSpider/ | [hee](https://github.com/hee0624) | Spiders for crawling data from [巨潮资讯](http://www.cninfo.com.cn/cninfo-new/information/companylist) |
| Spiders/CNKI_Patent_Spider/ | [lxw](https://github.com/lxw0109) | (w/o scrapy)Spiders for crawling patent data from [中国知网](http://cnki.net/) |
| Spiders/NECIPSSpider/ | [lxw](https://github.com/lxw0109) | (w/ scrapy)Spiders for crawling data from [国家企业信用信息公示系统](http://www.gsxt.gov.cn/corp-query-homepage.html)(National Enterprise Credit Information Publicity System) |
| Spiders/new_three_board/ | [lxw](https://github.com/lxw0109) | (w/ scrapy)Spiders for crawling data from [全国中小企业股份转让系统](http://www.neeq.com.cn/nq/listedcompany.html) |
| Spiders/SBJSpider/ | [hee](https://github.com/hee0624) |  |
| Spiders/TYCSpider/ | [lxw](https://github.com/lxw0109) | (w scrapy, PhantomJS)Spiders for crawling patent/copyright data from [天眼查](http://www.tianyancha.com/) |


### TODO
**[He Chen](https://github.com/hee0624)**:
1. 在README.md中更新所提交的**关键**目录的用途(如果子目录中有关键的文件，也请列出)

**[Xiaowei Liu](https://github.com/lxw0109)**:
+ **CJOSpider**
 CJOSpider架构存在问题，把URL去重关闭了， 可能会存在重复抓取的问题

 0. 【比rpush可能会稍微好一点儿，这个暂时不改了，感觉怎么改都会有问题】proxy的获取策略改成lpop() + insert(第六个位置)，而不是lpop() + rpush()
 1. [NO, 按理说只用CJOSpider.py然后重新运行就可以] 增加对Redis中TASKS_HASH没有爬取结束任务的爬取代码(一定小于CONCURRENT_REQUESTS个?)
 2. [NO, 按理说只用CJODocIDSpider.py然后重新运行就可以] 增加对Redis中DOC_ID_HASH没有爬取结束任务的爬取代码

