# encoding: utf-8
import time

import requests
import threading
from lxml import etree
from urllib import request
from queue import Queue
import re
import os
"""
代码逻辑：
    每一页的url ===》 生产者（获取表情url） ====》每个表情的url ====》消费者（下载表情包）
"""

NUMBER = 1

# 生产者
class Procuder(threading.Thread):
    __headers = {
        'User - Agent': 'Mozilla / 5.0(Windows NT 10.0;WOW64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 70.0.3538.102Safari / 537.36',
    }

    # 继承父类的__init__并添加需要的参数
    def __init__(self, page_queue, img_queue, *arg, **kwargs):
        super(Procuder, self).__init__(*arg, **kwargs)
        self.page_quque = page_queue
        self.img_queue = img_queue

    # 主入口
    def run(self):
        global NUMBER
        while True:
            if self.page_quque.empty():
                break
            url = self.page_quque.get()
            self.parse_page(url)
            # print("====》当前线程：%s" %threading.current_thread())

    # 获取每一页中的表情包url
    def parse_page(self, url):
        response = requests.get(url, headers=self.__headers)
        text = response.text
        html = etree.HTML(text)
        imgs = html.xpath("//div[@class='page-content text-center']//img[@class!='gif']")

        # 获取表情的url
        for img in imgs:
            img_url = img.get('data-backup').replace('!dta', '')
            alt = img.get('alt')  # 获取图片名
            alt = re.sub(r'\W', '_', alt)
            suffix = os.path.splitext(img_url)[1]  # 获取后缀名
            filename = alt + suffix

            # 添加到img_queue队列中
            self.img_queue.put((img_url, filename))
            # print(self.img_queue.empty())


# 消费者
class Consumer(threading.Thread):

    # 继承父类的__init__并添加需要的参数
    def __init__(self, page_queue, img_queue, *arg, **kwargs):
        super(Consumer, self).__init__(*arg, **kwargs)
        self.page_quque = page_queue
        self.img_queue = img_queue

    def run(self):
        # 获取img_gueue中的数据
        while True:
            if self.img_queue.empty() and self.page_quque.empty():
                break
            img_url, filename = self.img_queue.get()
            request.urlretrieve(img_url, '多线程版images/' + filename)

            # print("====》当前线程：%s" % threading.current_thread())


def main():
    page_queue = Queue(100)
    img_queue = Queue(1000)
    for x in range(1,101):
        url = 'http://www.doutula.com/photo/list/?page=%d' % x
        page_queue.put(url)

    for x in range(5):
        t = Procuder(page_queue, img_queue,name="消费者：%d"%x)
        t.start()

    time.sleep(1)       #由于多线程的退出判断有误，只好先休眠一下

    for x in range(3):
        t = Consumer(page_queue, img_queue,name="消费者：%d" %x)
        t.start()


if __name__ == '__main__':
    main()
