import math
from functools import reduce
from .bayes import Naive_Bayes
from .models import Category
from django.conf import settings
import os

class csdn_Bayes(Naive_Bayes):

    def naive_Bayes(self,text_dict):
        categorys_list = []    #获取最终处理好的样本类别
        filter_text = self.filter_stop(text_dict)
        redis = self.init_redis  #初始化好redis的连接

        text_all_words = 0.0
        words_list = []

        for category in Category.objects.filter(category__contains="csdn"):       #为类别加上一些方便贝叶斯计算的属性

            category.all_words = []           #该类别所含的所有词
            cate_all_words = redis.hkeys(category.category)
            for words in cate_all_words:
                words = words.decode('utf-8')
                category.all_words.append(words)
            words_list += category.all_words

            category.prior = 0.0
            category.likelihood = 0.0                         #似然函数 分子
            category.log_prob = 0.0                           #log概率
            category.evidence = 0.0                           #证据因子 分母

            res_redis = redis.hvals(category.category)        #算出每个类别的总词数
            if len(res_redis) > 2:
                category.all_words_count = reduce(lambda x, y: int(x) + int(y), res_redis)
            elif len(res_redis) == 1:                         #防止只有一个词
                category.all_words_count = int(res_redis[0])
            else:                                             #可能还没有词
                category.all_words_count = 0

            text_all_words += category.all_words_count        #计算总词数
            categorys_list.append(category)


        for cate in categorys_list:
            diff_words = len(set(words_list))
            cate.evidence = diff_words + cate.all_words_count

        for cate in categorys_list:
            cate.prior = (cate.all_words_count * 1.0) / text_all_words  #计算先验概率
            for w,cnt in list(filter_text.items()):      #计算每个类别的证据因子
                if w not in cate.all_words:
                    cate.evidence += 1

        for cate in categorys_list:
            for w, cnt in list(filter_text.items()):
                word_cnt = redis.hget(cate.category, w)   #待测文件中出现的词 在 样本类别出现的次数。
                if word_cnt == None:
                    word_cnt = 0
                else:
                    word_cnt = int(word_cnt)
                try:
                    child_likelihood = (cnt * (math.log((word_cnt + 1) * 1.0 / cate.evidence)))
                    cate.likelihood += child_likelihood
                except ZeroDivisionError:
                    print("证据因子为0，错误")

            cate.log_prob = cate.likelihood + math.log(cate.prior)

        # for cate in categorys_list:
        #     print('---category',cate.category,'---prior',cate.prior,
        #           '---evi',cate.evidence,'---','---log_prob',cate.log_prob)

        #### 开始汇总
        max = {
            "cate" : "",
            "prob" : -10000000.0
        }

        for cate in categorys_list:

            if cate.log_prob > max["prob"]:
                max["prob"] = cate.log_prob
                max["cate"] = cate.category

        return max


    def get_stop_words(self):
        stopList = []
        stop_file = os.path.join(settings.STOPWORDS_DIR,'StopWords.txt')
        for line in open(stop_file, "r"):
            stopList.append(line[:len(line) - 1])
        return stopList

    def filter_stop(self,text_dict):
        new_text ={}
        stop = self.get_stop_words()
        for word in text_dict:
            if word in stop:
                new_text[word] = text_dict[word]
        return text_dict

