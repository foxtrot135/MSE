from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse
from pymongo import MongoClient
import json
import os
import requests

class Crawler:
    def __init__(self, seeds=[]):
        self.seen = set()
        self.seeds = seeds
        self.allowed_extensions = {'.zip'}  # Specify the file extensions you want to search for
        self.delay = 1  # Example delay (seconds) for rate limiting

        # Replace with your actual MongoDB connection string
        self.client = MongoClient('mongodb+srv://foxtrot1305:Ankit%4012345@backtesting.krt8rkf.mongodb.net/')  # Replace with actual credentials
        self.db = self.client['FYP']
        self.collection_files = self.db['Adam_TheZoo_crawler']
        self.collection_crawled_links = self.db['Adam_crawled_links']  # New collection for all crawled links
        self.collection_zip_urls = self.db['Adam_zip_urls']  # New collection for URLs with .zip files

    def crawl(self, max_depth):
        for seed in self.seeds:
            self.dfs(seed, 0, max_depth)

    def dfs(self, url, depth, max_depth):
        if depth > max_depth:
            time.sleep(self.delay)
            return

        if url in self.seen:
            return

        self.seen.add(url)

        try:
            response = requests.get(url)

            if response.status_code == 200:
                print(f"Processing: {url}, Depth: {depth}")

                self.collection_crawled_links.insert_one({'url': url})

                soup = BeautifulSoup(response.content, 'html.parser')

                for link in soup.find_all('a', href=True):
                    new_link = urljoin(url, link['href'])
                    if '#' in new_link:
                        new_link = new_link.split('#', 1)[0]  # Remove fragment

                    # Ensure links belong to the target repository and exclude ".." directories
                    if not new_link.startswith('https://github.com/foxtrot135/theZoo') or "/.." in new_link:
                        continue  # Skip external links and ".." directories

                    # Print for debugging purposes
                    print(f"Following link: {new_link}")  # Track link following

                    # Recursive call outside conditional block for guaranteed execution
                    self.dfs(new_link, depth + 1, max_depth)

                    # Optional: Implement processing for files with allowed extensions
                    # ... (Replace with your custom logic for downloading or processing files)

                    # Check if the link is a .zip file and store its URL in the collection
                    if self.is_allowed_extension(new_link):
                        self.collection_zip_urls.insert_one({'zip_url': new_link})

        except requests.exceptions.RequestException as e:
            print(f"An error occurred for {url}: {e}")

    def is_allowed_extension(self, href):
        parsed_url = urlparse(href)
        _, file_extension = os.path.splitext(parsed_url.path)
        return file_extension.lower() in self.allowed_extensions


# Example usage for a specific URL
# last_path = "https://github.com/ytisf/theZoo/tree/master"  # Example last path to crawl
crawler = Crawler(['https://github.com/foxtrot135/theZoo'])
crawler.crawl(max_depth=1000000)  # Adjust max_depth as needed
