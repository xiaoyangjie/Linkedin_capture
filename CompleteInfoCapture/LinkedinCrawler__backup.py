# -*- coding: UTF-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import time
import exceptions
import re
from multiprocessing.dummy import Pool
from multiprocessing import Queue
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from pymongo import errors
import logging
import logging.config
import codecs
import random
import urllib2

from Configure import *
from DataStorage import DataStorage
from Parse import Parse


class LinkedinCrawler:
    def __init__(self, dataStorage):
        """
        初始化
        :return:
        """
        self.driver = webdriver.Chrome()
        # self.driver = webdriver.PhantomJS()
        # self.driver.maximize_window()
        # 设置页面超时时间
        self.driver.set_page_load_timeout(30)

        self.accountName = ACCOUNT.get('name')
        self.urlName = LINKEDINURL.get('name')
        self.usersName = LINKEDINUSERS.get('name')
        self.__dataStorage = dataStorage
        self.parse = Parse()
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
            except Exception:
                print 1
                print Exception.message
                # self.__dataStorage.get(self.accountName).update({'email':email}, {'$set':{'userState':'except'}})
                self.loginLogger.error('email:' + email + ' ' + 'password:' + str(password) + ' ' + 'login fail!')
                flag = False
        except Exception:
            print 2
            print Exception.message
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
        except Exception:
            if self.driver.current_url == 'http://www.linkedin.com/in/unavailable/':
                self.__dataStorage.get(self.urlName).update({'person_website':LinkedinUrl},{'$set':{'alive':False}})
                self.parse.processPageLogger.error(LinkedinUrl + ':not exists!')
            else:
                print 3
                self.parse.processPageLogger.error('Timeout!!!'+LinkedinUrl)
            return False
        ##############初始化parse中的usr和url#################
        self.parse.usr = {}
        self.parse.url = {}
        #################点击##########################
        self.webAction()
        ################解析大部分内容#############
        self.parse.pageParse(self.driver, LinkedinUrl)
        ################存储用户信息#######################
        self.__dataStorage.get(self.usersName).update({"person_website": LinkedinUrl}, {'$set': self.parse.usr}, upsert=True)
        self.__dataStorage.get(self.urlName).update({"person_website": LinkedinUrl},{"$set":{"isView": True}})
        #################解析URLs#######################
        self.parse.captureUrls(self.driver)
        try:
            self.__dataStorage.get(self.urlName).update({'person_website': LinkedinUrl}, {'$set': self.parse.url},upsert=True)
        except DuplicateKeyError as DUEerr:
            self.parse.getUrlsLogger.error(DUEerr.message)

        # try:
        #     self.driver.find_element_by_class_name('wf-notif')  #linkedin受限
        #     self.linkedin_limit = 1
        # except :
        #     pass
        # # 爬取姓名
        # try:
        #     print self.driver.find_element_by_class_name("pv-top-card-section__name").text
        #     self.usr['name'] = self.driver.find_element_by_class_name("pv-top-card-section__name").text
        # except NoSuchElementException:
        #     self.processPageLogger.debug('name' + '\t' + 'no such element')
        #
        # # 个人主页链接
        # self.usr['person_website'] = LinkedinUrl
        #
        # # 爬取头像url
        # try:
        #     avater = self.driver.find_element_by_class_name("pv-top-card-section__photo")
        #     self.usr['profile_images_url'] = avater.find_element_by_tag_name("img").get_attribute("src")
        # except NoSuchElementException:
        #     self.processPageLogger.debug('profile_images_url' + '\t' + 'no such element')
        #
        # # 爬取职位
        # try:
        #     self.usr['title'] = self.driver.find_element_by_class_name("pv-top-card-section__headline").text
        # except NoSuchElementException:
        #     self.processPageLogger.debug('title' + '\t' + 'no such element')
        #
        # # 爬取公司地址
        # try:
        #     self.usr['company_location'] = self.driver.find_element_by_name("pv-top-card-section__location").text
        # except NoSuchElementException:
        #     self.processPageLogger.debug('company_location' + '\t' +'no such element')
        #
        # # 爬取现在的公司
        # try:
        #     self.usr['current_company'] = self.driver.find_element_by_class_name('pv-top-card-section__company').text
        # except NoSuchElementException:
        #     self.processPageLogger.debug('current_company' + '\t' + 'no such element')
        #
        # # 爬取简单教育情况
        # try:
        #     self.usr['education_overview'] = self.driver.find_element_by_class_name('pv-top-card-section__school').text
        # except NoSuchElementException:
        #     self.processPageLogger.debug('education_overview' + '\t' + 'no such element')
        #
        # # 爬取post内容
        # try:
        #     temp_list = []
        #     for item in self.driver.find_elements_by_class_name("artdeco-carousel-slide-container"):
        #         temp_list.append(item.find_element_by_tag_name('a').get_attribute('href'))
        #     print temp_list   #只有链接，以后在采集
        #         # temp = {}
        #         # try:temp['post_url'] = item.find_element_by_tag_name("a").get_attribute("href")
        #         # except:pass
        #         # try:temp['photo_url'] = item.find_element_by_tag_name("img").get_attribute("src")
        #         # except:pass
        #         # try:temp['brief_introduction'] = item.find_element_by_class_name("influencer-post-title").text
        #         # except:pass
        #         # try:temp['post_date'] = item.find_element_by_class_name("influencer-post-published").text
        #         # except:pass
        #         # temp_list.append(temp)
        #     if temp_list:
        #         self.usr['posts'] = temp_list
        # except NoSuchElementException:
        #     self.processPageLogger.debug('posts' + '\t' + 'no such element')
        #
        # # 爬取背景总概
        # try:
        #     self.usr['background_summary'] = self.driver.find_element_by_class_name("pv-top-card-section__summary").text
        # except NoSuchElementException:
        #     self.processPageLogger.debug('background_summary' + '\t' +'no such element')
        #
        # # 爬取从业经历
        # try:
        #     exp_overview = self.driver.find_elements_by_class_name('pv-position-entity')
        #     temp_list = []
        #     for item in exp_overview:
        #         temp = {}
        #         try:temp['company'] = item.find_element_by_class_name("pv-position-entity__secondary-title").text
        #         except:pass
        #         try:temp['title'] = item.find_element_by_tag_name("h3").text
        #         except:pass
        #         try:temp['time'] = item.find_element_by_class_name("pv-entity__date-range").text
        #         except:pass
        #         try:temp['duration'] = item.find_element_by_class_name("pv-entity__duration").text
        #         except:pass
        #         try:temp['description'] = item.find_element_by_class_name("pv-entity__description").text
        #         except:pass
        #         temp_list.append(temp)
        #     if temp_list:
        #         self.usr['job_experience'] = temp_list
        # except NoSuchElementException:
        #     self.processPageLogger.debug('job_experience' + '\t' + 'no such element')
        #
        # #爬取详细教育情况
        # try:
        #     temp_list = []
        #     education = self.driver.find_elements_by_class_name("pv-education-entity")
        #     for item in education:
        #         temp = {}
        #         try:temp['school name'] = item.find_element_by_class_name("pv-entity__school-name").text
        #         except:pass
        #         try:temp['major and degree'] = item.find_element_by_class_name("pv-entity__comma-item").text
        #         except:pass
        #         try:temp['date'] = item.find_element_by_class_name("pv-education-entity__date").text
        #         except:pass
        #         try:temp['description'] = item.find_element_by_class_name("pv-entity__description").text
        #         except:pass
        #         temp_list.append(temp)
        #     if temp_list:
        #         self.usr['education_detail'] = temp_list
        # except NoSuchElementException:
        #         self.processPageLogger.debug('education' + '\t' + 'no such element')
        #
        # #志愿者经历
        # try:
        #     exp_overview = self.driver.find_elements_by_class_name('pv-volunteering-entity')
        #     temp_list = []
        #     for item in exp_overview:
        #         temp = {}
        #         try:temp['company'] = item.find_element_by_class_name("pv-volunteer-entity__secondary-title").text
        #         except:pass
        #         try:temp['title'] = item.find_element_by_tag_name("h3").text
        #         except:pass
        #         try:temp['time'] = item.find_element_by_class_name("pv-entity__date-range").text
        #         except:pass
        #         try:temp['duration'] = item.find_element_by_class_name("pv-entity__duration").text
        #         except:pass
        #         try:temp['description'] = item.find_element_by_class_name("pv-entity__description").text
        #         except:pass
        #         temp_list.append(temp)
        #     if temp_list:
        #         self.usr['volunteer_experience'] = temp_list
        # except NoSuchElementException:
        #     self.processPageLogger.debug('volunteer_experience' + '\t' + 'no such element')
        #
        # # 爬取技能
        # try:
        #     temp_list = []
        #     for item in self.driver.find_elements_by_class_name('pv-skill-entity--featured'):
        #         temp = {}
        #         try:temp['skill_name'] = item.find_element_by_class_name('pv-skill-entity__skill-name').text
        #         except:pass
        #         try:temp['skill_points'] = item.find_element_by_class_name('pv-skill-entity__endorsement-count').text
        #         except:pass
        #         temp_list.append(temp)
        #     if temp_list:
        #         self.usr['skills'] = temp_list
        # except NoSuchElementException:
        #     self.processPageLogger.debug('skills' + '\t' + 'no such element')
        #
        # # 爬取推荐信息
        # try:
        #     temp_list = []
        #     for item in self.driver.find_elements_by_class_name("pv-recommendation-entity"):
        #         temp = {}
        #         try:temp['recommenderPersonWebsite'] = item.find_element_by_tag_name("a").get_attribute('href')
        #         except:pass
        #         try:temp['recommenderName'] = item.find_element_by_tag_name("h3").text
        #         except:pass
        #         try:temp['recommenderPosition'] = item.find_element_by_class_name("pv-recommendation-entity__headline").text
        #         except:pass
        #         try:temp['date'] = item.find_element_by_class_name("rec-extra").text
        #         except:pass
        #         try:temp['content'] = item.find_element_by_class_name("pv-recommendation-entity__text").text
        #         except:pass
        #         temp_list.append(temp)
        #     if temp_list:
        #         self.usr['Recommendations'] = temp_list
        # except NoSuchElementException:
        #     self.processPageLogger.debug('Recommendations' + '\t' + 'no such element')


        # # following news
        # try:
        #     temp_list = []
        #     for item in self.driver.find_element_by_id("follow-channel-list").find_elements_by_tag_name("li"):
        #         temp = {}
        #         try:
        #             temp['name'] = item.find_element_by_class_name("channel-name").text
        #             temp['stats'] = item.find_element_by_class_name("following-stats").text
        #             temp_list.append(temp)
        #         except:
        #             pass
        #     if temp_list:
        #         usr['following_news'] = temp_list
        #
        # except NoSuchElementException:
        #     self.processPageLogger.debug('following_news' + '\t' + 'no such element')
        # # following companies
        # try:
        #     temp_list = []
        #     for item in self.driver.find_element_by_xpath("//div[@class='following-companies expanded-view']").find_elements_by_tag_name("li"):
        #         temp = {}
        #         try:
        #             temp['name'] = item.find_element_by_class_name("following-name").text
        #             temp['fields'] = item.find_element_by_class_name("following-field").text
        #             temp_list.append(temp)
        #         except:
        #             pass
        #     if temp_list:
        #         usr['following_companies'] = temp_list
        # except NoSuchElementException:
        #     self.processPageLogger.debug('following_companies_expanded-view' + '\t' + 'no such element')
        #
        # try:
        #     temp_list = []
        #     for item in self.driver.find_element_by_xpath("//div[@class='following-companies collapsed-view']").find_elements_by_tag_name("li"):
        #         temp = {}
        #         try:
        #             temp['name'] = item.find_element_by_class_name("following-name").text
        #             temp['fields'] = item.find_element_by_class_name("following-field").text
        #             temp_list.append(temp)
        #         except:
        #             pass
        #     if temp_list:
        #         usr['following_companies'] = temp_list
        # except NoSuchElementException:
        #     self.processPageLogger.debug('following_companies_collapsed-view' + '\t' + 'no such element')
        # # following schools
        # try:
        #     temp_list = []
        #     self.driver.find_element_by_class_name("following-schools")
        #     for item in self.driver.find_element_by_class_name("following-schools").find_elements_by_tag_name("li"):
        #         temp = {}
        #         try:
        #             temp['name'] = item.find_element_by_class_name("following-name").text
        #             temp['fields'] = item.find_element_by_class_name("following-field").text
        #             temp_list.append(temp)
        #         except:
        #             pass
        #     if temp_list:
        #         usr['following_schools'] = temp_list
        # except NoSuchElementException:
        #     self.processPageLogger.debug('following_schools' + '\t' + 'no such element')
        # # other following companies
        # try:
        #     temp_list = []
        #     self.driver.find_element_by_class_name("following-industries-companies")
        #     for item in self.driver.find_element_by_class_name("following-industries-companies").find_elements_by_tag_name("li"):
        #         temp = {}
        #         try:
        #             temp['name'] = item.find_element_by_class_name("following-name").text
        #             temp['fields'] = item.find_element_by_class_name("following-field").text
        #             temp_list.append(temp)
        #         except:
        #             pass
        #     if temp_list:
        #         usr['other_companies'] = temp_list
        # except NoSuchElementException:
        #     self.processPageLogger.debug('other_companies' + '\t' + 'no such element')

        #个人成就

        # 爬取出版物
        # try:
        #     temp_list = []
        #     for item in self.driver.find_element_by_xpath("//button[@data-control-name='accomplishments_expand_publications']").\
        #             find_element_by_xpath("../div[@class='pv-accomplishments-block__list-container']").find_elements_by_tag_name('li'):
        #         temp = {}
        #         try:temp['publications_title'] = item.find_element_by_tag_name("h4").text
        #         except:pass
        #         try:temp['publisher'] = item.find_element_by_class_name("pv-accomplishment-entity__publisher").text
        #         except:pass
        #         try:temp['publications_journal'] = item.find_element_by_class_name("pv-accomplishment-entity__description").text
        #         except:pass
        #         try:temp['publications_date'] = item.find_element_by_class_name("pv-accomplishment-entity__date").text
        #         except:pass
        #         temp_list.append(temp)
        #     if temp_list:
        #         usr['publications'] = temp_list
        # except NoSuchElementException:
        #         self.processPageLogger.debug('publications' + '\t'+ 'no such element')
        # # 语言
        # try:
        #     temp_list = []
        #     for item in self.driver.find_element_by_xpath(
        #             "//button[@data-control-name='accomplishments_collapse_languages']"). \
        #             find_element_by_xpath(
        #         "../div[@class='pv-accomplishments-block__list-container']").find_elements_by_tag_name('li'):
        #         temp = {}
        #         temp['languages'] = item.find_element_by_tag_name("h4").text
        #         try:temp['languages-proficiency'] = item.find_element_by_class_name("pv-accomplishment-entity__proficiency").text
        #         except:pass
        #         temp_list.append(temp)
        #     if temp_list:
        #         usr['languages'] = temp_list
        # except NoSuchElementException:
        #         self.processPageLogger.debug('languages' + '\t' + 'no such element')
        # # 认证
        # try:
        #     temp_list = []
        #     for item in self.driver.find_element_by_xpath(
        #             "//button[@data-control-name='pv-accomplishment-entity__proficiency']"). \
        #             find_element_by_xpath(
        #         "../div[@class='pv-accomplishments-block__list-container']").find_elements_by_tag_name('li'):
        #         temp = {}
        #         try:temp['certification_item'] = item.find_element_by_tag_name("h4").text
        #         except :pass
        #         try:temp['certification_organization'] = item.find_elements_by_tag_name("a")[0].find_element_by_tag_name('p').text
        #         except:pass
        #         try:temp['certification_date'] = item.find_element_by_class_name("pv-accomplishment-entity__date").text
        #         except:pass
        #         temp_list.append(temp)
        #     if temp_list:
        #         usr['certification'] = temp_list
        # except NoSuchElementException:
        #         self.processPageLogger.debug('certification' + '\t' + 'no such element')
        # # 荣誉奖项   (如果太多，会不会定位不到？？)
        # try:
        #     temp_list = []
        #     for item in self.driver.find_element_by_xpath(
        #             "//button[@data-control-name='accomplishments_expand_honors']"). \
        #             find_element_by_xpath(
        #         "../div[@class='pv-accomplishments-block__list-container']").find_elements_by_tag_name('li'):
        #         temp = {}
        #         try:temp['honor_name'] = item.find_element_by_tag_name("h4").text
        #         except NoSuchElementException:
        #             pass
        #         try:temp['honor_organization'] = item.find_element_by_class_name("pv-accomplishment-entity__issuer").text
        #         except:pass
        #         try:temp['honor_time'] = item.find_element_by_class_name("pv-accomplishment-entity__date").text
        #         except:pass
        #         try:temp['honor_content'] = item.find_element_by_class_name("pv-accomplishment-entity__description").text
        #         except:pass
        #         temp_list.append(temp)
        #     if temp_list:
        #         usr['honor'] = temp_list
        # except NoSuchElementException:
        #     self.processPageLogger.debug('honor' + '\t' + 'no such element')
        # # 参与组织
        # try:
        #     temp_list = []
        #     for item in self.driver.find_element_by_xpath(
        #             "//button[@data-control-name='accomplishments_expand_organizations']"). \
        #             find_element_by_xpath(
        #         "../div[@class='pv-accomplishments-block__list-container']").find_elements_by_tag_name('li'):
        #         temp = {}
        #         try:
        #             temp['name'] = item.find_element_by_tag_name("h4").text
        #         except NoSuchElementException:
        #             pass
        #         try:
        #             temp['position'] = item.find_element_by_class_name(
        #                 "pv-accomplishment-entity__position").text
        #         except:
        #             pass
        #         try:
        #             temp['time'] = item.find_element_by_class_name("pv-accomplishment-entity__date").text
        #         except:
        #             pass
        #         try:temp['descripation'] = item.find_element_by_class_name(
        #                 "pv-accomplishment-entity__description").text
        #         except:pass
        #         temp_list.append(temp)
        #     if temp_list:
        #         usr['organization'] = temp_list
        # except NoSuchElementException:
        #     self.processPageLogger.debug('organization' + '\t' + 'no such element')

        # twitter账号
        # try:
        #     temp_list = []
        #     for item in self.driver.find_element_by_class_name("ci-twitter").find_elements_by_tag_name("li"):
        #         temp = {}
        #         temp['screen_name'] = item.find_element_by_tag_name('a').text
        #         temp['url'] = item.find_element_by_tag_name('a').get_attribute('href')
        #         temp_list.append(temp)
        #     if temp_list:
        #         self.usr['twitter'] = temp_list
        # except NoSuchElementException:
        #     self.processPageLogger.debug('twitter' + '\t' + 'no such element')
        # print self.usr

        # self.__usr_collection.update({"account_id": usr['account_id']}, {'$set': usr}, upsert=True)
        # self.url_collection.update({"url": LinkedinUrl},{"$set":{"unview": False, "state": "idle"}})
        # try:
        #     self.driver.find_element_by_class_name('wf-notif')  #linkedin受限
        #     self.linkedin_limit = 1
        # except :
        #     pass
        return True

    def webAction(self):
        """
        模拟浏览器动作
        :return: true
        """

        ##################################################################################
        ActionChains(self.driver).send_keys(Keys.END).perform()# 拉到底
        time.sleep(3)
        #############################
        #
        #  button按键click不管用，只有用Keys.ENTER。。
        #
        ##############################
        #####################简介点击(已知有两个种情况)###################################################
        try:
            menu = self.driver.find_element_by_class_name("button-tertiary-small")
            ActionChains(self.driver).move_to_element(menu).perform()
            menu.send_keys(Keys.ENTER)
        except:pass
        try:
            menu = self.driver.find_element_by_class_name("truncate-multiline--button")
            ActionChains(self.driver).move_to_element(menu).perform()
            menu.send_keys(Keys.ENTER)
        except:pass
        time.sleep(6)
        ########################发布的文章(如果存在，则不点击，并且下边的点击减少相应的个数)######################################
        # try:
        #     menu = self.driver.fin("pv-recent-activity-section__see-more-inline")
        #     len(menu)
        #
        # except:pass
        # time.sleep(6)
        ########################工作经历、个人成就等的点击,有可能有很多，要点击多次#######################################
        # for i in self.driver.find_elements_by_class_name('ui-tablink'):# 这里主要是应对推荐信中已发出的信，如果没有这个会陷入死循环。
        #     ActionChains(self.driver).move_to_element(i).perform()  #可能有两个或则一个
        #     i.send_keys(Keys.ENTER)
        #     time.sleep(1)
        #     frontLen = 0
        #     backLen = 0
        #     while True:
        #         buttonMore = self.driver.find_elements_by_xpath("//div//button[@class='pv-profile-section__see-more-inline link']")
        #         frontLen = len(buttonMore)
        #         if len(buttonMore) != 0:
        #             for menu in buttonMore:
        #                 try:
        #                     ActionChains(self.driver).move_to_element(menu).perform()
        #                     menu.send_keys(Keys.ENTER)
        #                     time.sleep(1)
        #                 except:pass
        #         backLen = len(self.driver.find_elements_by_xpath("//div//button[@class='pv-profile-section__see-more-inline link']"))
        #         if frontLen == backLen:
        #             break


        #############工作经历、个人成就等的点击,有可能有很多，要点击多次################################
        try:
            limitNum = 21 #限定一下次数，怕万一陷入了死循环。。
            while limitNum:
                limitNum -= 1
                buttonMore = self.driver.find_elements_by_xpath("//div//button[@class='pv-profile-section__see-more-inline link']")
                if len(buttonMore) != 0:
                    for i in self.driver.find_elements_by_class_name('ui-tablink'):
                        try:
                            ActionChains(self.driver).move_to_element(i).perform()  # 可能有两个或则一个
                            i.send_keys(Keys.ENTER)
                            time.sleep(1)
                        except:pass
                        buttonMore = self.driver.find_elements_by_xpath("//div//button[@class='pv-profile-section__see-more-inline link']")
                        for menu in buttonMore:
                            try:
                                ActionChains(self.driver).move_to_element(menu).perform()
                                menu.send_keys(Keys.ENTER)
                                time.sleep(1)
                            except:pass
                else:break
        except:pass
        ############个人成就的按钮(很蛋疼，边点击，边解析)###################################################
        try:
            buttonMore = self.driver.find_elements_by_class_name("pv-accomplishments-block__expand")
            if len(buttonMore) != 0:
                for menu in buttonMore:
                    type = menu.find_element_by_xpath("../h3[@class='pv-accomplishments-block__title']").text
                    try:
                        ActionChains(self.driver).move_to_element(menu).perform()
                        menu.send_keys(Keys.ENTER)
                        limitNum = 21
                        while limitNum:   #个人成就里面可能有【更多按钮】
                            limitNum = limitNum - 1
                            _buttonMore = self.driver.find_elements_by_xpath(
                                "//div//button[@class='pv-profile-section__see-more-inline link']")
                            if len(_buttonMore) != 0:
                                for _menu in _buttonMore:
                                    try:
                                        ActionChains(self.driver).move_to_element(_menu).perform()
                                        _menu.send_keys(Keys.ENTER)
                                        time.sleep(1)
                                    except:pass
                            else:break
                        time.sleep(1)
                    except:pass
                    self.parse.typeInfo(type, self.driver) #一边点击，一边解析
        except:pass
        ############点击详细说明#####################################

        for menu in self.driver.find_elements_by_class_name('pv-profile-section__show-more-detail'):
            try:
                ActionChains(self.driver).move_to_element(menu).perform()
                menu.send_keys(Keys.ENTER)
                time.sleep(1)
            except:
                pass
        ##########################################点击技能#############################################
        try:
            menu = self.driver.find_element_by_class_name("pv-skills-section__additional-skills")   #技能进行加载更多点击
            ActionChains(self.driver).move_to_element(menu).perform()
            menu.click()
        except : pass
        time.sleep(3)
        ########################个人联系########################################
        try:
            menu = self.driver.find_element_by_class_name("contact-see-more-less")   #技能进行加载更多点击
            ActionChains(self.driver).move_to_element(menu).perform()
            menu.send_keys(Keys.ENTER)
        except : pass
        time.sleep(3)

        return True

    # def save_page(self,page_source,filePath):
    #     """
    #     存储页面
    #     :param page_source:
    #     :return: null
    #     """
    #     fp = codecs.open(filePath, 'w', encoding='utf8')
    #     fp.write(page_source)
    #     fp.close()

    # def captureUrls(self):
    #     """
    #     得到其他用户的主页url
    #     :return:null
    #     """
    #     try:
    #         for item in self.driver.find_elements_by_class_name("pv-browsemap-section__member-container"):
    #             url = {}
    #             url['person_website'] = item.find_element_by_tag_name("a").get_attribute("href")
    #             if url['person_website'].split('/')[0] == 'https:':
    #                 time.sleep(10 * 60 * 60)
    #             url['isInterestSchool'] = False
    #             url['isInterestCompanies'] = False
    #             url['isInfluencers'] = False
    #             url['isRecentActivityPosts'] = False
    #             url['isView'] = False
    #             try:self.__dataStorage.get(self.urlName).update({'person_website':url['person_website']},{'$set':url},upsert=True)
    #             except DuplicateKeyError as DUEerr:
    #                 self.getUrlsLogger.error(DUEerr.message)
    #     except NoSuchElementException:
    #             self.getUrlsLogger.debug('browse-map-list_URL' + '\t' + 'no such element')

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
        # self.account_access = 0
        # self.urlNumber = 0
        self.processNum = PRECESSNUM
        self.accountQueue = Queue()
        self.urlQueue = Queue()
        self.dataStorage = DataStorage()
        self.__dataStorage = self.dataStorage.dataStorage
        self.accountName = ACCOUNT.get('name')
        self.urlName = LINKEDINURL.get('name')
        self.usersName = LINKEDINUSERS.get('name')

    def __getAccount(self):
        """
        从数据库获得账户名和密码
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

    def __getUrl(self):
        """
        读取没有读取过的url
        :return:
        """
        for url in self.__dataStorage.get(self.urlName).find({'isView':False,'alive':{'$exists':False}},{'_id':0,'person_website':1}).limit(URLLIMIT):
            self.urlQueue.put(url['person_website'])

    # def assert_user(self):
    #     for account in self.__name_pwd_collection.find({'user_state':'unknown'},{'_id':0,'email':1,'ld_pwd':1}):
    #         self.account_queue.put(account)
    #     for account in self.__name_pwd_collection.find({'user_state':'exception'},{'_id':0,'email':1,'ld_pwd':1}):
    #         self.account_queue.put(account)
    #     while self.account_queue.qsize() :
    #         # driver = webdriver.Chrome('D:\yj_project\linkedin\chromedriver.exe')
    #         driver = webdriver.PhantomJS()
    #         account = self.account_queue.get()
    #         email = account['email']
    #         password = account['ld_pwd']
    #         try:
    #             driver.get('https://www.linkedin.com/uas/login')
    #             WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, "inner-wrapper")))
    #             driver.find_element_by_id('session_key-login').send_keys(email)
    #             driver.find_element_by_id('session_password-login').send_keys(password)
    #             driver.find_element_by_css_selector('input#btn-primary.btn-primary').click()
    #             time.sleep(9)
    #             if driver.current_url == 'https://www.linkedin.com/uas/consumer-email-challenge':
    #                 print ('email:'+ email + ' ' + 'login fail!')
    #                 self.__name_pwd_collection.update({'email':email}, {'$set':{'user_state':'exception'}})
    #             else :
    #                 WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, "member")))
    #                 print ('email:'+ email + ' ' + 'login success!')
    #                 self.__name_pwd_collection.update({'email':email}, {'$set':{'user_state':'good'}})
    #         except Exception as e:
    #             print e.message
    #             self.__name_pwd_collection.update({'email':email}, {'$set':{'user_state':'unknown'}})
    #             pass
    #         finally:
    #             driver.quit()

    ##############################################
    #
    #  认定一个账号可以无限制的采集用户信息
    #
    ################################################
    def RunCrawler(self):
        while True :
            try:
                if self.accountQueue.qsize()==0:
                    if not self.__getAccount() :##########如果没有账号，等待3个小时，再次循环###############
                        print "sleep"
                        time.sleep(3 * 60 * 60) #休息3个小时
                        continue
            except:
                print "maybe mongodb or network have a problem"
                time.sleep(10 * 60)

            pool = Pool(self.processNum)
            [pool.apply_async(self.__RunCrawler) for i in range(self.processNum)]
            pool.close()
            pool.join()


    def __RunCrawler(self):
        while True:
            try :
                crawler = LinkedinCrawler(self.__dataStorage)
                if self.accountQueue.qsize() == 0:
                    break
                # if self.urlQueue.qsize() < 3:   #假定的需要爬取的用户（url）一定是足够的，没有写保护措施（即url没有的情况）
                #     self.__getUrl()
                account = self.accountQueue.get(timeout=3)
                if not crawler.login(account['email'],account['password']):
                    crawler.closeWeb()
                    continue

                while True:
                    if self.urlQueue.qsize() < 3:  # 假定的需要爬取的用户（url）一定是足够的，没有写保护措施（即url没有的情况）
                        self.__getUrl()
                    LinkedinUrl = self.urlQueue.get()
                    crawler.processPage(LinkedinUrl)
                        # crawler.captureUrls()
                        # self.__dataStorage.get(self.urlName).insert()



                # crawler.capture_urls(account['email'])
                # while count < 50:
                #     if self.url_queue.qsize() < 3:
                #         self.get_url()
                #     if not crawler.process_page(self.url_queue.get()):
                #         no_linked_count += 1
                #         if no_linked_count > 6 :  #在这个账号1次爬取过程中如果超时、不能爬取等情况多余20次，换个账号。
                #             break
                #         continue
                #     no_linked_count = 0     #能爬一个，清0
                #     if crawler.linkedin_limit == 1 :    #发现linkedin所限，跳出循环
                #         break
                #     crawler.capture_urls(account['email'])
                #     self.__name_pwd_collection.update_one({'email':account['email']},{'$inc':{'day_num':1}})
                #     self.urlNumber += 1
                #     print self.urlNumber
                #     count += 1
                #     print count
                # if count > 49 or crawler.linkedin_limit == 1:   #账号爬取了50个用户信息或者所限的情况下
                #     crawler.update_account(account['email'])
                #     crawler.linkedin_limit = 0

            except Exception as e:
                print 6
                time.sleep(30)
                print e.message
            finally:
                crawler.closeWeb()


if __name__ == '__main__':

    Crawler = MultiProcessCrawler()
    Crawler.RunCrawler()
