import requests
from bs4 import BeautifulSoup
from queue import PriorityQueue
from urllib.parse import urlparse, urljoin
import os
import time

class WebCrawler:
    def __init__(self, seed_urls, max_pages=1000, max_depth=5, timeout=10):
        self.seed_urls = seed_urls
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.timeout = timeout
        self.visited_urls = set()
        self.queue = PriorityQueue()
        self.depth_map = {}

    def crawl(self):
        for url in self.seed_urls:
            self.queue.put((0, url))
            self.depth_map[url] = 0  # Set initial depth for seed URLs

        while not self.queue.empty() and len(self.visited_urls) < self.max_pages:
            priority, url = self.queue.get()

            if url not in self.visited_urls:
                depth = self.depth_map.get(url, 0)  # Get depth from depth_map or default to 0
                self.visited_urls.add(url)
                print(f"Crawling {url} at depth {depth}...")

                try:
                    response = requests.get(url, timeout=self.timeout)
                    if response.status_code == 200:
                        self.parse_page(url, response.text, depth)
                except Exception as e:
                    print(f"Error crawling {url}: {e}")

        print("Crawling finished.")

    def parse_page(self, url, html_content, depth):
        soup = BeautifulSoup(html_content, 'html.parser')
        self.depth_map[url] = depth

        # Extract anchor tags and new URLs
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(url, href)
            parsed_url = urlparse(absolute_url)

            # Filter out non-HTTP(S) URLs and URLs not within the same domain
            if parsed_url.scheme.startswith('http') and parsed_url.netloc == urlparse(url).netloc:
                self.queue.put((self.calculate_priority(absolute_url), absolute_url))
                if absolute_url not in self.depth_map:  # Ensure the URL is not already in the depth map
                    self.depth_map[absolute_url] = depth + 1  # Add the new URL to the depth map

        # Save HTML content to a file
        self.save_to_file(url, html_content)

    def calculate_priority(self, url):
        # Placeholder for scoring function (e.g., keyword matching, cosine similarity)
        # Here, we simply return a priority based on URL length
        return -len(url)

    def save_to_file(self, url, html_content):
        # Create a directory to store crawled pages if it doesn't exist
        if not os.path.exists('crawled_pages'):
            os.makedirs('crawled_pages')

        # Generate a filename based on the URL
        # Remove characters not valid for filenames using regular expressions
        filename = url.replace('/', '_').replace(':', '_')

        # Save HTML content to a file
        with open(f'crawled_pages/{filename}.html', 'w', encoding='utf-8') as file:
            file.write(html_content)

    def print_url_tree(self):
        for url, depth in self.depth_map.items():
            print(f"{' ' * (depth * 2)}Depth {depth}: {url}")

if __name__ == "__main__":
    seed_urls = ['https://github.com/topics/malware-samples',
                 'https://zeltser.com/malware-sample-sources/',
                 'https://cyberlab.pacific.edu/resources/malware-samples-for-students',
                 'https://www.cosive.com/capabilities/malware-zoo',
                 'https://github.com/Da2dalus/The-MALWARE-Repo',
                 'https://malshare.com/',
                 'https://github.com/jstrosch/malware-samples',
                 'https://github.com/hslatman/awesome-threat-intelligence',
                 'https://maldatabase.com/',
                 'https://malpedia.caad.fkie.fraunhofer.de/',
                 'https://maltiverse.com/start',
                 'https://www.malwarepatrol.net/',
                 'https://malware-traffic-analysis.net/',
                 'https://riskanalytics.com/community/',
                 'https://github.com/topics/malware-dataset',
                 'https://whyisyoung.github.io/BODMAS/',
                 'https://github.com/gfek/Real-CyberSecurity-Datasets',
                 'https://virusshare.com/hashes',
                 'https://www.virustotal.com/gui/home/upload',
                 'https://otx.alienvault.com/indicator/file/c0202cf6aeab8437c638533d14563d35',
                 'https://github.com/eminunal1453/Various-Malware-Hashes',
                 'https://fordham.libguides.com/Cybersecurity/Databases',
                 'https://www.cyberdb.co/database/']
    crawler = WebCrawler(seed_urls)
    start_time = time.time()
    crawler.crawl()
    crawler.print_url_tree()  # Print URL tree after crawling
    end_time = time.time()
    print(f"Crawling finished in {end_time - start_time:.2f} seconds.")
