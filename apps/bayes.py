import math
from functools import reduce
from .redisdb import Redis_Go
import jieba

class Naive_Bayes():

    @property
    def init_redis(self,host="127.0.0.1",port="6379"):
        redis = Redis_Go(port=port, host=host)
        r = redis.redis_connection()
        return r

    def addToDict(self,wordsList):
        wordsDict = {}
        for item in wordsList:
            if item in wordsDict.keys():
                wordsDict[item] += 1
            else:
                wordsDict.setdefault(item, 1)
        return wordsDict

    def cut_test_file(self,test_file):
        # 分词结果放入res_list
        wordsList = []
        res_list = list(jieba.cut(test_file))
        for i in res_list:
            if  i.strip() != '' and i != None:
                wordsList.append(i)
        return wordsList

    def naive_Bayes(self,test_file):
        wordsList = self.cut_test_file(test_file)
        wordsDict = self.addToDict(wordsList)

        normal_count = int(self.init_redis.get("normal_count"))
        spam_count = int(self.init_redis.get("spam_count"))

        prior_normal = normal_count * 1.0 / (normal_count + spam_count)        #先验概率
        prior_spam =  spam_count * 1.0 / (normal_count + spam_count)

        likelihood_normal = 0.0
        likelihood_spam = 0.0

        redis = self.init_redis
        all_words = redis.hkeys("normal")
        normal_all_words = []
        for words in all_words:
            words = words.decode('utf-8')
            normal_all_words.append(words)

        all_words = redis.hkeys("spam")
        spam_all_words = []
        for words in all_words:
            words = words.decode('utf-8')
            spam_all_words.append(words)

        all_words_list = normal_all_words + spam_all_words
        diff = len(all_words_list)

        normal_all_words_count = reduce(lambda x,y:int(x)+int(y),redis.hvals("normal"))
        spam_all_words_count = reduce(lambda x,y:int(x)+int(y),redis.hvals("spam"))

        for w,cnt in list(wordsDict.items()):
            if w not in all_words_list:
                diff += 1

        normal_evidence = normal_all_words_count + diff
        spam_evidence   = spam_all_words_count + diff

        for w,cnt in list(wordsDict.items()):
            word_cnt = redis.hget("normal", w)  # 待测文件中出现的词 在 样本类别出现的次数。
            if word_cnt == None:
                word_cnt = 0
            else:
                word_cnt = int(word_cnt)
            child_like = (cnt * math.log((word_cnt + 1) * 1.0 / (normal_evidence)))
            likelihood_normal += child_like


            word_cnt = redis.hget("spam", w)  # 待测文件中出现的词 在 样本类别出现的次数。
            if word_cnt == None:
                word_cnt = 0
            else:
                word_cnt = int(word_cnt)
            child_like = (cnt * math.log((word_cnt + 1) * 1.0 / (spam_evidence)))
            likelihood_spam += child_like

        p_norm = likelihood_normal + math.log(prior_normal)
        p_spam = likelihood_spam + math.log(prior_spam)

        print('正常邮件的概率: ',p_norm)
        print('垃圾邮件的概率: ',p_spam)

        if p_norm >= p_spam:
            prob = "正常"
        else:
            prob = "垃圾"

        return prob