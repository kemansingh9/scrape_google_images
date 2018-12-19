import os
import time
import urllib.request
import random
import json
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from progress_bar import printProgressBar as ppb

#Adding Suitable Options to our Headless Browser
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument("--window-position=0,0")
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument("--log-level=3")

#Command Line Interface
argument_parser = argparse.ArgumentParser(description='Download images using google image search')
argument_parser.add_argument('query', metavar='query', type=str, help='Search Term for Images')
argument_parser.add_argument('--number', metavar='number', default=25, type=int, help='Number of images you want to scrape')
argument_parser.add_argument('--save_dir', metavar='save_dir', type=str, help="Directory for storing the images", required=True)

def make_dir(query, save_dir):
    download_path = f"{save_dir}/{query.replace(' ', '_')}"
    if not os.path.exists(download_path):
        os.makedirs(download_path)

def capture_images(search_term, number):
    driver = webdriver.Chrome(executable_path = "chromedriver", chrome_options = chrome_options)
    search_url = f"https://www.google.com/search?q={search_term}&tbm=isch"
    driver.get(search_url)
    show_all_results(driver)
    images = driver.find_elements_by_xpath('//div[contains(@class,"rg_meta")]')
    img_urls = {}
    for img in images[0:number]:
        img_url = json.loads(img.get_attribute('innerHTML'))["ou"]
        img_type = json.loads(img.get_attribute('innerHTML'))["ity"]
        img_urls[img_url] = img_type
    driver.quit()
    return img_urls


def save_images(image_links, query):
    count = 0
    l = len(image_links)
    ppb(0, l, prefix='Progress:', suffix='Complete', length=50)
    for i, (url, type) in enumerate(image_links.items()):
        if not type:
            type = 'jpg'
        try:
            filename = f"{query.strip()}_{count}.{type}"
            urllib.request.urlretrieve(url, f"images/{query.replace(' ', '_')}/{filename}")
        except:
            pass
        ppb(i + 1, l, prefix='Progress:', suffix='Complete', length=50)
        count+=1

def show_all_results(driver):
    for i in range(10):
        driver.execute_script("window.scrollBy(0, 1000000)")
        time.sleep(2)

def show_more_results(driver):
    show_all_results(driver)
    time.sleep(2)
    try:
        driver.find_element_by_xpath("//input[@value='Show more results']").click()
    except Exception as e:
        print ("The search results have lower number of images")

def main():
    args = argument_parser.parse_args()
    if args.number > 400:
        args.number = 400
    make_dir(args.query, args.save_dir)
    search_term = args.query.replace(" ", "+")
    img_url_dict = capture_images(search_term, args.number)
    save_images(img_url_dict, args.query)

if __name__ == "__main__":
    main()
