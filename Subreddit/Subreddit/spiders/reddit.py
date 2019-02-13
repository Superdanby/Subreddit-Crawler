from selenium import webdriver

import unittest, time, re, scrapy, json, csv


class RedditSpider(scrapy.Spider):
    name = "reddit"
    authors = []
    media = []
    unixtime = []
    ups = []
    downs = []
    url_cnt = 0

    def start_requests(self):
        assert(self.subreddit is not None and self.unix_time is not None)
        subreddit = str(self.subreddit)
        timestamp = float(self.unix_time)
        driver = webdriver.Chrome()
        driver.implicitly_wait(30)
        base_url = "https://www.reddit.com/r/" + subreddit + "/"
        driver.get(base_url)
        jsondriver = webdriver.Chrome()
        jsondriver.implicitly_wait(30)
        while True:
            jsondriver.get(driver.find_elements_by_xpath("//*[@data-click-id='body']")[-1].get_attribute('href') + '.json')
            pre = jsondriver.find_element_by_tag_name("pre").text
            data = json.loads(pre)
            if data[0]["data"]["children"][0]["data"]["created"] < timestamp:
                break
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
        urls = driver.find_elements_by_xpath("//*[@data-click-id='body']")
        self.url_cnt = len(urls)
        for url in urls:
            yield scrapy.Request(url=url.get_attribute('href') + '.json', callback=self.parse)

    def parse(self, response):
        data = json.loads(response.body_as_unicode())
        self.authors.append(data[0]["data"]["children"][0]["data"]["author"])
        self.media.append(data[0]["data"]["children"][0]["data"]["url"])
        self.unixtime.append(int(data[0]["data"]["children"][0]["data"]["created"]))
        self.ups.append(data[0]["data"]["children"][0]["data"]["ups"])
        self.downs.append(data[0]["data"]["children"][0]["data"]["downs"])
        self.log('Fetched: ' + self.authors[-1] + ' ' + self.media[-1])

    def closed(self, reason):
        with open(self.name + '.csv', 'w', newline='') as f:
            csvwriter = csv.writer(f, delimiter=',', lineterminator='\n')
            csvwriter.writerow(('Author', 'Unix_timestamp', 'Ups', 'Downs', 'Link'))
            for row in zip(self.authors, self.unixtime, self.ups, self.downs, self.media):
                csvwriter.writerow(row)
        print(f'Expected: {self.url_cnt}, got: {len(self.authors)}\n')
