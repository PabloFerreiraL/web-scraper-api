import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin
import re

class WebScraper:
    def clean_text(self, text):
        return ' '.join(text.strip().split())

    def extract_content(self, soup, params=None):
        content = {}
        
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'iframe', 'img', 'aside', 'nav', 'footer', 'header', 'form', 'noscript'
        'ad', 'advertisement', 'sponsor', 'banner', 'ads', 'promo', 'promoted']):
            element.decompose()

        # Extract content
        if not params:
            content['text'] = self.clean_text(soup.get_text())
            return content

        for param in params:
            elements = soup.find_all(param)
            content[param] = [self.clean_text(el.get_text()) for el in elements if el and self.clean_text(el.get_text())] #only include if not empty

        return content

    def scrape(self, url, params=None):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            content = self.extract_content(soup, params)
            
            return {
                'url': url,
                'content': content,
                'status': 'success'
            }
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error scraping {url}: {str(e)}")
            return {
                'url': url,
                'error': str(e),
                'status': 'error'
            }