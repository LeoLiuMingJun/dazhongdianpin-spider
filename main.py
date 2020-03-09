import time

from reviews import StoreReviews

DRIVER_PATH = '/Users/mingjunliu/Library/chromedriver'

if __name__ == '__main__':
    stores = [128015796, ]

    for store in stores:
        StoreReviews(store, '上海', '美容/SPA').run()
        time.sleep(10)
