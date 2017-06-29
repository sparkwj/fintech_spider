#!/usr/bin/env python3
# coding: utf-8
# File: selenium_display.py
# Author: lxw
# Date: 6/22/17 9:11 AM

import multiprocessing
from pyvirtualdisplay import Display
import random
from selenium import webdriver

def get_driver_chrome():
    # chromedriver
    options = webdriver.ChromeOptions()

    # display = Display(visible=1, size=(800, 800))
    display = Display(visible=0, size=(800, 800))
    display.start()
    driver = webdriver.Chrome(executable_path=r"/home/lxw/Software/chromedriver_selenium/chromedriver",
                              chrome_options=options)

    # 设置超时时间
    driver.set_page_load_timeout(60)
    driver.set_script_timeout(60)  # 这两种设置都进行才有效
    return display, driver


def test_proxy(num):
    display, driver = get_driver_chrome()
    driver.implicitly_wait(30)
    driver.get("http://xiaoweiliu.cn")
    driver.find_element_by_xpath("/html")
    driver.quit()
    display.stop()
    print(num)

if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=10)
    for i in range(10):
        pool.apply_async(test_proxy, (i,))

    pool.close()
    pool.join()
