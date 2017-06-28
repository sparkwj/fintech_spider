### 爬取细节
1.
天眼查数据爬取需要两步:
 + 1).爬取公司对应的id(天眼查网站内部定义的一个id);
 + 2).通过id构建JSON字符串, 从而爬取所需要的软著数据
其中第1)步爬取公司对应的id: "http://www.tianyancha.com/v2/search/平安银行股份有限公司.json?"这个url通过浏览器是无法访问的, 但通过requests可以访问(但通过requests访问时User-Agent必须设置为Python/Javascript/Java等, 不能是具体的浏览器的User-Agent否则就无法抓取到).
第2)步可以通过浏览器直接访问, 也可以通过requests构建请求进行爬取

2.

|板块|json url|备注|例子|
|------|------|------|
|专利|http://www.tianyancha.com/expanse/patent.json?id=22822&pn=1&ps=5000|可浏览器直接访问|{"state":"ok","message":"","special":"","vipMessage":"","isLogin":0,"data":{"viewtotal":"1512","items":[{"mainCatNum":"G10L15/06(2013.01)I","createTime":"1492028883000","updateTime":"0","applicationPublishNum":"CN103871404B","agency":"北京鸿德海业知识产权代理事务所(普通合伙) 11412","pid":"0e94e0dafaa6468f9d5a877970c00d64","inventor":"贾磊;万广鲁;","agent":"袁媛;","applicationPublishTime":"2017.04.12","imgUrl":"http://pic.cnipr.com:8080/XmlData/SQ/20170412/201210539598.2/201210539598.gif","patentNum":"CN201210539598.2","allCatNum":"G10L15/06(2013.01)I;","patentName":"一种语言模型的训练方法、查询方法和对应装置","abstracts":"本发明提供了一种语言模型的训练方法、查询方法和对应装置，其中训练方法包括：对训练语料进行分块得到N组训练语料，N为大于1的正整数；对分块得到的N组训练语料并行执行：进行递归的后缀树排序，分别得到反映各词语在各句子中倒序位置状况的排序结果，基于排序结果，将各句子中倒数第二个词作为根节点按照预设的第一词序结构分别建立n元词序树，n为预设的一个或多个大于1的正整数；对得到的相同根节点的词序树进行合并和词序转换后，得到存放前向概率信息的Trie树，该Trie树中从根到叶的词序顺序为：句子中倒数第二个词、最后一个词、其他词语按照倒序排列。通过本发明能够实现语言模型的快速更新。","address":"100085 北京市海淀区上地十街10号百度大厦2层","applicationTime":"2012.12.13","uuid":"0e94e0dafaa6468f9d5a877970c00d64","patentType":"发明专利","applicantName":"北京百度网讯科技有限公司;"}],"pageSize":"5000"}}|
|软件著作权|http://www.tianyancha.com/expanse/copyReg.json?id=22822&pn=1&ps=5000|可浏览器直接访问|{"state":"ok","message":"","special":"","vipMessage":"","isLogin":0,"data":{"viewtotal":"93","items":[{"createTime":"1496621453000","regtime":"1494950400000","authorNationality":"北京百度网讯科技有限公司:中国","publishtime":"1484582400000","simplename":"百度糯米","updateTime":"1496621453000","regnum":"2017SR185245","catnum":"30000-0000","pid":"1556690","fullname":"百度糯米IOS终端软件","version":"V7.1.0"}],"pageSize":"5000"}}|
|网站备案|http://www.tianyancha.com/v2/IcpList/22822.json|可浏览器直接访问|{"state":"ok","message":"","special":"","vipMessage":"","isLogin":0,"data":[{"webSite":["www.baidu.com"],"examineDate":"2017-03-07","companyType":"企业","webName":"百度","ym":"baidu.com","companyName":"北京百度网讯科技有限公司","liscense":"京ICP证030173号"}]}|

url中的 pn: 第几页
        ps: pagesize, 每页有多少条数据
