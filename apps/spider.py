import re
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup
from django.shortcuts import get_object_or_404

from .cut_words import LoadData
import json
from .models import Article,Category

class Spider_html(object):
    def filter_tags(self, htmlstr):
        # 先过滤CDATA
        re_cdata = re.compile('//<!\[CDATA\[[^>]*//\]\]>', re.I)  # 匹配CDATA
        re_script = re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', re.I)  # Script
        re_style = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)  # style
        re_br = re.compile('<br\s*?/?>')  # 处理换行
        re_h = re.compile('</?\w+[^>]*>')  # HTML标签
        re_comment = re.compile('<!--[^>]*-->')  # HTML注释
        s = re_cdata.sub('', htmlstr)  # 去掉CDATA
        s = re_script.sub('', s)  # 去掉SCRIPT
        s = re_style.sub('', s)  # 去掉style
        s = re_br.sub('\n', s)  # 将br转换为换行
        s = re_h.sub('', s)  # 去掉HTML 标签
        s = re_comment.sub('', s)  # 去掉HTML注释
        # 去掉多余的空行
        blank_line = re.compile('\n+')
        s = blank_line.sub('\n', s)
        s = self.replaceCharEntity(s)  # 替换实体
        return s

    def replaceCharEntity(self, htmlstr):
        CHAR_ENTITIES = {'nbsp': ' ', '160': ' ',
                         'lt': '<', '60': '<',
                         'gt': '>', '62': '>',
                         'amp': '&', '38': '&',
                         'quot': '"', '34': '"', }

        re_charEntity = re.compile(r'&#?(?P<name>\w+);')
        sz = re_charEntity.search(htmlstr)
        while sz:
            entity = sz.group()  # entity全称，如&gt;
            key = sz.group('name')  # 去除&;后entity,如&gt;为gt
            try:
                htmlstr = re_charEntity.sub(CHAR_ENTITIES[key], htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
            except KeyError:
                # 以空串代替
                htmlstr = re_charEntity.sub('', htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
        return htmlstr

class Spider_man(Spider_html,LoadData):
    def __init__(self,url,category):
        super(Spider_man,self).__init__()
        self.base_url = url
        self.category = category

    def headers(self):
        Cookie = "uuid_tt_dd=7973822789280704112_20180404; smidV2=20180426192055a522902c733495421151e4bfda2e80d4004e36ab525d50a90; kd_user_id=e6e09a93-828e-447e-90c3-fe60b8f52680; dc_session_id=10_1525410033622.888758; TY_SESSION_ID=d8f41f5b-3a6d-4dfc-89d0-136add8d0b57; Hm_lvt_6bcd52f51e9b3dce32bec4a3997715ac=1522833755,1524741632,1525410035; ADHOC_MEMBERSHIP_CLIENT_ID1.0=a4863cff-a23d-74d9-c857-91c508065869; Hm_lpvt_6bcd52f51e9b3dce32bec4a3997715ac=1525410040; dc_tos=p86tx4; Hm_lvt_cdce8cda34e84469b1c8015204129522=1525410041; Hm_lpvt_cdce8cda34e84469b1c8015204129522=1525410041"
        headers = {
            'Accept': 'application / json, text / javascript, * / *; q = 0.01',
            'Accept - Encoding': 'gzip, deflate, br',
            'Accept - Language': 'en - US, en;q = 0.9',
            'Cache - Control': 'max - age = 0',
            'Connection': 'keep-alive',
            'Cookie': Cookie,
            'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
        }
        return headers

    def get_index(self):
        data = {
            'type': 'more',
            'category': self.category,
            'shown_offset': 0,
        }
        params = urlencode(data)
        base = self.base_url
        url = base + '?' + params
        try:
            response = requests.get(url, headers=self.headers())
            if response.status_code == 200:
                response.encoding = "utf-8"
                return json.loads(response.text)
            else:
                print("抓取JSON失败，错误代码： ",response.status_code)
            return None
        except ConnectionError:
            print('Error occurred')
            return None

    def get_detail(self,article_info):
        if article_info:
            url = article_info['url']
            title = article_info['title']
            auth_name = article_info['user_name']
            try:
                response = requests.get(url, headers=self.headers())
                if response.status_code == 200:
                    response.encoding = 'utf-8'
                    soup = BeautifulSoup(response.text, 'lxml')
                    html = str(soup.select(".markdown_views"))
                    data = self.filter_tags(html)
                    if data != "[]":
                        self.load_data(data)
                        cate_name = "csdn_"+self.category
                        category = Category.objects.filter(category=cate_name).first()
                        New_record = Article(title=title,author=auth_name,url=url,category=category)
                        New_record.save()
                else:
                    print("爬取文章失败，错误代码： ",response.status_code)
                return None
            except ConnectionError:
                print('Error occurred')
                return None
        else:
            return None

    def load_data(self,data):
        category = "csdn_"+self.category
        self.load_run(data,category)

    def parse_detail(self,res):
        if res['status'] == "true":
            for i in res['articles']:
                article_info = {
                    'title'     : i["title"],
                    'url'       : i["url"],
                    'created'   : i['created_at'],
                    'user_name' : i["user_name"],
                }
                self.get_detail(article_info)
        else:
            print("JSON数据解析失败 爬取出错了！！")

    def run_spider(self):
        res = self.get_index()
        self.parse_detail(res)