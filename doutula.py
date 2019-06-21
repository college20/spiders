# -*- coding: utf-8 -*-
#@Author    : huinono
#@time      : 2019/6/20 0020 20:06
#@File      : doutula.py
#@Software  : PyCharm

import requests
import re
from lxml import etree

class DoutuLa(object):
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36'}

    def get_image_message(self,page):
        url = 'http://www.doutula.com/article/list/?page={}'.format(page)
        response = requests.get(url=url,headers=self.headers)
        html = response.text
        #获取图片链接和图片名字
        message_list = re.findall(r'data-original="(.*?)".*?alt="(.*?)"',html)
        return message_list

    def download_picture(self,image_list):
        for image in image_list:
            #访问图片链接下载图片
            response = requests.get(url=image[0],headers=self.headers)
            text = response.content
            #取出图片名字
            name = image[1].replace('，','').replace('?','').replace('！','').replace(',','').replace('？','')
            #取出图片格式
            suffix = image[0].split('.')[-1]
            #保存图片
            self.save_picture(name,suffix,text)

    def save_picture(self,name,suffix,text):
        with open(r'./data_file/DTL_picture/{}.{}'.format(name,suffix),'wb') as f:
            f.write(text)

if __name__=='__main__':
    DoutuLa = DoutuLa()
    for i in range(1,5):
        image_list = DoutuLa.get_image_message(i)
        DoutuLa.download_picture(image_list)



