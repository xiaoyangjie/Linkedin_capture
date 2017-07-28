#coding=utf-8
import random

import pymongo

# MONGOHOST = 'mongodb://mongo:123456@121.49.99.14'
# cli = pymongo.MongoClient(MONGOHOST)['Linkedin']['urlNew']
# cli.update_many({},{'$set':{'updateTime':1}})
# cli1 = pymongo.MongoClient(MONGOHOST)['Linkedin']['LinkedinAccount']
#
# print random.randint(0,3)

# for r in cli.find({}):
#     try:
#         rr = {}
#         rr['password'] = r['ld_pwd']
#         rr['email'] = r['email']
#         rr['lastUsedTime'] = 1
#         rr['userState'] = 'normal'
#         rr['isNeedCheckEmail'] = False
#         rr['lastUsedTimeStr'] = '1'
#         rr['usedState'] = 'noUsed'
#         try:
#             rr['emailPassword'] = r['email_pwd']
#         except:
#             rr['emailPassword'] = r['ld_pwd']
#
#         cli1.insert(rr)
#     except :
#         pass
# http://www.linkedin.com/in/sanjoykumarmalik/
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
#
# def login(self, email, password):
#     """
#     使用账户名和密码进行登录
#     :param email:
#     :param password:
#     :return:登录成功返回true
#     """
#     flag = True
#     try:
#         self.driver.get('https://www.linkedin.com/uas/login')
#         WebDriverWait(self.driver, 180).until(EC.presence_of_element_located((By.CLASS_NAME, "inner-wrapper")))
#         self.driver.find_element_by_id('session_key-login').send_keys(email)
#         self.driver.find_element_by_id('session_password-login').send_keys(password)
#         self.driver.find_element_by_css_selector('input#btn-primary.btn-primary').click()
#         try:
#             WebDriverWait(self.driver, 60).until(
#                 EC.presence_of_element_located((By.CLASS_NAME, "nav-item__china-logo")))
#             self.loginLogger.info('email:' + email + ' ' + 'password:' + str(password) + ' ' + 'login success!')
#         except Exception:
#             print 1
#             print Exception.message
#             if self.driver.current_url == 'https://www.linkedin.com/uas/consumer-email-challenge' or self.driver.find_element_by_id(
#                     'global-alert-queue'):
#                 self.__dataStorage.get(self.accountName).update({'email': email}, {'$set': {'userState': 'except'}})
#             self.loginLogger.error('email:' + email + ' ' + 'password:' + str(password) + ' ' + 'login fail!')
#             flag = False
#     except Exception:
#         print 2
#         print Exception.message
#         flag = False
#     return flag
#
from redis import ConnectionPool
import redis
a = redis.StrictRedis(host='121.49.99.14',port=6000,db=0,password='yj123456')
print a.scard('linkedinUrlName')