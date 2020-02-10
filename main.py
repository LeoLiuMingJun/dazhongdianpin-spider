import time

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
    def __init__(self, store_id):
        self.store_id = store_id
        self.driver = Driver().driver
        time.sleep(1)

    def get_content_list(self):
        li_list = self.driver.find_elements_by_xpath("//*[@id='song-list-pre-cache']/div/div[1]/table/tbody/tr")
        content_list = []
        for li in li_list:
            term = {}
            term["title"] = li.find_element_by_xpath("./td[2]/div/div/div/span/a/b").get_attribute('title')
            term["author"] = li.find_element_by_xpath("./td[4]/div/span").get_attribute('title')
            content_list.append(term)
        return content_list

    def save_content(self, content_list):
        with open("WYMusic_all_0.txt", "a", encoding="utf-8") as f:
            for content in content_list:
                content_str = content["title"] + "\nby " + content["author"] + "\n"
                f.write(content_str)

    def run(self):

        basic_url = f"http://www.dianping.com/shop/{self.store_id}/review_all"

        self.driver.get(basic_url)

        while True:

            print(self.driver.find_element_by_xpath(
                '//*[@id="review-list"]/div[2]/div[3]/div[3]/div[3]/ul/li[1]/div/div[1]/a').text)
            try:
                self.driver.find_element_by_xpath('//*[@title="下一页"]').click()
                time.sleep(5)
            except exceptions.NoSuchElementException:  # last page
                print('Already last page')
                break

        # self.save_content(content_list)
        print("Done")
        time.sleep(5)
        self.driver.quit()


if __name__ == '__main__':
    StoreReviews('92363924').run()
