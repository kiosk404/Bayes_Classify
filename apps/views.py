import json
import time
from django.http import HttpResponse
from django.shortcuts import render
from .models import Article,Category
from .spider import Spider_man
from django.conf import settings
from django.core.paginator import Paginator
from .forms import ArticleForm,CategoryForm
from .bayes import Naive_Bayes
from .nlpir import analysis_text
from .csdn_bayes import csdn_Bayes
from .redisdb import Redis_Go
from functools import reduce

# Create your views here.

class PageFunc():
    # filter_list 是过滤后的列表

    def __init__(self,filter_list):
        self.paginator = Paginator(filter_list, settings.EACHE_PAGE)  # 每5篇博客为一页

    # page_num 是当前页码
    def get_pagintor_info(self,page_num):
        last_page = self.paginator.num_pages
        page_num = page_num
        current_page_num = self.paginator.get_page(page_num).number  # 获取当前页码
        # 获取当前页码前后各2页
        page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                     list(range(current_page_num, min(current_page_num + 2, last_page) + 1))

        # 加上省略号
        if page_range[0] - 1 >= 2:
            page_range.insert(0, '...')
        if last_page - page_range[-1] >= 2:
            page_range.append('...')
        # 加上首页和尾页
        if page_range[0] != 1:
            page_range.insert(0, 1)
        if page_range[-1] != last_page:
            page_range.append(last_page)

        res = {
            'page_range' : page_range,
            'last_page'  : last_page,
        }

        return res

def index_view(request):
    return render(request,'index.html')

def workstation_view(request):
    category_count = Category.objects.count()
    text_count = Article.objects.count()
    cut_engine = "jieba"

    get_all = request.GET.get("show",1)
    if get_all == "all":
        articles = Article.objects.all()
    else:
        articles = PageFunc(Article.objects.all()).paginator.get_page("1")

    if text_count > 10000:
        text_count = text_count//10000
        text_count = str(text_count)+"w+"

    # 获取每个分类中有几篇样本
    categorys = Category.objects.all().order_by('category')
    categorys_list = []
    for category in categorys:
        category.count = Article.objects.filter(category=category).count()
        if category.category == "正常邮件":
            category.count = 7064 + int(category.count)
        elif category.category == "垃圾邮件":
            category.count = 7776 + int(category.count)
        categorys_list.append(category)

    data = {
        "cut_engine" : cut_engine,
        "text_count" : text_count,
        "category_count" : category_count,
        "articles" : articles,
        "categorys_list" : categorys_list
    }

    return render(request,'workstation.html',data)

def run_spider_view(request):
    # 获取每个分类中有几篇样本
    categorys = Category.objects.filter(category__contains="csdn")
    categorys_list = []
    for category in categorys:
        category.count = Article.objects.filter(category=category).count()
        categorys_list.append(category)

    articles = PageFunc(Article.objects.all()).paginator.get_page("1")

    context = {
        'category': categorys_list,
        'articles': articles,
    }
    return render(request,'run_spider.html',context)

def check_view(request):
    return render(request,'check.html')

def check_csdn_view(request):
    return render(request,'check_csdn.html')

def category_view(request):
    redis = Redis_Go(port=settings.REDIS_PORT, host=settings.REDIS_HOST)
    r = redis.redis_connection()

    # 获取每个分类中有几篇样本
    categorys = Category.objects.all().order_by('category')
    categorys_list = []
    for category in categorys:
        category.count = Article.objects.filter(category=category).count()
        if category.category == "正常邮件":
            category.count = 7064+int(category.count)
        elif category.category == "垃圾邮件":
            category.count = 7776+int(category.count)

        res_redis = r.hvals(category.category)  # 算出每个类别的总词数
        if len(res_redis) > 2:
            category.all_words_count = reduce(lambda x, y: int(x) + int(y), res_redis)
        elif len(res_redis) == 1:  # 防止只有一个词
            category.all_words_count = int(res_redis[0])
        else:  # 可能还没有词
            category.all_words_count = 0

        categorys_list.append(category)


    context = {
        'category' : categorys_list,
    }
    return render(request,'category.html',context)

def run_check(request):
    print("开始分析")
    article = ArticleForm(request.POST)
    if article.is_valid():
        message = article.cleaned_data['body']
        bayes = Naive_Bayes()
        res = bayes.naive_Bayes(message)
        return HttpResponse(res)
    else:
        return HttpResponse("错误")

def run_check_csdn(request):
    print("csdn.. 开始分析")
    article = ArticleForm(request.POST)
    if article.is_valid():
        message = article.cleaned_data['body']

        csdn = csdn_Bayes()
        ana_res = analysis_text(message)
        max = csdn.naive_Bayes(ana_res.pop('text_count'))
        print(max)
        res = {
            'status' : True,
            'res'  : ana_res,
            'max'  : max
        }
        res_json = json.dumps(res,ensure_ascii=False)
        return HttpResponse(res_json,content_type="application/json")
    else:
        return HttpResponse("")

def run_spider(request):
    if request.method == "GET":
        op = request.GET.get('op')
        cate = request.GET.get('cate')[5:]
        print("开始爬取",cate)
        if op == "run":
            url = 'https://blog.csdn.net/api/articles'
            category = cate
            spider = Spider_man(url, category)
            for i in range(100):
                time.sleep(1)
                spider.run_spider()
        else:
            print("AJAX 传输出错")
        return HttpResponse("成功")
    else:
        return HttpResponse("失败")

def run_create_category(request):
    category = CategoryForm(request.POST)
    if category.is_valid():
        message = category.cleaned_data['category']
        new_record = Category(category=message)
        new_record.save()
        return HttpResponse("成功")
    else:
        return HttpResponse("错误")

def run_get_category(request):
    categorys = Category.objects.filter(category__contains='csdn').order_by('category')  # 算出每个分类的数量
    category_dict = {}
    for category in categorys:  # 计算每个类别的样本个数
        count = Article.objects.filter(category=category).count()  #
        category_dict[category.category] = count

    res = {
        "category_list" : category_dict
    }

    res_json = json.dumps(res,ensure_ascii=False)
    return HttpResponse(res_json,content_type="application/json")
