#coding=utf-8
'''
Created on 2018年3月26日

@author: weijiaxiang007
@mail: weijiaxiang007@foxmail.com
'''

from abc import abstractmethod,ABCMeta
import redis

class redis_Base(object):
    def __init__(self, port=6379, host="127.0.0.1",db=0):
        self.port = port
        self.host = host
        self.db = db

    def redis_connection(self):
        pool = redis.ConnectionPool(host=self.host,port=self.port,db=self.db)
        r = redis.Redis(connection_pool=pool)
        return r

    @abstractmethod
    def redis_hset(self,r,type,words,count):
        r.hset(type,words,count)

class Redis_Go(redis_Base):
    def redis_hset(self,r,type,words):
        res = r.hget(type, words)
        if res == None:
            r.hset(type,words,1)
        else:
            r.hincrby(type,words,1)
    def redis_hlen(self,r,type):
        res = r.hlen(type)
        if res == None:
            print("Redis Error ,HLEN")
        else:
            return res



