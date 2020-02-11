import time
import re
import csv
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common import exceptions

DRIVER_PATH = '/Users/mingjunliu/Library/chromedriver'


class Driver(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        options = Options()
        options.add_argument("user-data-dir=/tmp/tarun")  # remember the login info
        self.driver = webdriver.Chrome(DRIVER_PATH, options=options)


class StoreReviews(object):

    @staticmethod
    def _score2class(s):
        # get num from str
        regex = r"\d+"
        score = int(re.search(regex, s).group())
        return '%.1f' % (score / 10)

    @staticmethod
    def save_content(content_list):
        with open("WYMusic_all_0.txt", "a", encoding="utf-8") as f:
            for content in content_list:
                content_str = content["title"] + "\nby " + content["author"] + "\n"
                f.write(content_str)

    def __init__(self, store_id):
        self.store_id = store_id
        self.driver = Driver().driver
        time.sleep(1)

    def get_content_list(self):
        result = []
        reviews = self.driver.find_elements_by_xpath('//*[@id="review-list"]/div[2]/div[3]/div[3]/div[3]/ul/li')
        for review in reviews:
            info = {}
            info['store_id'] = self.store_id
            info['author_id'] = review.find_element_by_xpath('./a').get_attribute('data-user-id')
            info['total_score'] = self._score2class(review.find_element_by_xpath(
                './div/div[@class="review-rank"]/span[contains (@class,"sml-rank-stars")]').get_attribute('class'))
            i = 1
            for score in review.find_elements_by_xpath('./div/div[@class="review-rank"]/span[@class= "score"]/span'):
                n, s = score.text.split('：')
                info[f'detail-{i} name'] = n
                info[f'detail-{i} score'] = s
                i += 1
            try:
                _tag = review.find_element_by_xpath('./div/div[@class="richtitle"]').text
                info['free_trial'] = '1' if _tag == '免费体验后点评' else '-1'
            except exceptions.NoSuchElementException:
                info['free_trial'] = '0'
            # TODO 评论暂时不需要
            # try:
            #     content = review.find_element_by_xpath('./div/div[@class="review-words Hide"]').get_attribute(
            #         'innerHTML')
            #     info['content'] = content[:content.find('<div class="less-words">')].strip()
            # except exceptions.NoSuchElementException:
            #     content = review.find_element_by_xpath('./div/div[@class="review-words"]').get_attribute('innerHTML')
            #     info['content'] = content
            result.append(info)

        return result

    def run(self):
        print(f'store {self.store_id} started')
        basic_url = f"http://www.dianping.com/shop/{self.store_id}/review_all"

        self.driver.get(basic_url)
        result = []
        count = 1
        while True:
            result.extend(self.get_content_list())
            print(f'now page {count}')
            count += 1
            # break  # TODO remove it
            try:
                self.driver.find_element_by_xpath('//*[@title="下一页"]').click()
                time.sleep(5)
            except exceptions.NoSuchElementException:  # last page
                print('Already last page')
                break

        # self.save_content(content_list)
        print(f"store {self.store_id} done")

        with open('./评论数据.csv', 'a') as csvfile:
            fieldnames = ['store_id', 'author_id', 'total_score', 'detail-1 name', 'detail-1 score', 'detail-2 name',
                          'detail-2 score', 'detail-3 name', 'detail-3 score', 'free_trial']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if os.stat("./评论数据.csv").st_size == 0:
                writer.writeheader()
            for record in result:
                writer.writerow(record)

        time.sleep(5)
        self.driver.quit()


if __name__ == '__main__':
    stores = [128015796,
              122427126,
              112528093,
              926694487,
              108313095,
              111848980,
              72370094,
              1335082579,
              64020413,
              5455422,
              67384715,
              131606867,
              131380608,
              129641244,
              97798368,
              129857137,
              124152688,
              69203123,
              102470681,
              38163919,
              96035886,
              103573725,
              56433502,
              1921936964,
              74620947,
              129787717,
              72347490,
              132099147,
              122064740,
              68195012,
              112169506,
              92988790]
    for store in stores:
        StoreReviews(store).run()
        time.sleep(10)
