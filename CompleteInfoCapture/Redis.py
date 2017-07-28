import json
import time
import redis
from pymongo import MongoClient
from Configure import *

class Redis(object):
    def __init__(self,dataStorge):
        self.urlRedis = redis.StrictRedis(host=REDISURL.get('redisHost'),port=REDISURL.get('port'),password=REDISURL.get('password'))
        self.linkedinUrlName = REDISURL.get('key')
        self.dataStorage = dataStorge

    def getLinkedinUrls(self):
        for url in self.dataStorage.get(LINKEDINURL.get('name')).find({'isView': False}, {'_id': 0, 'person_website': 1,'readNum': 1}).limit(1000):
            self.urlRedis.sadd(self.linkedinUrlName, json.dumps(url))

    def urlSpop(self):
        try:
            if self.urlRedis.scard(self.linkedinUrlName) < 10:
                self.getLinkedinUrls()
            result = json.loads(self.urlRedis.spop(self.linkedinUrlName))
        except Exception as e :
            print e.message
            time.sleep(6 * 60 * 60)
        else:
            return result

    # def run(self):
    #     while True:
    #         if self.urlRedis.scard(self.linkedinUrlName) < 100:
    #             self.getLinkedinUrls()
    #         time.sleep(60)
# api = Redis('a')
# print api.urlSpop()['readNum']
