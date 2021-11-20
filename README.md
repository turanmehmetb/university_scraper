# university_scraper

### About

Scrapes Turkish universities and their departments from https://www.hangiuniversite.com/. Saves data as json type into txt files.

### Prerequisites

Python3 and BeautifulSoup

  ```sh
  pip install beautifulsoup4
  ```
  
### Usage
  ```sh
python university_scraper.py 
  ```
or
  ```sh
py university_scraper.py
  ```
university_scraper.py file takes 2 optional arguments as scrape types and download directory.

* -d Scrape universities
* -u Scrape departments
* -w Scrape universities with departments

* --dir C:\users\user\Desktop

As default, py file will scrape all types and saves in current directory

### Examples

  ```sh
  python university_scraper.py -d

  python university_scraper.py -dw --dir C:\users\user\Desktop

  python university_scraper.py -dwu

  python university_scraper.py
  
 ```
