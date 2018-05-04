from .redisdb import Redis_Go
import os
from django.conf import settings
import jieba

class Training_info(object):
    '''
    存储一些训练集的基本信息，并且初始化对redis的连接
    '''
    def __init__(self,host="127.0.0.1",port="6379"):
        self.redis_con = self.init_redis(host,port)

    def init_redis(self,host,port):
        redis = Redis_Go(port=port, host=host)
        r = redis.redis_connection()
        return r

class LoadData(Training_info,Redis_Go):
    def __init__(self):
        #加载停用词
        super(LoadData,self).__init__()
        self.stop_words = self.get_stop_words()

    def get_stop_words(self):
        stopList = []
        stop_file = os.path.join(settings.STOPWORDS_DIR,'StopWords.txt')
        for line in open(stop_file, "r"):
            stopList.append(line[:len(line) - 1])
        return stopList

    def get_word_list(self,content):
        # 分词结果放入res_list
        wordsList = []
        res_list = list(jieba.cut(content))
        for i in res_list:
            if i not in self.stop_words and i.strip() != '' and i != None:
                wordsList.append(i)
        return wordsList

    #存入redis
    def dump_into_redis(self,content,type):
        wordsList = self.get_word_list(str(content).replace("\n",""))
        pipe = self.redis_con.pipeline(transaction=True)
        for word in wordsList:
            self.redis_hset(self.redis_con, type, word)
        pipe.execute()

    def load_run(self,content,type):
        self.dump_into_redis(content,type)