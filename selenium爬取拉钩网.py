# encoding: utf-8
import time

from selenium import webdriver
from lxml import etree
import csv

"""
selenium获取的源代码（page_source）是获取elements中的信息
"""


class LagouSpider(object):
    driver_path = r'D:\Program Files (x86)\Firefox\driver\geckodriver.exe'

    def __init__(self):
        self.driver = webdriver.Firefox(executable_path=self.driver_path)
        self.url = 'https://www.lagou.com/jobs/list_python?labelWords=&fromSearch=true&suginput='
        self.positions = []
        self.num = 0
        self.page_num = 1

    # 入口
    def run(self):
        self.driver.get(self.url)
        while True:
            source = self.driver.page_source
            self.parse_list_page(source)
            next_btn = self.driver.find_element_by_xpath("//div[@class='pager_container']/span[last()]")
            if 'pager_next_disabled' in next_btn.get_attribute('class'):
                break
            else:
                next_btn.click()
                self.page_num = self.page_num + 1
                self.num = 0
            # time.sleep(2)
        self.position_file(self.positions)

    # 每一页职位url
    def parse_list_page(self, source):
        html = etree.HTML(source)
        print()
        links = html.xpath("//a[@class='position_link']/@href")
        for link in links:
            self.request_detail_page(link)
            # time.sleep(2)

    # 打开职位详情
    def request_detail_page(self, url):
        self.driver.execute_script("window.open('%s')" % url)
        self.driver.switch_to.window(self.driver.window_handles[1])
        time.sleep(1)
        source = self.driver.page_source
        self.parse_detail_page(source)
        # time.sleep(2)
        # 关闭当前职业详情页并切换回职位url页
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    # 获取职位详情
    def parse_detail_page(self, source):
        html = etree.HTML(source)
        position_name = html.xpath('//span[@class="name"]/text()')[0]
        job_request_span = html.xpath('//dd[@class="job_request"]//span')
        salary = job_request_span[0].xpath('.//text()')[0].strip()
        city = job_request_span[1].xpath('.//text()')[0].replace('/', '').strip()
        work_years = job_request_span[2].xpath('.//text()')[0].replace('/', '').strip()
        education = job_request_span[3].xpath('.//text()')[0].replace('/', '').strip()
        company_name = html.xpath("//h2[@class='fl']/text()")[0].strip()

        desc = "".join(html.xpath("//dd[@class='job_bt']//text()")).strip()
        position = {
            'name': position_name,
            'company_name': company_name,
            'salary': salary,
            'city': city,
            'work_years': work_years,
            'education': education,
            'desc': desc
        }
        self.positions.append(position)
        print(self.positions)
        self.num = self.num + 1
        print('*' * 30, '第%d页第%d条' % (self.page_num, self.num), '*' * 30)

    # 所有职位保存在文件中
    def position_file(self, datalist):
        # 标题
        headers = ['name', 'company_name', 'salary', 'city', 'work_years', 'education', 'desc']

        # 内容 datalist

        # newline='' 在写入文件时另起一行是默认在前一行添加\n
        with open('lagouwang.csv', 'w', encoding='utf-8', newline='') as fp:
            # 写入标题（需要调用writeheader方法）
            writer = csv.DictWriter(fp, headers)
            writer.writeheader()

            # 写入大量数据
            writer.writerows(datalist)


if __name__ == '__main__':
    spider = LagouSpider()
    spider.run()
