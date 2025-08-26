import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
from collections import defaultdict
import logging

class LinkExtractor:
    """Class to extract and categorize links from web pages"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def extract_links(self, url):
        """Extract only download links from a given URL"""
        try:
            # Validate and normalize URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Fetch the webpage
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract all links
            all_links = self._extract_all_links(soup, url)
            
            # Filter only download links
            download_links = self._filter_download_links(all_links)
            
            # Create categories with only download links
            categories = {'Download Links': download_links} if download_links else {}
            
            return {
                'error': None,
                'links': download_links,
                'categories': categories,
                'total_count': len(download_links)
            }
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error: {str(e)}")
            return {
                'error': f'Failed to fetch webpage: {str(e)}',
                'links': [],
                'categories': {},
                'total_count': 0
            }
        except Exception as e:
            logging.error(f"Parsing error: {str(e)}")
            return {
                'error': f'Failed to parse webpage: {str(e)}',
                'links': [],
                'categories': {},
                'total_count': 0
            }
    
    def _extract_all_links(self, soup, base_url):
        """Extract all links from the parsed HTML"""
        links = []
        
        # Find all anchor tags with href attributes
        for tag in soup.find_all('a', href=True):
            href = tag['href'].strip()
            if not href or href.startswith('#'):
                continue
            
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, href)
            
            # Get link text
            link_text = tag.get_text(strip=True) or tag.get('title', '') or href
            
            # Get additional attributes
            link_info = {
                'url': absolute_url,
                'original_href': href,
                'text': link_text,
                'title': tag.get('title', ''),
                'target': tag.get('target', ''),
                'rel': tag.get('rel', []),
                'class': tag.get('class', [])
            }
            
            links.append(link_info)
        
        # Also check for links in other elements (like buttons with onclick)
        for tag in soup.find_all(['button', 'div', 'span'], onclick=True):
            onclick = tag.get('onclick', '')
            url_match = re.search(r'(?:window\.open|location\.href|window\.location)\s*=\s*["\']([^"\']+)["\']', onclick)
            if url_match:
                href = url_match.group(1)
                absolute_url = urljoin(base_url, href)
                link_text = tag.get_text(strip=True) or 'JavaScript Link'
                
                link_info = {
                    'url': absolute_url,
                    'original_href': href,
                    'text': link_text,
                    'title': tag.get('title', ''),
                    'target': '_blank',
                    'rel': [],
                    'class': tag.get('class', []),
                    'type': 'javascript'
                }
                
                links.append(link_info)
        
        # Check for image links that might be download buttons
        for img in soup.find_all('img'):
            parent_link = img.find_parent('a')
            if parent_link and parent_link.get('href'):
                href = parent_link['href']
                if not any(link['url'] == urljoin(base_url, href) for link in links):
                    absolute_url = urljoin(base_url, href)
                    img_alt = img.get('alt', '')
                    img_src = img.get('src', '')
                    link_text = img_alt or parent_link.get_text(strip=True) or 'Image Link'
                    
                    # Check if this looks like a download button
                    if any(keyword in img_alt.lower() for keyword in ['download', 'get', 'hubcloud', 'gdflix', 'drive', 'cloud']) or \
                       any(keyword in img_src.lower() for keyword in ['download', 'hubcloud', 'gdflix', 'drive', 'cloud']) or \
                       any(keyword in link_text.lower() for keyword in ['download', 'hubcloud', 'gdflix', 'drive', 'cloud']):
                        
                        link_info = {
                            'url': absolute_url,
                            'original_href': href,
                            'text': link_text,
                            'title': parent_link.get('title', ''),
                            'target': parent_link.get('target', ''),
                            'rel': parent_link.get('rel', []),
                            'class': parent_link.get('class', []),
                            'type': 'image_link'
                        }
                        
                        links.append(link_info)
        
        return links
    
    def _categorize_links(self, links):
        """Categorize links based on their characteristics"""
        categories = defaultdict(list)
        
        for link in links:
            url = link['url'].lower()
            text = link['text'].lower()
            original_href = link['original_href'].lower()
            
            # Parse URL for analysis
            parsed = urlparse(link['url'])
            domain = parsed.netloc.lower()
            path = parsed.path.lower()
            
            # Download links
            download_extensions = ['.zip', '.rar', '.7z', '.tar', '.gz', '.exe', '.msi', '.dmg', '.pkg', 
                                 '.deb', '.rpm', '.apk', '.ipa', '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
                                 '.ppt', '.pptx', '.mp4', '.mkv', '.avi', '.mov', '.mp3', '.wav', '.flac']
            
            if (any(ext in path for ext in download_extensions) or 
                'download' in text or 'download' in url or
                'hubcloud' in domain or 'gdflix' in domain or 'gdtot' in domain):
                categories['Download Links'].append(link)
            
            # Social media links
            social_domains = ['facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com', 
                            'youtube.com', 'tiktok.com', 'pinterest.com', 'snapchat.com',
                            'telegram.me', 't.me', 'discord.gg', 'reddit.com']
            
            if any(social in domain for social in social_domains):
                categories['Social Media'].append(link)
            
            # Email links
            if link['url'].startswith('mailto:'):
                categories['Email Links'].append(link)
            
            # Phone links
            if link['url'].startswith('tel:'):
                categories['Phone Links'].append(link)
            
            # Image links
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico']
            if any(ext in path for ext in image_extensions):
                categories['Image Links'].append(link)
            
            # Media links (video/audio streaming)
            media_domains = ['youtube.com', 'vimeo.com', 'dailymotion.com', 'twitch.tv', 
                           'spotify.com', 'soundcloud.com']
            if any(media in domain for media in media_domains):
                categories['Media Links'].append(link)
            
            # External vs Internal links
            # This would need the original domain to compare
            # For now, we'll categorize based on domain
            
            # Navigation links
            if (any(nav in text for nav in ['home', 'about', 'contact', 'blog', 'news', 'menu']) or
                any(nav in path for nav in ['/home', '/about', '/contact', '/blog', '/news'])):
                categories['Navigation'].append(link)
            
            # If not categorized yet, put in general external links
            if not any(link in cat for cat in categories.values()):
                categories['External Links'].append(link)
        
        # Convert defaultdict to regular dict and sort
        return {k: v for k, v in sorted(categories.items()) if v}
    
    def _filter_download_links(self, links):
        """Filter and return only download links"""
        download_links = []
        
        for link in links:
            url = link['url'].lower()
            text = link['text'].lower()
            original_href = link['original_href'].lower()
            
            # Parse URL for analysis
            parsed = urlparse(link['url'])
            domain = parsed.netloc.lower()
            path = parsed.path.lower()
            
            # Download link indicators
            download_extensions = ['.zip', '.rar', '.7z', '.tar', '.gz', '.exe', '.msi', '.dmg', '.pkg', 
                                 '.deb', '.rpm', '.apk', '.ipa', '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
                                 '.ppt', '.pptx', '.mp4', '.mkv', '.avi', '.mov', '.mp3', '.wav', '.flac']
            
            # Download domains (file hosting services)
            download_domains = ['hubcloud', 'gdflix', 'gdtot', 'drive.google', 'mega.nz', 'mediafire',
                              'dropbox', 'onedrive', 'box.com', 'wetransfer', 'sendspace', 'zippyshare',
                              'uploadhaven', '4shared', 'rapidgator', 'turbobit', 'nitroflare', 'gdlink',
                              'gofile.io', 'anonfiles', 'catbox.moe', 'pixeldrain', 'krakenfiles',
                              'upload.ee', 'filebin.net', 'temp.sh', 'streamtape', 'doodstream']
            
            # Very specific download keywords - only actual download terms
            download_keywords = ['download', 'direct-dl', 'drive-login', 'file/', 'dl/', 'hubcloud', 'gdflix', 'gdtot']
            
            # Check if this is a download link
            is_download = (
                # File extensions
                any(ext in path for ext in download_extensions) or
                # Hosting domains
                any(domain_name in domain for domain_name in download_domains) or
                # Keywords in text
                any(keyword in text for keyword in download_keywords) or
                # Keywords in URL
                any(keyword in url for keyword in download_keywords) or
                # Common download URL patterns
                'file/' in url or 'dl/' in url or 'download/' in url or
                '/drive/' in url or '/folder/' in url or '/view/' in url or
                # Skip navigation, social, and site links - be very strict
                not any(skip in text.lower() for skip in ['home', 'about', 'contact', 'telegram', 'facebook', 'twitter', 'instagram', 'join', 'channel', 'support', 'visit', 'official', 'website', 'spot', 'perfect', 'thank', 'sharing']) and
                not any(skip in url for skip in ['facebook.com', 'twitter.com', 'instagram.com', 't.me', 'telegram.me', 'moviesdrives.cv', 'moviesdrive.cc']) and
                # Must be from known hosting service or have download-specific patterns
                (any(domain_name in domain for domain_name in download_domains) or 
                 any(keyword in url for keyword in ['file/', 'dl/', 'download/', '/drive/']) or
                 any(ext in path for ext in download_extensions))
            )
            
            if is_download:
                download_links.append(link)
        
        return download_links
    
    def get_link_preview(self, url):
        """Get basic preview info for a link (title, description)"""
        try:
            response = self.session.head(url, timeout=5)
            content_type = response.headers.get('content-type', '').lower()
            content_length = response.headers.get('content-length')
            
            preview = {
                'content_type': content_type,
                'content_length': content_length,
                'status_code': response.status_code
            }
            
            # If it's HTML, try to get title and description
            if 'text/html' in content_type:
                response = self.session.get(url, timeout=5)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                title_tag = soup.find('title')
                if title_tag:
                    preview['title'] = title_tag.get_text(strip=True)
                
                desc_tag = soup.find('meta', attrs={'name': 'description'})
                if desc_tag and hasattr(desc_tag, 'attrs') and 'content' in desc_tag.attrs:
                    preview['description'] = desc_tag.attrs['content']
            
            return preview
            
        except Exception as e:
            logging.error(f"Error getting link preview: {str(e)}")
            return {'error': str(e)}
