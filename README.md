# Bayes_Classify

本项目是一个文本分类的python项目。采用django封装了一个web界面。

![Image text](https://raw.githubusercontent.com/weijiaxiang007/Bayes_Classify/master/Assets/Image/pic01.png)

数据库是redis和sqlite3。 所以注意安装redis。收集到的文本都拆成了键值对存入redis

环境是python3.6 .运行前请打开redis，不要有密码，host设置为127.0.0.1 

pip -m requirements.txt

使用 python manager runserver 启动django 服务。点击菜单的操作界面。
注意，这个时候文本分类是没用的，因为redis里面没有数据。可以点击 运行爬虫来抓取
csdn的博客。等数据收集到一定步骤就可以文本分类了。

此文本分类为 贝叶斯算法。
目前的分类的准确率达到97%。分类对象都是从csdn网站上爬取的网站博客

安装运行可能出现的问题。
-------
nlpir初始化失败。--- 这是因为 nlpir 库需要每个月更新一次。需要从新去github上下载授权。可参考 http://blog.sina.com.cn/s/blog_7ad2a8d50102val9.html    
redis里面一定要放进去训练的样本。我会把redis中的数据上传到github上   
