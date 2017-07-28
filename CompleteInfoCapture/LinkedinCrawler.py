# -*- coding: UTF-8 -*-
import random

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, NoSuchWindowException,TimeoutException
import time
from multiprocessing.dummy import Pool
from multiprocessing import Queue
from pymongo.errors import DuplicateKeyError
import logging
import logging.config
from Redis import Redis
from Configure import *
from DataStorage import DataStorage
from Parse import Parse
from WebAction import WebAction




class LinkedinCrawler:
    def __init__(self, dataStorage):
        """
        初始化
        :return:
        """
        self.driver = webdriver.Chrome()
        # self.driver.implicitly_wait(1)
        # self.driver = webdriver.PhantomJS() #########不能使用，个人成就和推荐信信息爬不出来

        self.accountName = ACCOUNT.get('name')
        self.urlName = LINKEDINURL.get('name')
        self.usersName = LINKEDINUSERS.get('name')
        self.postName = LINKEDINPOSTSURL.get('name')
        self.__dataStorage = dataStorage
        self.parse = Parse()
        self.webAction = WebAction()
        # self.linkedin_limit = 0
        self.__initLogger()

    def __initLogger(self):
        """
        初始化日志模块
        :return:
        """
        logging.config.fileConfig("logging.conf")
        self.loginLogger = logging.getLogger('login')

    def login(self, email, password):
        """
        使用账户名和密码进行登录
        :param email:
        :param password:
        :return:登录成功返回true
        """
        flag = True
        try:
            self.driver.get('https://www.linkedin.com/uas/login')
            WebDriverWait(self.driver, 180).until(EC.presence_of_element_located((By.CLASS_NAME, "inner-wrapper")))
            self.driver.find_element_by_id('session_key-login').send_keys(email)
            self.driver.find_element_by_id('session_password-login').send_keys(password)
            self.driver.find_element_by_css_selector('input#btn-primary.btn-primary').click()
            try :
                WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, "nav-item__china-logo")))
                self.loginLogger.info('email:' + email + ' ' + 'password:' + str(password) + ' ' + 'login success!')
            except TimeoutException:
                self.driver.refresh()
                if self.driver.current_url != 'http://www.linkedin.com/feed/?trk=':
                    if self.driver.current_url == 'https://www.linkedin.com/uas/consumer-email-challenge':
                        self.__dataStorage.get(self.accountName).update({'email':email}, {'$set':{'userState':'except'}})
                    elif self.driver.find_element_by_id('global-alert-queue'):
                        self.__dataStorage.get(self.accountName).update({'email': email}, {'$set': {'userState': 'limit'}})
                    self.loginLogger.error('email:' + email + ' ' + 'password:' + str(password) + ' ' + 'login fail!')
                    flag = False
                else:
                    self.loginLogger.info('email:' + email + ' ' + 'password:' + str(password) + ' ' + 'login success!')
        except TimeoutException:
            if self.driver.current_url != 'http://www.linkedin.com/feed/?trk=':
                flag = False

        return flag

    def processPage(self,LinkedinUrl):
        """
        处理页面
        :return:usr
        """
        self.parse.processPageLogger.info('Start:' + LinkedinUrl)
        time.sleep(3)
        try:
            self.driver.get(LinkedinUrl)
            WebDriverWait(self.driver,180).\
                until(EC.presence_of_all_elements_located((By.CLASS_NAME,'pv-top-card-section__header')))
        except TimeoutException:
            print self.driver
            self.driver.refresh()
            if self.driver.current_url == 'http://www.linkedin.com/in/unavailable/':
                self.__dataStorage.get(self.urlName).update({'person_website':LinkedinUrl},{'$set':{'alive':False,'isView':True}})
                self.parse.processPageLogger.error(LinkedinUrl + ':not exists!')
            else:
                self.parse.processPageLogger.error('Timeout!!!'+LinkedinUrl)
            return False
        ##############初始化parse#################
        self.parse.usr = {}
        self.parse.url = []
        self.parse.person_website = LinkedinUrl
        self.parse.userPosts = []
        #################点击##########################
        self.webAction.userWebAction(self.driver, self.parse)
        time.sleep(3)
        ################解析大部分内容#############
        print self.driver.page_source
        self.parse.pageParse(self.driver)
        ################存储用户信息#######################
        self.__dataStorage.get(self.usersName).update({"person_website": LinkedinUrl}, {'$set': self.parse.usr},upsert=True)
        if self.parse.usr.get('job_experience') or self.parse.usr.get('education_detail') or self.parse.usr.get('volunteer_experience') \
            or self.parse.usr.get('skills') or self.parse.usr.get('education_detail'): #只要有一个就行
            self.__dataStorage.get(self.urlName).update({"person_website": LinkedinUrl},{"$set":{"isView": True}})
            #################解析userPosts###############################
            if self.parse.userPosts != []:
                for post in self.parse.userPosts:
                    self.__dataStorage.get(self.postName).update({'postUrl': post['postUrl']}, {'$set': post},upsert=True)
            #################解析URLs#######################
            self.parse.captureUrls(self.driver)
            if self.parse.url != []:
                for url in self.parse.url:
                    try:
                        self.__dataStorage.get(self.urlName).insert(url)
                    except DuplicateKeyError as DUEerr:
                        self.parse.getUrlsLogger.error(DUEerr.message)


        return True

    def postCapture(self, postUrl):
        """

        :param postUrl:
        :return:
        """
        self.parse.processPageLogger.info('Start:' + postUrl)
        time.sleep(3)
        try:
            self.driver.get(postUrl)
            WebDriverWait(self.driver,180).\
                until(EC.presence_of_all_elements_located((By.CLASS_NAME,'pv-treasury-media-viewer__detail-info')))
        except Exception:
            if self.driver.current_url == 'http://www.linkedin.com/in/unavailable/':
                self.__dataStorage.get(self.postName).update({'postUrl':postUrl},{'$set':{'alive':False,'isView':True}})
                self.parse.processPageLogger.error(postUrl + ':not exists!')
            else:
                print 3
                self.parse.processPageLogger.error('Timeout!!!'+postUrl)
            return False

        usr = {}
        usr = self.parse.parsePosts(self.driver)
        self.__dataStorage.get(self.postName).update({'postUrl': postUrl}, {'$set': {'isView':True}})
        if usr != {}:
            self.__dataStorage.get(self.usersName).update({"person_website": LinkedinUrl}, {'$set': usr})

    def followingSchoolsCapture(self, LinkedinUrl):
        followingSchoolsUrl = LinkedinUrl + 'interests/schools/'
        self.parse.processPageLogger.info('Start:' + followingSchoolsUrl)
        time.sleep(3)
        ####################防范策略还没有完善##################
        try:
            self.driver.get(followingSchoolsUrl)
            WebDriverWait(self.driver, 180). \
                until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'modal-title')))
        except Exception:
            if self.driver.current_url == 'http://www.linkedin.com/in/unavailable/':
                self.__dataStorage.get(self.urlName).update({'person_website': LinkedinUrl},
                                                            {'$set': {'alive': False, 'isView': True}})
                self.parse.processPageLogger.error(LinkedinUrl + ':not exists!')
            else:
                self.parse.processPageLogger.error('Timeout!!!' + followingSchoolsUrl)
            return False

        #######初始化############
        self.parse.person_website = LinkedinUrl
        self.parse.followingSchools = {}
        #######点击###########
        self.webAction.followingAction(driver=self.driver)
        ########解析#########
        self.parse.parseFollowingSchools(self.driver)
        #####更新用户##############
        if self.parse.followingSchools != {}:
            ##############更新用户信息#############################
            self.__dataStorage.get(self.usersName).update({'person_website': self.parse.person_website},
                                                          {'$set': self.parse.followingSchools}, upsert=True)
        ###############更新url######################
        self.__dataStorage.get(self.urlName).update({'person_website': self.parse.person_website},
                                                    {'$set': {'isInterestSchool': True}})

    def followingCompaniesCapture(self, LinkedinUrl):
        followingCompaniesUrl = LinkedinUrl + 'interests/companies/'
        self.parse.processPageLogger.info('Start:' + followingCompaniesUrl)
        time.sleep(3)
        ####################防范策略还没有完善##################
        try:
            self.driver.get(followingCompaniesUrl)
            WebDriverWait(self.driver, 180). \
                until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'modal-title')))
        except Exception:
            if self.driver.current_url == 'http://www.linkedin.com/in/unavailable/':
                self.__dataStorage.get(self.urlName).update({'person_website': LinkedinUrl},
                                                            {'$set': {'alive': False, 'isView': True}})
                self.parse.processPageLogger.error(LinkedinUrl + ':not exists!')
            else:
                print 3
                self.parse.processPageLogger.error('Timeout!!!' + followingCompaniesUrl)
            return False

        #######初始化############
        self.parse.person_website = LinkedinUrl
        self.parse.followingCompanies = {}
        #######点击###########
        self.webAction.followingAction(driver=self.driver)
        ########解析#########
        self.parse.parseFollowingCompanies(self.driver)
        #####更新用户##############
        if self.parse.followingCompanies != {}:
            ##############更新用户信息#############################
            self.__dataStorage.get(self.usersName).update({'person_website': self.parse.person_website},
                                                          {'$set': self.parse.followingCompanies}, upsert=True)
        ###############更新url######################
        self.__dataStorage.get(self.urlName).update({'person_website': self.parse.person_website},
                                                    {'$set': {'isInterestCompanies': True}})

    def followingInfluencersCapture(self,LinkedinUrl):
        followingInfluencersUrl = LinkedinUrl + 'interests/influencers/'
        self.parse.processPageLogger.info('Start:' + followingInfluencersUrl)
        time.sleep(3)
        ####################防范策略还没有完善##################
        try:
            self.driver.get(followingInfluencersUrl)
            WebDriverWait(self.driver, 180). \
                until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'modal-title')))
        except Exception:
            if self.driver.current_url == 'http://www.linkedin.com/in/unavailable/':
                self.__dataStorage.get(self.urlName).update({'person_website': LinkedinUrl},
                                                            {'$set': {'alive': False, 'isView': True}})
                self.parse.processPageLogger.error(LinkedinUrl + ':not exists!')
            else:
                print 3
                self.parse.processPageLogger.error('Timeout!!!' + followingInfluencersUrl)
            return False

        #######初始化############
        self.parse.person_website = LinkedinUrl
        self.parse.followingInfluencers = {}
        #######点击###########
        self.webAction.followingAction(driver=self.driver)
        ########解析#########
        self.parse.parseFollowingInfluencers(self.driver)
        #####更新用户##############
        if self.parse.followingInfluencers != {}:
            ##############更新用户信息#############################
            self.__dataStorage.get(self.usersName).update({'person_website': self.parse.person_website},
                                                          {'$set': self.parse.followingInfluencers}, upsert=True)
        ###############更新url######################
        self.__dataStorage.get(self.urlName).update({'person_website': self.parse.person_website},
                                                    {'$set': {'isInfluencers': True}})

    def recentActivityPostsCapture(self, LinkedinUrl):
        """

        :param LinkedinUrl:
        :return:
        """
        recentActivityPostsUrl = LinkedinUrl + 'recent-activity/posts/'
        self.parse.processPageLogger.info('Start:' + recentActivityPostsUrl)
        time.sleep(3)
        ####################防范策略还没有完善##################
        try:
            self.driver.get(recentActivityPostsUrl)
            WebDriverWait(self.driver, 180). \
                until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'pv-recent-activity-detail__header-container')))
        except Exception:
            if self.driver.current_url == 'http://www.linkedin.com/in/unavailable/':
                self.__dataStorage.get(self.urlName).update({'person_website': LinkedinUrl}, {'$set': {'alive': False,'isView':True}})
                self.parse.processPageLogger.error(LinkedinUrl + ':not exists!')
            else:
                print 3
                self.parse.processPageLogger.error('Timeout!!!' + recentActivityPostsUrl)
            return False


        #######初始化############
        self.parse.person_website = LinkedinUrl
        self.parse.recentActivityPosts = {}
        #######点击###########
        self.webAction.recentActivityPostsAction(driver=self.driver)
        ########解析#########
        self.parse.parseRecentActivityPosts(self.driver)
        #####更新用户##############
        if self.parse.recentActivityPosts != {}:
            ##############更新用户信息#############################
            self.__dataStorage.get(self.usersName).update({'person_website': self.parse.person_website}, {'$set': self.parse.recentActivityPosts},upsert=True)
        ###############更新url######################
        self.__dataStorage.get(self.urlName).update({'person_website': self.parse.person_website}, {'$set': {'isRecentActivityPosts':True}})

    def logout(self):
        self.driver.get('http://www.linkedin.com/m/logout/')
        time.sleep(9)
        if self.driver.current_url == 'https://www.linkedin.com/hp/':
            self.loginLogger.info('logout success!')

    def closeWeb(self):
        self.driver.quit()



