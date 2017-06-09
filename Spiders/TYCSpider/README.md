### 爬取细节
1.
天眼查数据爬取需要两步:
 + 1).爬取公司对应的id(天眼查网站内部定义的一个id);
 + 2).通过id构建JSON字符串, 从而爬取所需要的软著数据
其中第1)步爬取公司对应的id: "http://www.tianyancha.com/v2/search/平安银行股份有限公司.json?"这个url通过浏览器是无法访问的, 但通过requests可以访问(但通过requests访问时User-Agent必须设置为Python/Javascript/Java等, 不能是具体的浏览器的User-Agent否则就无法抓取到). 第2)步可以通过浏览器直接访问, 也可以通过requests构建请求进行爬取

2.
专利数据: http://www.tianyancha.com/expanse/patent.json?id=22944923&pn=1&ps=5000
软著数据: http://www.tianyancha.com/expanse/copyReg.json?id=22944923&pn=1&ps=5000
url中的 pn: 第几页
        ps: pagesize, 每页有多少条数据


