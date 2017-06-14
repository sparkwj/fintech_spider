### 数据检索策略
一.
1. abbr in full  
使用简称可以搜索到所有全称的, 但有些简称不是这家公司的(e.g. 飞亚达)
简称(结果里全称筛选)

2. abbr not in full  
都搜索(全称没问题, 简称不是这家公司的)

全 和 准 如何取舍:  
全称能够保证准确率(但有些公司申请时以简称申请导致查询不到, 例如中国工商银行/中国工商银行股份有限公司)
简称能够保证召回率(但有些简称指代的不是我们想要的公司)

二.  
海外专利是否需要? 中国工商银行能搜到  工商银行搜不到  
海外专利不要  


### 相关说明
1. CurRec 所有返回数据中的第几条数据(不是本页中的第几条数据)

2.
http://kns.cnki.net/kns/detail/detail.aspx?QueryID=0&CurRec=1&dbcode=SCPD&dbname=SCPD2017&filename=CN106506563A  
建行   账户设置方法、装置和银行服务系统

http://kns.cnki.net/kns/detail/detail.aspx?QueryID=13&CurRec=1&dbcode=SCPD&dbname=SCPD2017&filename=CN106503084A  
软件所   一种面向云数据库的非结构化数据的存储与管理方法

3.
Field: company_code||company_name||url||abbr/full  
        url:  
            "+": 检索页的初始页(当前公司的第一页)  
            "+?curpage=.....": 检索页的非初始页(不包含前缀http://kns.cnki.net/kns/brief/brief.aspx)  
            "-/kns/detail/detail.aspx?....": 详情页  
Value: flag  
         0: initial value  
        -1: Done. 当前请求成功.  
        -2: page_no/patent_no没有得到, url有问题. 以后再请求还是会有问题, 所以结束这一请求.  