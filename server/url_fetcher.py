import re
import requests
from typing import List, Dict, Optional
from urllib.parse import urlparse, urljoin
import time


class URLFetcher:
    """Handles fetching content from URLs found in input files"""
    
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        # Set a user agent to avoid blocking
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (MCP Test Plan Generator) AppleWebKit/537.36'
        })
    
    def extract_urls_from_text(self, text: str) -> List[str]:
        """Extract all URLs from text content"""
        # More robust URL pattern that handles complex URLs with hyphens
        url_pattern = r'https?://[^\s<>"{\}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text, re.IGNORECASE)
        
        # Clean and validate URLs
        valid_urls = []
        for url in urls:
            try:
                parsed = urlparse(url)
                if parsed.scheme and parsed.netloc:
                    valid_urls.append(url)
            except:
                continue
        
        return list(set(valid_urls))  # Remove duplicates
    
    def is_fetchable_url(self, url: str) -> bool:
        """Check if URL is likely to contain useful text content"""
        parsed = urlparse(url)
        
        # Skip certain file types that won't have useful text
        skip_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.mp4', '.mp3', '.zip', '.exe']
        if any(parsed.path.lower().endswith(ext) for ext in skip_extensions):
            return False
        
        # Allow common documentation and API sites
        useful_domains = [
            'github.com', 'docs.', 'api.', 'developer.', 'swagger.', 'postman.com',
            'confluence.', 'notion.', 'gitbook.', 'readthedocs.', 'wiki.'
        ]
        
        domain = parsed.netloc.lower()
        if any(useful in domain for useful in useful_domains):
            return True
        
        # Allow if path suggests documentation
        useful_paths = ['/docs/', '/api/', '/documentation/', '/wiki/', '/help/', '/guide/']
        if any(path in parsed.path.lower() for path in useful_paths):
            return True
        
        return True  # Allow by default, let content filtering handle it
    
    def fetch_url_content(self, url: str) -> Optional[Dict[str, str]]:
        """Fetch and clean content from a URL"""
        if not self.is_fetchable_url(url):
            return None
        
        for attempt in range(self.max_retries):
            try:
                print(f"🌐 Fetching content from: {url}")
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                # Check content type
                content_type = response.headers.get('content-type', '').lower()
                if 'text/html' in content_type or 'text/plain' in content_type:
                    content = self.extract_text_from_html(response.text)
                elif 'application/json' in content_type:
                    content = response.text
                else:
                    # Try to extract text anyway
                    content = self.extract_text_from_html(response.text)
                
                if content and len(content.strip()) > 100:  # Only keep substantial content
                    return {
                        'url': url,
                        'content': content.strip(),
                        'content_type': content_type,
                        'title': self.extract_title_from_html(response.text)
                    }
                
            except requests.exceptions.RequestException as e:
                print(f"⚠️  Error fetching {url} (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(1)  # Wait before retry
                continue
            except Exception as e:
                print(f"⚠️  Unexpected error fetching {url}: {e}")
                break
        
        return None
    
    def extract_text_from_html(self, html: str) -> str:
        """Extract readable text from HTML content"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text and clean it up
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        except ImportError:
            # Fallback: simple HTML tag removal
            import re
            text = re.sub(r'<[^>]+>', '', html)
            text = re.sub(r'\s+', ' ', text)
            return text.strip()
        except Exception:
            # Last resort: return HTML as-is
            return html
    
    def extract_title_from_html(self, html: str) -> str:
        """Extract title from HTML content"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            title_tag = soup.find('title')
            if title_tag:
                return title_tag.get_text().strip()
        except:
            pass
        
        # Fallback: regex
        import re
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        if title_match:
            return title_match.group(1).strip()
        
        return "Untitled"
    
    def process_urls_from_text(self, text: str, max_urls: int = 5) -> List[Dict[str, str]]:
        """Extract URLs from text and fetch their content"""
        urls = self.extract_urls_from_text(text)
        
        if not urls:
            return []
        
        print(f"🔗 Found {len(urls)} URL(s) in content")
        
        fetched_content = []
        for i, url in enumerate(urls[:max_urls]):  # Limit to avoid too many requests
            content = self.fetch_url_content(url)
            if content:
                fetched_content.append(content)
                print(f"✅ Successfully fetched content from: {url}")
            else:
                print(f"❌ Could not fetch content from: {url}")
        
        if len(urls) > max_urls:
            print(f"ℹ️  Limited to first {max_urls} URLs. Found {len(urls)} total.")
        
        return fetched_content 