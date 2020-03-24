import csv
import os
import re
import time

from selenium.common import exceptions

from driver import Driver
from helper import get_css, class2score


class StoreReviews(object):
    def __init__(self, store_id, city, industry):
        self.store_id = store_id
        self.city = city
        self.industry = industry
        self.driver = Driver().driver
        # time.sleep(1)

    def get_content_list(self, mapping):
        result = []

        reviews = self.driver.find_elements_by_xpath(
            '//*[@id="review-list"]/div[2]/div[3]/div[3]/div[3]/ul/li'
        )
        for review in reviews:
            # print(review.text)
            info = {
                "store_id": self.store_id,
                "city": self.city,
                "industry": self.industry,
                "author_id": review.find_element_by_xpath("./a").get_attribute(
                    "data-user-id"
                ),
                "total_score": class2score(
                    review.find_element_by_xpath(
                        './div/div[@class="review-rank"]/span[contains (@class,"sml-rank-stars")]'
                    ).get_attribute("class")
                ),
            }
            i = 1

            #  info['detail_score']
            for score in review.find_elements_by_xpath(
                './div/div[@class="review-rank"]/span[@class= "score"]/span'
            ):

                n, s = score.text.split("：")
                info[f"detail-{i} name"] = n
                info[f"detail-{i} score"] = s
                i += 1

            # info['free_trial']
            try:
                _tag = review.find_element_by_xpath(
                    './div/div[@class="richtitle"]'
                ).text
                info["free_trial"] = "1" if _tag == "免费体验后点评" else "-1"
            except exceptions.NoSuchElementException:
                info["free_trial"] = "0"

            # info['content']
            try:
                content = review.find_element_by_xpath(
                    './div/div[@class="review-words Hide"]'
                ).get_attribute("innerHTML")
                comments = content[: content.find('<div class="less-words">')].strip()
            except exceptions.NoSuchElementException:
                content = review.find_element_by_xpath(
                    './div/div[@class="review-words"]'
                ).get_attribute("innerHTML")
                comments = content
            res = r'<svgmtsi class="([a-z0-9]+)"></svgmtsi>'
            while True:
                try:
                    groups = re.search(res, comments).groups()
                    # print(groups)
                    comments = re.sub(res, f"|{groups[0]}|", comments, 1)
                except AttributeError:
                    break

            lst = comments.replace("||", "|").split("|")
            word = []
            for c in lst:
                if c in mapping:
                    word.append(mapping[c])
                else:
                    word.append(c)

            info["content"] = "".join(word)
            # //*[@id="review_689070127_action"]/span[1]
            info["time_stamp"] = str(
                review.find_element_by_xpath('.//span[@class= "time"]').text
            ).strip()
            result.append(info)

        return result

    def run(self):
        print(f"store {self.store_id} started")
        basic_url = f"http://www.dianping.com/shop/{self.store_id}/review_all"

        self.driver.get(basic_url)
        # time.sleep(60)
        result = []

        count = 1
        css_link = self.driver.find_element_by_xpath(
            "/html/head/link[4]"
        ).get_attribute("href")
        mapping = get_css(css_link)
        while True:
            result.extend(self.get_content_list(mapping))
            print(f"now page {count}")
            count += 1
            try:
                self.driver.find_element_by_xpath('//*[@title="下一页"]').click()
                time.sleep(10)
            except exceptions.NoSuchElementException:  # last page
                print("Already last page")
                break

        # self.save_content(content_list)
        print(f"store {self.store_id} done")

        with open("data/reviews.csv", "a") as csvfile:
            fieldnames = [
                "store_id",
                "city",
                "industry",
                "author_id",
                "total_score",
                "detail-1 name",
                "detail-1 score",
                "detail-2 name",
                "detail-2 score",
                "detail-3 name",
                "detail-3 score",
                "free_trial",
                "content",
                "time_stamp",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if os.stat("data/reviews.csv").st_size == 0:
                writer.writeheader()
            for record in result:
                writer.writerow(record)

        # time.sleep(5)
        self.driver.quit()


if __name__ == "__main__":
    stores = [
        128015796,
    ]

    for store in stores:
        start_time = time.time()
        StoreReviews(store, "shanghai", "美容/SPA").run()
        print("--- %s seconds ---" % (time.time() - start_time))
