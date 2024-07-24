import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import traceback
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.chrome.service import Service

class WebScrapper:

    def __init__(self):
        self.ROOT_DIR = os.path.abspath(os.curdir)
        self.db_dir = os.path.join(self.ROOT_DIR, "chromedriver")
        self.visited_urls = set()
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--remote-debugging-port=9222")
        driver_path = None
        if os.name == 'posix':
            driver_path = os.path.join(self.db_dir, "chromedriver")
        else:
            driver_path = os.path.join(self.db_dir, "chromedriver.exe")

        self.s = Service(executable_path=driver_path)
        self.driver = webdriver.Chrome(service = self.s, options=self.chrome_options)

        self.extracted_text_data = ''
        self.max_depth = 3


    def get_links(self, page_url):
        try:
            self.driver.get(page_url)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            links = soup.find_all('a', href=True)
            return [urljoin(page_url, link['href']) for link in links]
        except Exception as e:
            print(e)
            return None


    def scrape_page(self, page_url):
        try:
            print(f"Scraping: {page_url}")
            self.driver.get(page_url)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            paragraphs = soup.find_all('p')
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'span', 'caption', 'li', 'ul', 'ol', 'pre', 'strong', 'b',
                                      'i', 'small', 'big'])
            # divs = soup.find_all('div')

            extracted_text = "\n".join(filter(lambda x: x.strip(), [p.get_text() for p in paragraphs] + [h.get_text() for h in headings] ))
            return extracted_text
        except Exception as e:
            print(e)
            return None

    def navigate(self, url, depth):
        try:
            if depth > self.max_depth or url in self.visited_urls:
                return
            self.visited_urls.add(url)

            links = self.get_links(url)
            if links:
                self.extracted_text_data = self.extracted_text_data +"\n"+ self.scrape_page(url)
                skip_files = ['js', 'css', 'pdf', 'csv',]
                for link in links:
                    file_ext = link.split(".")[-1]
                    if not link.startswith(url) or file_ext in skip_files:
                        continue
                    self.navigate(link, depth + 1)
        except Exception as e:
            print(e)
            return None


    def _run_scrape_page(self, url):
        try:
            self.navigate(url, 0)
            self.driver.quit()
            # print(self.extracted_text_data)
            return self.extracted_text_data
        except Exception as e:
            print(e)
            print(traceback.print_exc())
            self.driver.quit()
            return None