class MultiProcessCrawler(object):
    """
    多线程调用爬虫
    """
    def __init__(self):
        """
        初始化
        :return:
        """
        self.processNum = PRECESSNUM
        self.accountQueue = Queue()
        self.urlQueue = Queue()
        self.dataStorage = DataStorage()
        self.__dataStorage = self.dataStorage.dataStorage
        self.accountName = ACCOUNT.get('name')
        self.urlName = LINKEDINURL.get('name')
        self.usersName = LINKEDINUSERS.get('name')
        self.redis = Redis(self.__dataStorage)


    def __getAccountMany(self):
        """
        从数据库获得账户名和密码(大量)
        :return:null
        """
        # lastUpdateTime = int(time.time() - 24*60*60)
        # result = self.__name_pwd_collection.find({'user_state':'good','last_used_time':{'$lt':last_update_time}},{'_id':0,'email':1,'ld_pwd':1,'day_num':1})

        flag = True
        accountResult = self.__dataStorage.get(self.accountName).find({'userState' : 'normal'},{'_id':0,'email':1,'password':1})
        if accountResult.count() == 0:
            flag = False
        for account in accountResult:
            self.accountQueue.put(account)
        return flag

    def __getAccountRandomOne(self):

        ################这里其实有一个问题，如果程序突然关闭（人为或者意外），会造成一些麻烦，这个账号一直是using，但是没有人使用。。#####
        account = self.__dataStorage.get(self.accountName).find({'userState': 'normal'}, {'_id': 0, 'email': 1, 'password': 1}).sort('lastUsedTime',1).limit(1)
        account = account[0]
        self.__dataStorage.get(self.accountName).update({'email': account['email']},{'$set' : {'lastUsedTime':int(time.time())}})

        # if account:
        #     ###标记正在使用#########
        #     self.__dataStorage.get(self.accountName).update({'email' : account['email']},{'$set' : {'usedState' : 'using'}})
        ###########如果account没有，则是None
        return account


    #######################直接从mongodb读取，不利于分布式############
    def __getUrl(self):
        """
        读取没有读取过的url
        :return:
        """
        for url in self.__dataStorage.get(self.urlName).find({'isView':False},{'_id':0,'person_website':1,'readNum':1}).limit(URLLIMIT):
            self.urlQueue.put(url)

    #######################从redis读取，用于分布式############
    def __redisGetUrl(self):
        """
        读取没有读取过的url
        :return:
        """
        return self.redis.urlSpop()

    ##############################################
    #
    #  认定一个账号可以无限制的采集用户信息
    #
    ################################################
    def RunCrawler(self):
        while True :
            ######################现在弃用#######################
            # try:
            #     if self.accountQueue.qsize()==0:
            #         if not self.__getAccountMany() :##########如果没有账号，等待3个小时，再次循环###############
            #             print "sleep"
            #             time.sleep(3 * 60 * 60) #休息3个小时
            #             continue
            # except:
            #     print "maybe mongodb or network have a problem"
            #     time.sleep(10 * 60)
            #########################################################
            pool = Pool(self.processNum)
            [pool.apply_async(self.__RunCrawler) for i in range(self.processNum)]
            pool.close()
            pool.join()

            ################test########################
            # self.__RunCrawler()


    def __RunCrawler(self):
        while True:
            ################这个是一次获取很多个账号########################
            # self.__getAccountMany()
            # if self.accountQueue.qsize() == 0:
            #     break
            # account = self.accountQueue.get(timeout=3)
            ##########################################
            time.sleep(random.randint(1,3))
            account = self.__getAccountRandomOne()
            if not account:
                print "no have account"
                time.sleep(10 * 60)
                continue

            try:
                crawler = LinkedinCrawler(self.__dataStorage)

                ###############登陆账号######################
                if not crawler.login(account['email'],account['password']):
                    crawler.closeWeb()
                    continue

                limitNum = 60
                while limitNum:
                    limitNum = limitNum - 1
                    ##############单进程#####################
                    # if self.urlQueue.qsize() < 3:  # 假定的需要爬取的用户（url）一定是足够的，没有写保护措施（即url没有的情况）
                    #     self.__getUrl()
                    # LinkedinUrl = self.urlQueue.get()
                    ############多进程############################
                    LinkedinUrl = self.__redisGetUrl()
                    ###########################################
                    _LinkedinUrl = LinkedinUrl['person_website']
                    readNum = LinkedinUrl['readNum']
                    ###############采集用户信息####################
                    if crawler.processPage(_LinkedinUrl):
                        readNum += 1
                        ###########这个网页读取次数加1####################
                        self.__dataStorage.get(self.urlName).update({'person_website': _LinkedinUrl},{'$set': {'readNum': readNum}})
                        if readNum >= 2:
                            self.__dataStorage.get(self.urlName).update({'person_website':_LinkedinUrl},{'$set':{'isView':True}})
                crawler.logout()

            except Exception as e:
                print "renderERROR"
            finally:
                time.sleep(30)
                crawler.closeWeb()


if __name__ == '__main__':
    #
    # Crawler = MultiProcessCrawler()
    # Crawler.RunCrawler()

    url = 'http://www.linkedin.com/in/leannekemp/'
    test = LinkedinCrawler({})
    test.login('1019177406@qq.com','yj15923365092')
    test.processPage(url)