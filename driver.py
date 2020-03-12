from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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
        options.add_experimental_option('excludeSwitches',
                                        ['enable-automation'])  # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium

        # options.add_argument('--proxy-server=http://127.0.0.1:8080')
        self.driver = webdriver.Chrome(DRIVER_PATH, options=options)
