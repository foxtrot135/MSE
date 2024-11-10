import requests
from bs4 import BeautifulSoup
import re

class FocusedCrawler:
    def __init__(self, max_pages=100):
        self.max_pages = max_pages
        self.urls_to_search = []
        self.urls_already_searched = set()
        self.files_found = []
        self.topic_words_weight_table = self.create_topic_words_weight_table()
        self.nb_training_set = set()
        self.seed_urls = self.get_seed_urls()

    def create_topic_words_weight_table(self):
        topic_words_weight_table = {}
        # Extract topic words weight from the provided table
        # You can manually enter the topic words and their weights
        # or load them from a file
        # For this demonstration, I'll manually add them
        topic_words_weight_table["Malware Lists and Collections"] = 0.9
        topic_words_weight_table["Downlaod"] = 0.7
        # Add other topic words with their weights
        return topic_words_weight_table

    def get_seed_urls(self):
        seed_urls = []
        response = requests.get("https://www.malwarebytes.com/malware")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Assuming the seed URLs are listed as links on the webpage
            for link in soup.find_all('a', href=True):
                seed_urls.append(link['href'])
        return seed_urls

    def fetch_page(self, url):
        # Fetch the page content
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None

    def parse_links(self, html):
        # Parse links from the HTML content
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        for link in soup.find_all('a', href=True):
            links.append(link['href'])
        return links

    def is_html_file(self, url):
        # Check if the file is an HTML file
        return url.endswith('.html') or url.endswith('.htm')

    def validate_url(self, url):
        # Validate the URL
        return re.match(r'^https?://', url)

    def crawl(self):
        self.urls_to_search = self.seed_urls.copy()
        while self.urls_to_search and len(self.files_found) < self.max_pages:
            url = self.urls_to_search.pop(0)
            self.urls_already_searched.add(url)
            if not self.validate_url(url):
                continue
            html = self.fetch_page(url)
            if not html:
                continue
            if not self.is_html_file(url):
                continue
            links = self.parse_links(html)
            for link in links:
                if self.validate_url(link):
                    if self.is_html_file(link):
                        if link not in self.urls_already_searched:
                            self.urls_to_search.append(link)
                    else:
                        self.files_found.append(link)
        return self.files_found

if __name__ == "__main__":
    crawler = FocusedCrawler()
    malware_links = crawler.crawl()
    print("Malware sample links found:")
    for link in malware_links:
        print(link)

