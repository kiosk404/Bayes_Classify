# Bayes_Classify

本项目是一个文本分类的python项目。采用django封装了一个web界面。

![Image text](https://raw.githubusercontent.com/weijiaxiang007/Bayes_Classify/master/Assets/Image/pic01.png)

数据库是redis和sqlite3。 所以注意安装redis。收集到的文本都拆成了键值对存入redis

环境是python3 .运行前请打开redis，不要有密码，host设置为127.0.0.1 
pip -m requirements.txt

使用 python manager runserver 启动django 服务。点击菜单的操作界面。
注意，这个时候文本分类是没用的，因为redis里面没有数据。可以点击 运行爬虫来抓取
csdn的博客。等数据收集到一定步骤就可以文本分类了。

此文本分类为 贝叶斯算法。