# coding=utf-8
import time

from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys


class WebAction(object):
    
    def __init__(self):
        pass
    
    def userWebAction(self, driver, parse):
        """
        模拟浏览器动作
        :return: true
        """

        ##################################################################################
        ActionChains(driver).send_keys(Keys.END).perform()# 拉到底
        time.sleep(9)
        #############################
        #
        #  button按键click不管用，只有用Keys.ENTER。。
        #
        ##############################
        #####################简介点击(已知有两个种情况)###################################################
        try:
            menu = driver.find_element_by_class_name("button-tertiary-small")
            ActionChains(driver).move_to_element(menu).perform()
            menu.send_keys(Keys.ENTER)
        except:pass
        try:
            menu = driver.find_element_by_class_name("truncate-multiline--button")
            ActionChains(driver).move_to_element(menu).perform()
            menu.send_keys(Keys.ENTER)
        except:pass
        time.sleep(3)
        #############工作经历、个人成就等的点击,有可能有很多，要点击多次################################
        try:
            limitNum = 600 #限定一下次数，怕万一陷入了死循环。。
            while limitNum:
                limitNum -= 1
                buttonMore = driver.find_elements_by_xpath("//div//button[@class='pv-profile-section__see-more-inline link']")
                if len(buttonMore) != 0:
                    for i in driver.find_elements_by_class_name('ui-tablink'):
                        try:
                            ActionChains(driver).move_to_element(i).perform()  # 可能有两个或则一个
                            i.send_keys(Keys.ENTER)
                            time.sleep(1)
                        except:pass
                        buttonMore =  driver.find_elements_by_xpath("//div//button[@class='pv-profile-section__see-more-inline link']")
                        for menu in buttonMore:
                            try:
                                ActionChains(driver).move_to_element(menu).perform()
                                menu.send_keys(Keys.ENTER)
                                time.sleep(1)
                            except:pass
                else:break
        except:pass
        ############推荐信有发出和收到的，边点击，边解析#####################################################
        flagType = 0 #用于判断收到还是发送的推荐信
        for i in driver.find_elements_by_class_name('ui-tablink'):
            try:
                ActionChains(driver).move_to_element(i).perform()  # 可能有两个或则一个
                i.send_keys(Keys.ENTER)
                time.sleep(1)
            except:
                pass
            parse.parseRecommentions(flagType, driver)
            flagType = flagType + 1
        ############个人成就的按钮(很蛋疼，边点击，边解析)###################################################
        try:
            buttonMore = driver.find_elements_by_class_name("pv-accomplishments-block__expand")
            if len(buttonMore) != 0:
                for menu in buttonMore:
                    type = menu.find_element_by_xpath("../h3[@class='pv-accomplishments-block__title']").text
                    try:
                        ActionChains(driver).move_to_element(menu).perform()
                        menu.send_keys(Keys.ENTER)
                        limitNum = 600
                        while limitNum:   #个人成就里面可能有【更多按钮】
                            limitNum = limitNum - 1
                            _buttonMore = driver.find_elements_by_xpath(
                                "//div//button[@class='pv-profile-section__see-more-inline link']")
                            if len(_buttonMore) != 0:
                                for _menu in _buttonMore:
                                    try:
                                        ActionChains(driver).move_to_element(_menu).perform()
                                        _menu.send_keys(Keys.ENTER)
                                        time.sleep(1)
                                    except:pass
                            else:break
                        time.sleep(1)
                    except:pass
                    parse.typeInfo(type, driver) #一边点击，一边解析
        except:pass
        ############点击详细说明#####################################

        for menu in driver.find_elements_by_class_name('pv-profile-section__show-more-detail'):
            try:
                ActionChains(driver).move_to_element(menu).perform()
                menu.send_keys(Keys.ENTER)
                time.sleep(1)
            except:
                pass
        ##########################################点击技能#############################################
        try:
            menu = driver.find_element_by_class_name("pv-skills-section__additional-skills")   #技能进行加载更多点击
            ActionChains(driver).move_to_element(menu).perform()
            menu.click()
        except : pass
        time.sleep(3)
        ########################个人联系########################################
        try:
            menu = driver.find_element_by_class_name("contact-see-more-less")
            ActionChains(driver).move_to_element(menu).perform()
            menu.send_keys(Keys.ENTER)
        except : pass
        time.sleep(3)

    def recentActivityPostsAction(self, driver):
        limitNum = 100
        while limitNum:
            limitNum = limitNum - 1
            postFrontNum = driver.find_elements_by_class_name('pv-post-entity--detail-page-format')
            ActionChains(driver).send_keys(Keys.END).perform()  # 拉到底
            time.sleep(3)
            postBackNum = driver.find_elements_by_class_name('pv-post-entity--detail-page-format')
            if postFrontNum == postBackNum :
                break

    def followingAction(self, driver):
        limitNum = 100
        while limitNum:
            limitNum = limitNum - 1
            postFrontNum = driver.find_elements_by_class_name(' entity-list-item')
            ActionChains(driver).send_keys(Keys.END).perform()  # 拉到底
            time.sleep(3)
            postBackNum = driver.find_elements_by_class_name(' entity-list-item')
            if postFrontNum == postBackNum:
                break