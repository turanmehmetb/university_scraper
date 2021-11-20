from bs4 import BeautifulSoup
import requests
import re
import json
from os.path import isdir, join
from requests import get
import argparse

parser = argparse.ArgumentParser(description='University Scraper')

parser.add_argument('-u', help='Scrape universities', action="store_true", default=False)
parser.add_argument('-d', help='Scrape departments', action="store_true", default=False)
parser.add_argument('-w', help='Scrape universities with departments', action="store_true", default=False)

parser.add_argument('--dir', dest='dir', type=str, help='Output directory for the file(s)')
args = parser.parse_args()

#transforms keys into camel casesys
def to_camel(word):
    res = ''.join(x.capitalize() or '-' for x in word.split('-'))
    return res[0].lower() + res[1:]

#scrapes universities, takes two arguments as boolean and string, returns location of file as string
#withDeps if true: scrapes universities with departments else without departments
#dir directory for the downloaded file
def scrapeUniversities(withDeps, dir):
    try:
        x = get("https://www.hangiuniversite.com/universiteler").text
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    soup = BeautifulSoup(x, "html.parser")
    unis = soup.find_all('div', attrs={'class': 'university-grid-item special-not'})
    bannedWords = ["Ucretsiz", "Ucretli", "TamBurslu", "Yuzde75Burslu", "Yuzde50Burslu"]
    uni_items = []
    fileName = ""

    if withDeps:
        print("This may take some time..")
        fileName = "universitiesWithDepartments.txt"
        for uni in unis:
            uni_item = {}
            deps = []
            item = uni.find('p').find('a')
            uni_item['name'] = item.text                                #scrape university name from its title and key from its href
            uni_item['key'] = to_camel(item['href'].split("com/")[1])

            try:
                x = get(item['href']).text
            except requests.exceptions.RequestException as e:
                raise SystemExit(e)

            soup = BeautifulSoup(x, "html.parser")
            table = soup.find('div', attrs={'id': 'lisans'})
            if table is not None: deps = table.find_all('a')            #scrape universities departments if any

            uni_item['deps'] = []

            for dp in deps:
                dep_item = {}
                dep_name = dp.text.split("»")[1]
                if '(' in dep_name:
                    dep_name = dep_name.split("(")[0].strip(" ")
                if len(list(filter(lambda dep: dep_name in dep['name'], uni_item['deps']))) == 0:
                    dep_item['name'] = dep_name

                    newKey = to_camel(dp['href'].split("com/")[1].split('/')[0]).replace(uni_item['key'], '')
                    for word in bannedWords:                            #remove unnecessary words from key
                        newKey = newKey.replace(word, "")

                    dep_item['key'] = newKey[0].lower() + newKey[1:]
                    uni_item['deps'].append(dep_item)

            uni_items.append(uni_item)

    else:
        fileName = "universities.txt"
        uni_items = {}
        for uni in unis:
            item = uni.find('p').find('a')
            key = to_camel(item['href'].split("com/")[1])
            uni_items[key] = item.text

    uni_items = json.dumps(uni_items, ensure_ascii=False)               #dump universities as json into a txt file, including Turkish letters
    jsonUni = json.loads(uni_items)
    json.dump(jsonUni, open(join(dir, fileName), 'w', encoding='utf-8'), indent=4, ensure_ascii=False)

    return join(dir, fileName)

#scrapes departments, takes one arguments as string, returns location of file as string
#dir directory for the downloaded file
def scrapeDeps(dir):
    try:
        x = get("https://www.hangiuniversite.com/bolumler").text
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    soup = BeautifulSoup(x, "html.parser")

    contents = soup.find('table', attrs={'class': 'table table-hover table-striped listing'})
    deps = contents.find_all('a')
    dep_items = {}
    name_list = []
    for dep in deps:
        dep_name = dep.text.split("»")[1].strip(" ")
        if '(' in dep_name:
            dep_name = dep_name.split("(")[0].strip(" ")
        dep_name = dep_name.title().strip(" ")

        if dep_name not in name_list:
            key = dep['href'].split("com/")[1].split('/')[1]
            dep_items[to_camel(key)] = dep_name
            name_list.append(dep_name)

    dep_items = json.dumps(dep_items, ensure_ascii=False)
    jsonDep = json.loads(dep_items)
    json.dump(jsonDep, open(join(dir, "departments.txt"), 'w', encoding='utf-8',), indent=4, ensure_ascii=False)

    return join(dir, "departments.txt")

def main():
    dir = ""
    dirs = []
    if args.dir:
        if isdir(args.dir) is False:
            raise ValueError("Provided directory is not valid!")
        else:
            dir = args.dir

    if all([args.u, args.d, args.w]) is True or any([args.u, args.d, args.w]) is False:
        resultDir = scrapeDeps(dir)
        dirs.append(resultDir)

        resultDir = scrapeUniversities(False, dir)
        dirs.append(resultDir)

        resultDir = scrapeUniversities(True, dir)
        dirs.append(resultDir)

    else:
        if args.u:
            resultDir = scrapeUniversities(False, dir)
            dirs.append(resultDir)
        if args.d:
            resultDir = scrapeDeps(dir)
            dirs.append(resultDir)
        if args.w:
            resultDir = scrapeUniversities(True, dir)
            dirs.append(resultDir)

    print("Scraped successfully!")
    print("File Location(s): ")
    for d in dirs:
        print(d)

if __name__ == '__main__':
    main()


