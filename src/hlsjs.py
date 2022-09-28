#!/usr/bin/python3.8

import time
import argparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.headless = True
chrome_options.add_argument('--no-sandbox')

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-url", type=str, required = True, help ='Player URL')
arg_parser.add_argument("-ua", type=str, nargs='?', help = 'User Agent')
arg_parser.add_argument("-tput", type=int, nargs='?', help = 'Throughput in KiloBYTES per second')
args = arg_parser.parse_args()

if args.ua is not None:
    chrome_arg_ua = "--user-agent={}".format(args.ua)
    chrome_options.add_argument(chrome_arg_ua)

driver = webdriver.Chrome(options=chrome_options)

if args.tput is not None:
    driver.set_network_conditions(
        offline=False,
        latency=5,
        throughput = args.tput * 1024
    )

while True:
    driver.get(args.url)
    driver.execute_script('document.getElementsByTagName("video")[0].play()')
    time.sleep(300)

driver.quit()


