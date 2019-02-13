from selenium import webdriver
from copy import deepcopy

import argparse, csv

parser = argparse.ArgumentParser()
parser.add_argument('--csvfile', nargs=1)
csvfile = parser.parse_args().csvfile[0]

imgur_fingerprint = "https://imgur.com/gallery/"

if csvfile is not None:
    with open(csvfile, 'r') as f:
        csvreader = csv.reader(f)
        headers = next(csvreader, None)
        origin_csv = [[str(row[0]), int(row[1]), int(row[2]), int(row[3]), str(row[4])] for row in csvreader]
        driver = webdriver.Chrome()
        driver.implicitly_wait(30)
        addition_csv = []
        for entry in origin_csv:
            if imgur_fingerprint in entry[-1]:
                driver.get(entry[-1])
                urls = driver.find_elements_by_xpath("//*[@class='image post-image']/a")
                for url in urls:
                    addition_csv.append(deepcopy(entry))
                    print(addition_csv)
                    print(url.get_attribute('href'))
                    addition_csv[-1][-1] = url.get_attribute('href')
                    print(addition_csv)
        driver.quit()
        final_csv = [row for row in origin_csv if imgur_fingerprint not in row[-1]]
        final_csv = final_csv + addition_csv
    final_csv = sorted(final_csv, key=lambda row: row[1])
    for row in final_csv:
        print(row)
    with open('imgur.csv', 'w', newline='') as f:
        csvwriter = csv.writer(f, delimiter=',', lineterminator='\n')
        csvwriter.writerow(headers)
        for row in final_csv:
            csvwriter.writerow(row)
