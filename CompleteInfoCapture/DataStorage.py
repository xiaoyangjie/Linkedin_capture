# coding=utf-8
import redis
from pymongo import MongoClient
from Configure import *

class DataStorage(object):

    def __init__(self):
        self.dataStorage = {}

        self.accountName = ACCOUNT.get('name')
        self.accountDB = ACCOUNT.get('db')
        self.accountCol = ACCOUNT.get('col')

        self.urlName = LINKEDINURL.get('name')
        self.urlDB = LINKEDINURL.get('db')
        self.urlCol = LINKEDINURL.get('col')

        self.usersName = LINKEDINUSERS.get('name')
        self.usersDB = LINKEDINUSERS.get('db')
        self.usersCol = LINKEDINUSERS.get('col')

        self.postName = LINKEDINPOSTSURL.get('name')
        self.postDB = LINKEDINPOSTSURL.get('db')
        self.postCol = LINKEDINPOSTSURL.get('col')

        self.__createUniqueIndex()
        self.__getCollection()

    def __createUniqueIndex(self):
        MongoClient(MONGOHOST).get_database(self.accountDB).get_collection(self.accountCol).ensure_index('email', unique=True)
        MongoClient(MONGOHOST).get_database(self.urlDB).get_collection(self.urlCol).ensure_index('person_website', unique=True)
        MongoClient(MONGOHOST).get_database(self.usersDB).get_collection(self.usersCol).ensure_index('person_website', unique=True)
        MongoClient(MONGOHOST).get_database(self.postDB).get_collection(self.postCol).ensure_index('postUrl',unique=True)

    #########################################
    #
    #  将每个数据库集合的游标都放在一个字典中，方便其后获取
    #
    ##########################################
    def __getCollection(self):
        if not (ACCOUNT or LINKEDINURL or LINKEDINUSERS) :
            print "please input correct configure:ACCOUNT and LINKEDINURL and LINKEDINUSERS"

        self.dataStorage[self.accountName] =  MongoClient(MONGOHOST).get_database(self.accountDB).get_collection(self.accountCol)
        self.dataStorage[self.urlName] = MongoClient(MONGOHOST).get_database(self.urlDB).get_collection(self.urlCol)
        self.dataStorage[self.usersName] = MongoClient(MONGOHOST).get_database(self.usersDB).get_collection(self.usersCol)
        self.dataStorage[self.postName] = MongoClient(MONGOHOST).get_database(self.postDB).get_collection(self.postCol)

    def find(self):
        pass