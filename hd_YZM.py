# !/usr/bin/env python
# -*- coding:utf-8 -*- 
# author:辉nono 2019/3/22 0022 22:28

import re
import time
import requests
import pytesser3
from lxml import etree
from PIL import  Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains

class Geetest(object):
    def __init__(self):
        options = Options()
        options.add_argument('--window-size=1366,768')
        self.driver = webdriver.Chrome(chrome_options=options)
        self.wait = WebDriverWait(self.driver,10)
    def go_to_register(self):
        try:
            self.driver.get("https://www.huxiu.com/")
            self.wait.until(EC.presence_of_element_located((
                By.XPATH,'//a[@class="js-login"]'))).click()
            self.wait.until(EC.presence_of_element_located((
                By.XPATH,'//input[@id="sms_username"]'
            ))).send_keys("smartliu it")
        except Exception as e:
            print('注册函数有误：%s'%e)
            self.driver.quit()
    def get_image(self):
        #没有缺陷的图片
        get_image_list = self.driver.find_elements_by_xpath('//div[@class="gt_cut_fullbg gt_show"]/div')
        print(len(get_image_list))
        style_list = [i.get_attribute('style') for i in get_image_list]
        image_url = re.search(r'url\("(.*?)"\);',style_list[0]).group(1)
        image_content = requests.get(image_url).content
        get_image = self.get_complete_image(style_list,image_content)
        #有缺陷的图片
        cut_get_image_list = self.driver.find_elements_by_xpath('//div[@class="gt_cut_fullbg gt_show"]/div')
        cut_style_list = [i.get_attribute('style') for i in cut_get_image_list]
        cut_image_url = re.search(r'url\("(.*?)"\);',cut_style_list[0]).group(1)
        cut_image_content = requests.get(cut_image_url).content
        cut_get_image = self.get_complete_image(style_list,cut_image_content)
        #对比两张照片,的到缺口位置
        return self.compare_image(get_image,cut_get_image)
    def get_complete_image(self,style_list,image):
        image_position_list = [re.findall(r'background-position: -(.*?)px -?(.*?)px;',i) for i in style_list]
        new_im = Image.new("RGB",(260,116))
        im = Image.open(BytesIO(image))
        up_count = dn_count = 0
        for i in image_position_list[:26]:
            croped = im.crop((int(i[0][0]),58,int(i[0][0]) + 10,116))
            new_im.paste(croped,(up_count,0))
            up_count += 10
        for i in image_position_list[26:]:
            croped = im.crop((int(i[0][0]),0,int(i[0][0]) + 10,58))
            new_im.paste(croped,(dn_count,58))
            dn_count += 10
        return new_im
    def compare_image(self,cut,no_cut):
        def compare_pixel(pixel1,pixel2):
            for i in range(3):
                if abs(pixel1[i]-pixel2[i])>50:
                    return False
        for i in range(260):
            for j in range(116):
                pixel1 = cut.getpixel((i,j))
                pixel2 = no_cut.getpixel((i,j))
                if compare_pixel(pixel1,pixel2) is False:
                    return i
    def slide(self,distance):
        button = self.wait.until(EC.visibility_of_element_located((
            By.XPATH,'//dic[@class="gt_slider_knob gt_show"]'
        )))
        ActionChains(self.driver).click_and_hold(button).perform()
        for i in self.track(distance-5):
            ActionChains(self.driver).move_by_offset(i,0).perform()
        ActionChains(self.driver).release().perform()
    def track(self,distance):
        t = 0.2
        current = 0
        mid = distance * 0.6
        speed = 0
        move_distance_list = []
        while current < distance:
            if current < mid:
                a = 5
            else:
                a = -10
            move_distance = speed*t + 0.5*a*t*t
            move_distance_list.append(round(move_distance))
            speed += (a*t)
            current += move_distance
        offset = sum(move_distance_list)*distance
        if offset > 0:
            move_distance_list.extend([-1]*offset)
        elif offset<0:
          move_distance_list.extend([1]*abs(offset))
        move_distance_list.extend([-1,-1,-1,-1,0,0,1,1,1,1,1,1,1,1,0,0,-1,-1,-1,-1])
        return move_distance_list

if __name__=='__main__':
    gee = Geetest()
    gee.go_to_register()
    distance = gee.get_image()
    gee.slide(distance)
