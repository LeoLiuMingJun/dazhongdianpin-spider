import csv
import os
import time

from selenium.common import exceptions

from driver import Driver


class StoreInfo(object):
    reference_data = {
        "food": "ch10",
        "SPA": "ch50/g158",
    }

    def __init__(self, city, industry):
        self.city = city
        self.industry = industry
        self.driver = Driver().driver
        time.sleep(1)

    def get_content_list(self):
        result = []

        reviews = self.driver.find_elements_by_xpath('//*[@id="shop-all-list"]/ul/li')
        for review in reviews:
            info = {
                "store_id": review.find_element_by_xpath(
                    './/div[contains(@class,"pic")]/a'
                ).get_attribute("data-shopid"),
                "city": self.city,
                "industry": self.industry,
                "store_name": review.find_element_by_xpath(
                    './/div[contains(@class,"pic")]/a/img'
                ).get_attribute("title"),
            }
            try:
                info["store_score"] = review.find_element_by_xpath(
                    './/div[contains(@class,"star_score_sml")]'
                ).text
            except exceptions.NoSuchElementException:
                info["store_score"] = "0"

            result.append(info)

        return result

    def run(self):
        print(f"collecting store info {self.city}, {self.industry} started")
        basic_url = (
            f"https://www.dianping.com/{self.city}/{self.reference_data[self.industry]}"
        )

        self.driver.get(basic_url)
        time.sleep(60)
        result = []

        count = 1
        while True:
            result.extend(self.get_content_list())
            print(f"now page {count}")
            count += 1
            try:
                next_url = self.driver.find_element_by_xpath(
                    '//*[@title="下一页"]'
                ).get_attribute("href")
                self.driver.get(next_url.replace("http", "https"))
                # time.sleep(5)
            except exceptions.NoSuchElementException:  # last page
                print("Already last page")
                break

        # self.save_content(content_list)
        print(f"store info done")

        with open("data/store.csv", "a") as f:
            fieldnames = [
                "store_id",
                "store_name",
                "city",
                "industry",
                "store_score",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if os.stat("data/store.csv").st_size == 0:
                writer.writeheader()
            for record in result:
                writer.writerow(record)
            f.write("\n")
        time.sleep(5)
        self.driver.quit()


if __name__ == "__main__":
    start_time = time.time()
    locations = [
        "beijing",
        "shanghai",
        "guangzhou",
        "shenzheng",
        "chengdu",
        "hangzhou",
        "chongqing",
        "wuhan",
        "suzhou",
        "xian",
        "tianjin",
        "nanjing",
        "zhengzhou",
        "changsha",
        "shenyang",
        "qingdao",
        "ningbo",
        "dongguan",
        "wuxi",
    ]
    for location in locations:
        StoreInfo(location, "SPA").run()
        print("--- %s seconds ---" % (time.time() - start_time))
        time.sleep(10)
