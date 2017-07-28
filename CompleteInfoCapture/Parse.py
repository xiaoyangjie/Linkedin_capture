# coding=utf-8

import logging
import logging.config

import time
from selenium.common.exceptions import NoSuchElementException


class Parse():

    def __init__(self):
        self.processPageLogger = logging.getLogger('process_page')
        self.getUrlsLogger = logging.getLogger('get_urls')
        self.usr = {}
        self.url = []
        self.userPosts = []
        self.person_website = ''
        self.recentActivityPosts = {}
        self.followingInfluencers = {}
        self.followingCompanies = {}
        self.followingSchools = {}


    ############解析大部分内容，如果有需要可以函数分离，写得更细###############
    def pageParse(self, driver):
        # 爬取姓名
        try:
            self.usr['name'] = driver.find_element_by_class_name("pv-top-card-section__name").text
        except NoSuchElementException:
            self.processPageLogger.debug('name' + '\t' + 'no such element')

        # 个人主页链接
        self.usr['person_website'] = self.person_website

        # 爬取头像url
        try:
            avater = driver.find_element_by_class_name("pv-top-card-section__photo")
            self.usr['profile_images_url'] = avater.find_element_by_tag_name("img").get_attribute("src")
        except NoSuchElementException:
            self.processPageLogger.debug('profile_images_url' + '\t' + 'no such element')

        # 爬取职位
        try:
            self.usr['title'] = driver.find_element_by_class_name("pv-top-card-section__headline").text
        except NoSuchElementException:
            self.processPageLogger.debug('title' + '\t' + 'no such element')

        # 爬取公司地址
        try:
            self.usr['company_location'] = driver.find_element_by_class_name("pv-top-card-section__location").text
        except NoSuchElementException:
            self.processPageLogger.debug('company_location' + '\t' + 'no such element')

        # 爬取现在的公司
        try:
            self.usr['current_company'] = driver.find_element_by_class_name('pv-top-card-section__company').text
        except NoSuchElementException:
            self.processPageLogger.debug('current_company' + '\t' + 'no such element')

        # 爬取简单教育情况
        try:
            self.usr['education_overview'] = driver.find_element_by_class_name('pv-top-card-section__school').text
        except NoSuchElementException:
            self.processPageLogger.debug('education_overview' + '\t' + 'no such element')

        # 爬取背景总概
        try:
            self.usr['background_summary'] = driver.find_element_by_class_name("pv-top-card-section__summary").text
        except NoSuchElementException:
            self.processPageLogger.debug('background_summary' + '\t' + 'no such element')

        # 爬取从业经历
        try:
            exp_overview = driver.find_elements_by_class_name('pv-position-entity')
            temp_list = []
            for item in exp_overview:
                temp = {}
                try:
                    temp['company'] = item.find_element_by_class_name("pv-position-entity__secondary-title").text
                except:
                    pass
                try:
                    temp['title'] = item.find_element_by_tag_name("h3").text
                except:
                    pass
                try:
                    temp['time'] = item.find_element_by_class_name("pv-entity__date-range").text
                except:
                    pass
                try:
                    temp['duration'] = item.find_element_by_class_name("pv-entity__duration").text
                except:
                    pass
                try:
                    temp['description'] = item.find_element_by_class_name("pv-entity__description").text
                except:
                    pass
                temp_list.append(temp)
            if temp_list:
                self.usr['job_experience'] = temp_list
        except NoSuchElementException:
            self.processPageLogger.debug('job_experience' + '\t' + 'no such element')

        # 爬取详细教育情况
        try:
            temp_list = []
            education = driver.find_elements_by_class_name("pv-education-entity")
            for item in education:
                temp = {}
                try:
                    temp['school name'] = item.find_element_by_class_name("pv-entity__school-name").text
                except:
                    pass
                try:
                    temp['major and degree'] = item.find_element_by_class_name("pv-entity__comma-item").text
                except:
                    pass
                try:
                    temp['date'] = item.find_element_by_class_name("pv-education-entity__date").text
                except:
                    pass
                try:
                    temp['description'] = item.find_element_by_class_name("pv-entity__description").text
                except:
                    pass
                temp_list.append(temp)
            if temp_list:
                self.usr['education_detail'] = temp_list
        except NoSuchElementException:
            self.processPageLogger.debug('education' + '\t' + 'no such element')

        # 志愿者经历
        try:
            exp_overview = driver.find_elements_by_class_name('pv-volunteering-entity')
            temp_list = []
            for item in exp_overview:
                temp = {}
                try:
                    temp['company'] = item.find_element_by_class_name("pv-volunteer-entity__secondary-title").text
                except:
                    pass
                try:
                    temp['title'] = item.find_element_by_tag_name("h3").text
                except:
                    pass
                try:
                    temp['time'] = item.find_element_by_class_name("pv-entity__date-range").text
                except:
                    pass
                try:
                    temp['duration'] = item.find_element_by_class_name("pv-entity__duration").text
                except:
                    pass
                try:
                    temp['description'] = item.find_element_by_class_name("pv-entity__description").text
                except:
                    pass
                temp_list.append(temp)
            if temp_list:
                self.usr['volunteer_experience'] = temp_list
        except NoSuchElementException:
            self.processPageLogger.debug('volunteer_experience' + '\t' + 'no such element')

        # 爬取技能
        try:
            temp_list = []
            for item in driver.find_elements_by_class_name('pv-skill-entity--featured'):
                temp = {}
                try:
                    temp['skill_name'] = item.find_element_by_class_name('pv-skill-entity__skill-name').text
                except:
                    pass
                try:
                    temp['skill_points'] = item.find_element_by_class_name('pv-skill-entity__endorsement-count').text
                except:
                    pass
                temp_list.append(temp)
            if temp_list:
                self.usr['skills'] = temp_list
        except NoSuchElementException:
            self.processPageLogger.debug('skills' + '\t' + 'no such element')

        # 爬取post内容
        try:
            temp_list = []
            for item in driver.find_elements_by_class_name("artdeco-carousel-slide-container"):
                postUrl = item.find_element_by_tag_name('a').get_attribute('href')
                temp_list.append(postUrl)
                self.userPosts.append({'person_website': self.person_website, 'postUrl': postUrl, 'isView':False})

            # temp = {}
            # try:temp['post_url'] = item.find_element_by_tag_name("a").get_attribute("href")
            # except:pass
            # try:temp['photo_url'] = item.find_element_by_tag_name("img").get_attribute("src")
            # except:pass
            # try:temp['brief_introduction'] = item.find_element_by_class_name("influencer-post-title").text
            # except:pass
            # try:temp['post_date'] = item.find_element_by_class_name("influencer-post-published").text
            # except:pass
            # temp_list.append(temp)
            if temp_list:
                self.usr['posts'] = temp_list
        except NoSuchElementException:
            self.processPageLogger.debug('posts' + '\t' + 'no such element')


        # twitter账号
        try:
            temp_list = []
            for item in driver.find_element_by_class_name("ci-twitter").find_elements_by_tag_name("li"):
                temp = {}
                temp['screen_name'] = item.find_element_by_tag_name('a').text
                temp['url'] = item.find_element_by_tag_name('a').get_attribute('href')
                temp_list.append(temp)
            if temp_list:
                self.usr['twitter'] = temp_list
        except NoSuchElementException:
            self.processPageLogger.debug('twitter' + '\t' + 'no such element')

        # 网站
        try:
            temp_list = []
            for item in driver.find_element_by_class_name("ci-websites").find_elements_by_tag_name("li"):
                temp = {}
                temp['description'] = item.text
                temp['url'] = item.find_element_by_tag_name('a').get_attribute('href')
                temp_list.append(temp)
            if temp_list:
                self.usr['website'] = temp_list
        except NoSuchElementException:
            self.processPageLogger.debug('website' + '\t' + 'no such element')

        # 邮箱
        try:
            self.usr['email'] = driver.find_element_by_class_name("ci-email").find_element_by_class_name("pv-contact-info__contact-item").text
        except NoSuchElementException:
            self.processPageLogger.debug('email' + '\t' + 'no such element')

    ################这里主要是解析个人成就里面的内容，只有一个一个去解析,有九种################
    def typeInfo(self, type, driver):
        if type == u'荣誉奖项':
            self.__parseHonor(driver)
        if type == u'语言能力':
            self.__parseLanguages(driver)
        if type == u'参与组织':
            self.__parseOrganization(driver)
        if type == u'资格认证':
            self.__parseCertification(driver)
        if type == u'出版作品':
            self.__parsePublications(driver)
        if type == u'所学课程':
            self.__parseCourses(driver)
        if type == u'专利发明':
            self.__parsePatent(driver)
        if type == u'所做项目':
            self.__parseProjects(driver)
        if type == u'测试成绩':
            self.__parseTestScores(driver)

    def __parseCourses(self, driver):
        # 课程
        temp_list = []
        try:
            temp_list = []
            for item in driver.find_element_by_xpath(
                    "//button[@data-control-name='accomplishments_collapse_courses']"). \
                    find_element_by_xpath(
                "../div[@class='pv-accomplishments-block__list-container']").find_elements_by_tag_name('li'):
                temp = {}
                try:
                    temp['courses_name'] = item.find_element_by_tag_name("h4").text
                except:
                    pass
                try:
                    temp['courses_num'] = item.find_element_by_class_name(
                        "pv-accomplishment-entity__course-number").text
                except:
                    pass
                temp_list.append(temp)
            if temp_list:
                self.usr['courses'] = temp_list
        except NoSuchElementException:
            self.processPageLogger.debug('courses' + '\t' + 'no such element')

    def __parsePatent(self,driver):
        #专利
        temp_list = []
        try:
            temp_list = []
            for item in driver.find_element_by_xpath(
                    "//button[@data-control-name='accomplishments_collapse_patents']"). \
                    find_element_by_xpath(
                "../div[@class='pv-accomplishments-block__list-container']").find_elements_by_tag_name('li'):
                temp = {}
                try:
                    temp['patents_name'] = item.find_element_by_tag_name("h4").text
                except:
                    pass
                try:
                    temp['patents_organization'] = item.find_element_by_class_name(
                        "pv-accomplishment-entity__issuer").text
                except:
                    pass
                try:
                    temp['patents_time'] = item.find_element_by_class_name("pv-accomplishment-entity__date").text
                except:
                    pass
                try:
                    temp['patents_content'] = item.find_element_by_class_name(
                        "pv-accomplishment-entity__description").text
                except:
                    pass
                temp_list.append(temp)
            if temp_list:
                self.usr['patents'] = temp_list
        except NoSuchElementException:
            self.processPageLogger.debug('patents' + '\t' + 'no such element')

    def __parseProjects(self, driver):
        # 项目
        temp_list = []
        try:
            temp_list = []
            for item in driver.find_element_by_xpath(
                    "//button[@data-control-name='accomplishments_collapse_projects']"). \
                    find_element_by_xpath(
                "../div[@class='pv-accomplishments-block__list-container']").find_elements_by_tag_name('li'):
                temp = {}
                try:
                    temp['projects_name'] = item.find_element_by_tag_name("h4").text
                except:
                    pass
                try:
                    temp['projects_time'] = item.find_element_by_class_name("pv-accomplishment-entity__date").text
                except:
                    pass
                try:
                    temp['projects_content'] = item.find_element_by_class_name(
                        "pv-accomplishment-entity__description").text
                except:
                    pass
                temp_list.append(temp)
            if temp_list:
                self.usr['projects'] = temp_list
        except NoSuchElementException:
            self.processPageLogger.debug('projects' + '\t' + 'no such element')

    def __parseTestScores(self, driver):
        # 测试成绩
        temp_list = []
        try:
            temp_list = []
            for item in driver.find_element_by_xpath(
                    "//button[@data-control-name='accomplishments_collapse_testScores']"). \
                    find_element_by_xpath(
                "../div[@class='pv-accomplishments-block__list-container']").find_elements_by_tag_name('li'):
                temp = {}
                try:
                    temp['testScores_name'] = item.find_element_by_tag_name("h4").text
                except:
                    pass
                try:
                    temp['testScores_score'] = item.find_element_by_class_name(
                        "pv-accomplishment-entity__score").text
                except:
                    pass
                try:
                    temp['testScores_time'] = item.find_element_by_class_name("pv-accomplishment-entity__date").text
                except:
                    pass
                try:
                    temp['testScores_content'] = item.find_element_by_class_name(
                        "pv-accomplishment-entity__description").text
                except:
                    pass
                temp_list.append(temp)
            if temp_list:
                self.usr['testScores'] = temp_list
        except NoSuchElementException:
            self.processPageLogger.debug('testScores' + '\t' + 'no such element')

    def __parseHonor(self, driver):
        # 荣誉奖项
        temp_list = []
        try:
            temp_list = []
            for item in driver.find_element_by_xpath(
                    "//button[@data-control-name='accomplishments_collapse_honors']"). \
                    find_element_by_xpath(
                "../div[@class='pv-accomplishments-block__list-container']").find_elements_by_tag_name('li'):
                temp = {}
                try:temp['honor_name'] = item.find_element_by_tag_name("h4").text
                except :pass
                try:temp['honor_organization'] = item.find_element_by_class_name("pv-accomplishment-entity__issuer").text
                except:pass
                try:temp['honor_time'] = item.find_element_by_class_name("pv-accomplishment-entity__date").text
                except:pass
                try:temp['honor_content'] = item.find_element_by_class_name("pv-accomplishment-entity__description").text
                except:pass
                temp_list.append(temp)
            if temp_list:
                self.usr['honor'] = temp_list
        except NoSuchElementException:
            self.processPageLogger.debug('honor' + '\t' + 'no such element')

    def __parseLanguages(self, driver):
        # 语言
        temp_list = []
        try:
            for item in driver.find_element_by_xpath(
                    "//button[@data-control-name='accomplishments_collapse_languages']"). \
                    find_element_by_xpath(
                "../div[@class='pv-accomplishments-block__list-container']").find_elements_by_tag_name('li'):
                temp = {}
                temp['languages'] = item.find_element_by_tag_name("h4").text
                try:temp['languages-proficiency'] = item.find_element_by_class_name("pv-accomplishment-entity__proficiency").text
                except:pass
                temp_list.append(temp)
            if temp_list:
                self.usr['languages'] = temp_list
        except NoSuchElementException:
                self.processPageLogger.debug('languages' + '\t' + 'no such element')

    def __parseOrganization(self, driver):
        # 参与组织
        temp_list = []
        try:
            for item in driver.find_element_by_xpath(
                    "//button[@data-control-name='accomplishments_collapse_organizations']"). \
                    find_element_by_xpath(
                "../div[@class='pv-accomplishments-block__list-container']").find_elements_by_tag_name('li'):
                temp = {}
                try:
                    temp['name'] = item.find_element_by_tag_name("h4").text
                except :
                    pass
                try:
                    temp['position'] = item.find_element_by_class_name(
                        "pv-accomplishment-entity__position").text
                except:
                    pass
                try:
                    temp['time'] = item.find_element_by_class_name("pv-accomplishment-entity__date").text
                except:
                    pass
                try:temp['descripation'] = item.find_element_by_class_name(
                        "pv-accomplishment-entity__description").text
                except:pass
                temp_list.append(temp)
            if temp_list:
                self.usr['organization'] = temp_list
        except NoSuchElementException:
            self.processPageLogger.debug('organization' + '\t' + 'no such element')


    def __parseCertification(self, driver):
        # 认证
        temp_list = []
        try:
            for item in driver.find_element_by_xpath(
                    "//button[@data-control-name='accomplishments_collapse_certifications']"). \
                    find_element_by_xpath(
                "../div[@class='pv-accomplishments-block__list-container']").find_elements_by_tag_name('li'):
                temp = {}
                try:temp['certification_item'] = item.find_element_by_tag_name("h4").text
                except :pass
                try:temp['certification_organization'] = item.find_elements_by_tag_name("a")[0].find_element_by_tag_name('p').text
                except:pass
                try:temp['certification_date'] = item.find_element_by_class_name("pv-accomplishment-entity__date").text
                except:pass
                temp_list.append(temp)
            if temp_list:
                self.usr['certification'] = temp_list
        except NoSuchElementException:
                self.processPageLogger.debug('certification' + '\t' + 'no such element')

    def __parsePublications(self, driver):
        # 爬取出版物
        temp_list = []
        try:
            for item in driver.find_element_by_xpath("//button[@data-control-name='accomplishments_collapse_publications']").\
                    find_element_by_xpath("../div[@class='pv-accomplishments-block__list-container']").find_elements_by_tag_name('li'):
                temp = {}
                try:temp['publications_title'] = item.find_element_by_tag_name("h4").text
                except:pass
                try:temp['publisher'] = item.find_element_by_class_name("pv-accomplishment-entity__publisher").text
                except:pass
                try:temp['publications_journal'] = item.find_element_by_class_name("pv-accomplishment-entity__description").text
                except:pass
                try:temp['publications_date'] = item.find_element_by_class_name("pv-accomplishment-entity__date").text
                except:pass
                temp_list.append(temp)
            if temp_list:
                self.usr['publications'] = temp_list
        except NoSuchElementException:
                self.processPageLogger.debug('publications' + '\t'+ 'no such elem0ent')

    def parseRecommentions(self,flag, driver):
        # 爬取推荐信息
        if flag == 0:
            key = 'rev_recommendations'
        else:
            key = 'send_recommendations'
        try:
            temp_list = []
            for item in driver.find_elements_by_class_name("pv-recommendation-entity"):
                temp = {}
                try:
                    temp['recommenderPersonWebsite'] = item.find_element_by_tag_name("a").get_attribute('href')
                except:
                    pass
                try:
                    temp['recommenderName'] = item.find_element_by_class_name(
                        'pv-recommendation-entity__detail').find_element_by_tag_name("h3").text
                except:
                    pass
                try:
                    temp['recommenderPosition'] = item.find_element_by_class_name(
                        "pv-recommendation-entity__headline").text
                except:
                    pass
                try:
                    temp['date'] = item.find_element_by_class_name("rec-extra").text
                except:
                    pass
                try:
                    temp['content'] = item.find_element_by_class_name("pv-recommendation-entity__text").text
                except:
                    pass
                if temp['recommenderName'] != u'':
                    temp_list.append(temp)
            if temp_list:
                self.usr[key] = temp_list
        except NoSuchElementException:
            self.processPageLogger.debug(key + '\t' + 'no such element')

    def captureUrls(self, driver):
        """
        得到其他用户的主页url
        :return:null
        """
        try:
            for item in driver.find_elements_by_class_name("pv-browsemap-section__member-container"):
                url = {}
                url['person_website'] = item.find_element_by_tag_name("a").get_attribute("href")
                if url['person_website'].split('/')[0] == 'https:':
                    time.sleep(10 * 60 * 60)
                url['isInterestSchool'] = False
                url['isInterestCompanies'] = False
                url['isInfluencers'] = False
                url['isRecentActivityPosts'] = False
                url['isView'] = False
                url['readNum'] = 0
                url['updateTime'] = 1
                self.url.append(url)
        except NoSuchElementException:
            self.getUrlsLogger.debug('browse-map-list_URL' + '\t' + 'no such element')

    def parseRecentActivityPosts(self, driver):
        try:
            temp_list = []
            for item in driver.find_elements_by_class_name('pv-post-entity--detail-page-format'):
                temp = {}
                try:
                    temp['author'] = item.find_element_by_tag_name('h4').text
                except:pass
                try:
                    temp['url'] = item.find_element_by_tag_name('a').get_attribute('href')
                except:
                    pass
                try:
                    temp['title'] = item.find_element_by_class_name('pv-post-entity__title').text
                except:
                    pass
                try:
                    temp['publish_location'] = item.find_element_by_class_name('pv-post-entity__by-line').text
                except:
                    pass
                try:
                    temp['date'] = item.find_element_by_class_name('pv-post-entity__created-date').text
                except:pass
                temp_list.append(temp)
            if temp_list:
                self.recentActivityPosts['recentActivityPosts'] = temp_list
        except NoSuchElementException:
            self.processPageLogger.debug('RecentActivityPosts' + '\t' + 'no such element')

    def parsePosts(self, driver):
        """

        :param driver:
        :return:
        """
        post = {}
        try:
            item = driver.find_element_by_class_name('pv-treasury-media-viewer__detail-info')
            try:
                post['post_url'] = item.find_element_by_tag_name('a').get_attribute('href')
            except:pass
            try:
                post['post_title'] = item.find_element_by_class_name('pv-treasury-media-viewer__title').text
            except:pass
            try:
                post['post_description'] = item.find_element_by_class_name('pv-treasury-media-viewer__description').text
            except:pass
        except NoSuchElementException:
            self.processPageLogger.debug('posts' + '\t' + 'no such element')
        return post

    def parseFollowingInfluencers(self, driver):
        """

        :param driver:
        :return:
        """
        try:
            temp_list = []
            for item in driver.find_elements_by_class_name(' entity-list-item'):
                temp = {}
                try:
                    temp['person_website'] = item.find_element_by_tag_name('a').get_attribute('href')
                except:
                    pass
                try:
                    temp['name'] = item.find_element_by_class_name('pv-entity__summary-title--has-hover').text
                except:
                    pass
                try:
                    temp['occupation'] = item.find_element_by_class_name('occupation ').text
                except:
                    pass
                try:
                    temp['follower-count'] = item.find_element_by_class_name('follower-count').text
                except:pass
                temp_list.append(temp)
            if temp_list:
                self.followingInfluencers['followingInfluencers'] = temp_list
        except NoSuchElementException:
            self.processPageLogger.debug('followingInfluencers' + '\t' + 'no such element')

    def parseFollowingCompanies(self, driver):
        """

        :param driver:
        :return:
        """
        try:
            temp_list = []
            for item in driver.find_elements_by_class_name(' entity-list-item'):
                temp = {}
                try:
                    temp['LinkedinCompanyUrl'] = item.find_element_by_tag_name('a').get_attribute('href')
                except:
                    pass
                try:
                    temp['companyName'] = item.find_element_by_class_name('pv-entity__summary-title--has-hover').text
                except:
                    pass
                try:
                    temp['follower-count'] = item.find_element_by_class_name('follower-count').text
                except:pass
                temp_list.append(temp)
            if temp_list:
                self.followingCompanies['followingCompanies'] = temp_list
        except NoSuchElementException:
            self.processPageLogger.debug('followingCompanies' + '\t' + 'no such element')

    def parseFollowingSchools(self, driver):
        """

        :param driver:
        :return:
        """
        try:
            temp_list = []
            for item in driver.find_elements_by_class_name(' entity-list-item'):
                temp = {}
                try:
                    temp['LinkedinSchoolUrl'] = item.find_element_by_tag_name('a').get_attribute('href')
                except:
                    pass
                try:
                    temp['schoolName'] = item.find_element_by_class_name('pv-entity__summary-title--has-hover').text
                except:
                    pass
                try:
                    temp['follower-count'] = item.find_element_by_class_name('follower-count').text
                except:pass
                temp_list.append(temp)
            if temp_list:
                self.followingSchools['followingSchools'] = temp_list
        except NoSuchElementException:
            self.processPageLogger.debug('followingSchools' + '\t' + 'no such element')