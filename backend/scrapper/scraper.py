import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
import re

import logging 
logger = logging.getLogger(__name__)

class ScrapperException(Exception):
    pass

class BeautifulSoupScraper:

        def __init__(self, timeout= 30, max_retries = 3):
            self.timeout = timeout
            self.max_retries = max_retries
            self.session = requests.sessions.Session()
            self.session.headers.update({
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })

        def fetch_page (self, url:str) ->str:
            for attempt in range(self.max_retries):
                try:
                    logger.info(f"Fetching {url} (attempt {attempt + 1}/{self.max_retries})")
                    response = self.session.get(url , timeout = self.timeout)
                    response.raise_for_status()
                    return response.text
                except requests.RequestException as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt == self.max_retries - 1:
                        raise ScrapperException(f"Failed to fetch URL after {self.max_retries} attempts: {str(e)}")
                    time.sleep(2 ** attempt)  # Exponential backoff

        def parse_html(self, html: str) ->BeautifulSoup:
            return BeautifulSoup(html, 'lxml')
        
        def scrape(self, url: str):
            """Main Scrapping method"""
            try:
                html = self.fetch_page(url)
                soup = self.parse_html(html)

                data = {
                    'url':url,
                    'title':self.get_title(soup),
                    #'meta desciption': self.get_meta_desciption(soup),
                    'headings': self.get_headings(soup),
                    'links': self.get_links(soup, url),
                    'images': self.get_images(soup, url),
                    'text_content': self.get_text_content(soup),
                    'tables': self.extract_tables(soup),
                    'lists': self.extract_lists(soup),
                }
                return data
            except Exception as e:
                logger.error(f"BeautifulSoup scraping failed: {str(e)}")
                raise ScrapperException(f"Scraping failed: {str(e)}")
        def get_title(self, soup: BeautifulSoup) -> Optional[str]:
            """Extract page title"""
            title_tag = soup.find('title')
            return title_tag.get_text(strip=True) if title_tag else None

        def get_meta_description(self, soup: BeautifulSoup) -> Optional[str]:
            """Extract meta description"""
            meta = soup.find('meta', attrs={'name': 'description'})
            return meta.get('content', '').strip() if meta else None

        def get_headings(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
            """Extract all headings (h1-h6)"""
            headings = {}
            for i in range(1, 7):
                tag = f'h{i}'
                headings[tag] = [h.get_text(strip=True) for h in soup.find_all(tag)]
            return headings

        def get_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
            """Extract all links"""
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(base_url, href)
                links.append({
                    'text': link.get_text(strip=True),
                    'url': absolute_url,
                    'is_external': urlparse(absolute_url).netloc != urlparse(base_url).netloc
                })
            return links

        def get_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
            """Extract all images"""
            images = []
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if src:
                    images.append({
                        'src': urljoin(base_url, src),
                        'alt': img.get('alt', ''),
                        'title': img.get('title', '')
                    })
            return images

        def get_text_content(self, soup: BeautifulSoup) -> str:
            """Extract main text content"""
            # Remove script and style elements
            for script in soup(['script', 'style', 'nav', 'footer', 'header']):
                script.decompose()

            text = soup.get_text(separator=' ', strip=True)
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text)
            return text

        def extract_tables(self, soup: BeautifulSoup) -> List[List[List[str]]]:
            """Extract data from tables"""
            tables = []
            for table in soup.find_all('table'):
                table_data = []
                for row in table.find_all('tr'):
                    cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
                    if cells:
                        table_data.append(cells)
                if table_data:
                    tables.append(table_data)
            return tables

        def extract_lists(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
            """Extract lists (ul, ol)"""
            return {
                'unordered': [li.get_text(strip=True) for ul in soup.find_all('ul') for li in ul.find_all('li', recursive=False)],
                'ordered': [li.get_text(strip=True) for ol in soup.find_all('ol') for li in ol.find_all('li', recursive=False)]
            }

class SeleniumScraper:
    """Dynamic website scraper using Selenium"""
    
    def __init__(self, headless=True, timeout=30):
        self.headless = headless
        self.timeout = timeout
        self.driver = None
    
    def _setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.set_page_load_timeout(self.timeout)
    
    def scrape(self, url: str, wait_for_element: Optional[str] = None) -> Dict[str, Any]:
        """Main scraping method"""
        try:
            self._setup_driver()
            logger.info(f"Loading {url} with Selenium")
            
            self.driver.get(url)
            
            # Wait for specific element if provided
            if wait_for_element:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_element))
                )
            else:
                # Default wait for body
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'body'))
                )
            
            # Additional wait for JS to execute
            time.sleep(2)
            
            # Get page source and parse with BeautifulSoup
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            
            # Use BeautifulSoup scraper for extraction
            bs_scraper = BeautifulSoupScraper()
            data = {
                'url': url,
                'title': bs_scraper.get_title(soup),
                'meta_description': bs_scraper.get_meta_description(soup),
                'headings': bs_scraper.get_headings(soup),
                'links': bs_scraper.get_links(soup, url),
                'images': bs_scraper.get_images(soup, url),
                'text_content': bs_scraper.get_text_content(soup),
                'tables': bs_scraper.extract_tables(soup),
                'lists': bs_scraper.extract_lists(soup),
                'rendered_html': html[:5000]  # First 5000 chars
            }
            
            return data
            
        except Exception as e:
            logger.error(f"Selenium scraping failed: {str(e)}")
            raise ScrapperException(f"Selenium scraping failed: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()
    
    def scroll_to_bottom(self):
        """Scroll to bottom to load lazy content"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
            last_height = new_height


class AutoScraper:
    """Automatically choose the best scraper"""
    
    DYNAMIC_INDICATORS = [
        'react', 'vue', 'angular', 'spa', 'ajax',
        'next.js', 'nuxt', 'gatsby'
    ]
    
    @staticmethod
    def detect_scraper_type(url: str) -> str:
        """Detect if a site needs Selenium"""
        try:
            # Quick check with requests
            response = requests.get(url, timeout=10)
            html = response.text.lower()
            
            # Check for dynamic site indicators
            for indicator in AutoScraper.DYNAMIC_INDICATORS:
                if indicator in html:
                    logger.info(f"Detected dynamic content ({indicator}), using Selenium")
                    return 'selenium'
            
            # Check content size (dynamic sites often have minimal HTML)
            soup = BeautifulSoup(html, 'lxml')
            text_content = soup.get_text(strip=True)
            
            if len(text_content) < 500:
                logger.info("Low content detected, using Selenium")
                return 'selenium'
            
            logger.info("Static site detected, using BeautifulSoup")
            return 'beautifulsoup'
            
        except Exception as e:
            logger.warning(f"Auto-detection failed: {str(e)}, defaulting to BeautifulSoup")
            return 'beautifulsoup'
    
    @staticmethod
    def scrape(url: str, scraper_type: str = 'auto') -> Dict[str, Any]:
        """Scrape with auto-detection or specified scraper"""
        if scraper_type == 'auto':
            scraper_type = AutoScraper.detect_scraper_type(url)
        
        if scraper_type == 'selenium':
            scraper = SeleniumScraper()
        else:
            scraper = BeautifulSoupScraper()
        
        return scraper.scrape(url)