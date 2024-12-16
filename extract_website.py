import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse
import time
from typing import Dict, List, Set

class WebsiteDataExtractor:
    def __init__(self, max_depth: int = 2, max_pages: int = 10, delay: float = 1.0):
        """
        Initialize the web scraping extractor
        
        Args:
            max_depth (int): Maximum depth of link traversal
            max_pages (int): Maximum number of pages to scrape
            delay (float): Delay between requests to avoid overwhelming servers
        """
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.delay = delay
        self.visited_urls: Set[str] = set()
        self.extracted_data: Dict[str, Dict] = {}
    
    def is_valid_url(self, url: str, base_domain: str) -> bool:
        """
        Check if the URL is valid and within the same domain
        
        Args:
            url (str): URL to validate
            base_domain (str): Base domain to compare against
        
        Returns:
            bool: Whether the URL is valid and within the same domain
        """
        try:
            parsed_url = urlparse(url)
            return (
                parsed_url.scheme in ['http', 'https'] and
                parsed_url.netloc == base_domain and
                url not in self.visited_urls
            )
        except Exception:
            return False
    
    def extract_page_data(self, url: str) -> Dict:
        """
        Extract data from a single webpage
        
        Args:
            url (str): URL of the webpage to scrape
        
        Returns:
            dict: Extracted webpage data
        """
        try:
            # Send a GET request to the website
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract metadata
            metadata = {}
            meta_tags = soup.find_all('meta')
            for tag in meta_tags:
                name = tag.get('name', tag.get('property', 'unnamed'))
                content = tag.get('content', '')
                if name and content:
                    metadata[name] = content
            
            # Extract title
            metadata['title'] = soup.title.string if soup.title else 'No Title'
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text content
            text_content = {
                'paragraphs': [p.get_text(strip=True) for p in soup.find_all('p') if p.get_text(strip=True)],
                'headings': {
                    'h1': [h.get_text(strip=True) for h in soup.find_all('h1')],
                    'h2': [h.get_text(strip=True) for h in soup.find_all('h2')],
                    'h3': [h.get_text(strip=True) for h in soup.find_all('h3')]
                }
            }
            
            # Extract links
            links = [
                urljoin(url, link.get('href', ''))
                for link in soup.find_all('a')
                if link.get('href')
            ]
            
            # Extract images
            images = [
                {
                    'src': urljoin(url, img.get('src', '')),
                    'alt': img.get('alt', '')
                } 
                for img in soup.find_all('img')
            ]
            
            return {
                'url': url,
                'metadata': metadata,
                'text_content': text_content,
                'links': links,
                'images': images
            }
        
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def recursive_crawl(self, start_url: str, current_depth: int = 0) -> None:
        """
        Recursively crawl and extract data from links
        
        Args:
            start_url (str): Starting URL to crawl
            current_depth (int): Current depth of crawling
        """
        # Check depth and page limits
        if (current_depth > self.max_depth or 
            len(self.visited_urls) >= self.max_pages):
            return
        
        # Parse base domain
        base_domain = urlparse(start_url).netloc
        
        # Skip if already visited
        if start_url in self.visited_urls:
            return
        
        # Mark as visited
        self.visited_urls.add(start_url)
        
        # Extract page data
        page_data = self.extract_page_data(start_url)
        if not page_data:
            return
        
        # Store extracted data
        self.extracted_data[start_url] = page_data
        
        # Recursive link extraction
        for link in page_data['links']:
            # Validate and explore links
            if (self.is_valid_url(link, base_domain) and 
                link not in self.visited_urls):
                # Add delay to be respectful of server resources
                time.sleep(self.delay)
                
                # Recursively crawl
                self.recursive_crawl(link, current_depth + 1)
    
    def extract_website_data(self, start_url: str) -> Dict:
        """
        Main method to start website data extraction
        
        Args:
            start_url (str): URL to start crawling from
        
        Returns:
            dict: Comprehensive extracted website data
        """
        # Reset data before starting
        self.visited_urls.clear()
        self.extracted_data.clear()
        
        # Start recursive crawling
        self.recursive_crawl(start_url)
        
        return {
            'total_pages_scraped': len(self.extracted_data),
            'extracted_data': self.extracted_data
        }

def main(url):
    # Example usage
    extractor = WebsiteDataExtractor(
        max_depth=2,  # How deep to go into links
        max_pages=10,  # Maximum number of pages to scrape
        delay=1.0     # Delay between requests
    )
    
    try:
        # Extract website data
        website_data = extractor.extract_website_data(url)
        
        # Pretty print the extracted data
        with open('website.json', 'w') as file:
            json.dump(website_data, file, indent=2)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main("https://www.stanford.edu/")