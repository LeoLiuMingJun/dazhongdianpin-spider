import csv
import json
import os
import re
import time

import cssutils
import requests
from lxml import etree
from selenium.common import exceptions

from driver import Driver


class StoreReviews(object):

    @staticmethod
    def get_css(css_url):

        # css file already loaded
        if os.path.exists(f'./svg_info/{hash(css_url)}.dat'):
            print('load from existing')
            with open(f'./svg_info/{hash(css_url)}.dat', 'r') as f:
                js = f.read()
                dic = json.loads(js)
                return dic

        print('load from new')
        css = requests.get(css_url).text

        css_dct = {}
        sheet = cssutils.parseString(css)
        svg_dct = {}
        for rule in sheet:
            selector = rule.selectorText
            styles = rule.style.cssText
            if '=' in selector:
                svg_dct[selector] = styles
            else:
                css_dct[selector] = styles
        # 将坐标与值对应
        pre_fix_re = r"\"([a-z]+)\""
        tmp = {}
        for k, v in svg_dct.items():
            _dct = {}
            for info in v.split('\n'):
                detail = info.split(':')
                _dct[detail[0]] = detail[1].strip().replace('"', '')

            key = re.search(pre_fix_re, k).group()
            tmp[key.replace('"', '')[:2]] = _dct
        svg_dct = tmp
        _mapping = {}
        for key, value in svg_dct.items():
            url = value['background-image'].replace('url(//', '').replace(');', '')
            html = etree.HTML(bytes(requests.get(f'https://{url}').text, 'utf-8'))
            result = html.xpath('//text')
            x = 0
            for txt in result:
                y = txt.attrib['y']
                for c in txt.text:
                    _mapping[f'{key},{x},{y}'] = c
                    x += 1
                x = 0
        _tmp = {}
        for key, value in css_dct.items():
            index_re = r'.+?(\d+).+?(\d+).+'
            x, y = re.search(index_re, value).groups()
            x = int(abs(int(x)) / 14)
            y = abs(int(y)) + int(svg_dct[key[1:3]]['height'][:2]) - 1
            try:
                _tmp[key[1:]] = _mapping[f'{key[1:3]},{x},{y}']
            except KeyError:
                # 干扰项目 跳过
                pass
        js_obj = json.dumps(_tmp)

        with open(f'./svg_info/{hash(css_url)}.dat', 'w') as f:
            f.write(js_obj)

        return _tmp

    @staticmethod
    def _score2class(s):
        # get num from str
        regex = r"\d+"
        score = int(re.search(regex, s).group())
        return '%.1f' % (score / 10)

    def __init__(self, store_id, city, industry):
        self.store_id = store_id
        self.city = city
        self.industry = industry
        self.driver = Driver().driver
        time.sleep(1)

    def get_content_list(self, mapping):
        result = []

        reviews = self.driver.find_elements_by_xpath('//*[@id="review-list"]/div[2]/div[3]/div[3]/div[3]/ul/li')
        for review in reviews:
            print(review.text)
            info = {}
            info['store_id'] = self.store_id
            info['city'] = self.city
            info['industry'] = self.industry
            info['author_id'] = review.find_element_by_xpath('./a').get_attribute('data-user-id')
            info['total_score'] = self._score2class(review.find_element_by_xpath(
                './div/div[@class="review-rank"]/span[contains (@class,"sml-rank-stars")]').get_attribute('class'))
            i = 1

            #  info['detail_score']
            for score in review.find_elements_by_xpath('./div/div[@class="review-rank"]/span[@class= "score"]/span'):
                n, s = score.text.split('：')
                info[f'detail-{i} name'] = n
                info[f'detail-{i} score'] = s
                i += 1

            # info['free_trial']
            try:
                _tag = review.find_element_by_xpath('./div/div[@class="richtitle"]').text
                info['free_trial'] = '1' if _tag == '免费体验后点评' else '-1'
            except exceptions.NoSuchElementException:
                info['free_trial'] = '0'

            # info['content']
            try:
                content = review.find_element_by_xpath('./div/div[@class="review-words Hide"]').get_attribute(
                    'innerHTML')
                comments = content[:content.find('<div class="less-words">')].strip()
            except exceptions.NoSuchElementException:
                content = review.find_element_by_xpath('./div/div[@class="review-words"]').get_attribute('innerHTML')
                comments = content
            res = r'<svgmtsi class="([a-z0-9]+)"></svgmtsi>'
            while True:
                try:
                    groups = re.search(res, comments).groups()
                    # print(groups)
                    comments = re.sub(res, f'|{groups[0]}|', comments, 1)
                except AttributeError:
                    break

            lst = comments.replace('||', "|").split('|')
            word = []
            for c in lst:
                if c in mapping:
                    word.append(mapping[c])
                else:
                    word.append(c)

            info['content'] = ''.join(word)
            # //*[@id="review_689070127_action"]/span[1]
            info['time_stamp'] = str(review.find_element_by_xpath('.//span[@class= "time"]').text).strip()
            result.append(info)

        return result

    def run(self):
        print(f'store {self.store_id} started')
        basic_url = f"http://www.dianping.com/shop/{self.store_id}/review_all"

        self.driver.get(basic_url)
        time.sleep(60)
        result = []

        count = 1
        css_link = self.driver.find_element_by_xpath('/html/head/link[4]').get_attribute('href')
        mapping = get_css(css_link)
        while True:
            result.extend(self.get_content_list(mapping))
            print(f'now page {count}')
            count += 1
            try:
                self.driver.find_element_by_xpath('//*[@title="下一页"]').click()
                time.sleep(10)
            except exceptions.NoSuchElementException:  # last page
                print('Already last page')
                break

        # self.save_content(content_list)
        print(f"store {self.store_id} done")

        with open('./评论数据.csv', 'a') as csvfile:
            fieldnames = ['store_id',
                          'city',
                          'industry',
                          'author_id',
                          'total_score',
                          'detail-1 name',
                          'detail-1 score',
                          'detail-2 name',
                          'detail-2 score',
                          'detail-3 name',
                          'detail-3 score',
                          'free_trial',
                          'content',
                          'time_stamp']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if os.stat("./评论数据.csv").st_size == 0:
                writer.writeheader()
            for record in result:
                writer.writerow(record)

        time.sleep(5)
        self.driver.quit()
