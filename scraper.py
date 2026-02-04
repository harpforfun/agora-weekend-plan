import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

def search_activities(query, date=None):
    """
    Search for activities in Toronto from multiple sources
    
    Args:
        query (str): Search query (e.g., "museums", "outdoor activities")
        date (str): Optional date filter in YYYY-MM-DD format
        
    Returns:
        list: List of activity dictionaries
    """
    activities = []
    
    # Search multiple sources
    logger.info(f"Searching across multiple sources for: {query}")
    
    # Search Toronto.com
    toronto_com_results = scrape_toronto_com(query, date)
    activities.extend(toronto_com_results)
    
    # Search BlogTO
    blogto_results = scrape_blogto(query, date)
    activities.extend(blogto_results)
    
    # Search Narcity Toronto
    narcity_results = scrape_narcity(query, date)
    activities.extend(narcity_results)
    
    # Remove duplicates based on URL
    activities = deduplicate_activities(activities)
    
    logger.info(f"Found {len(activities)} unique activities from {len(activities)} total across all sources")
    return activities

def deduplicate_activities(activities):
    """
    Remove duplicate activities based on source URL
    
    Args:
        activities (list): List of activity dictionaries
        
    Returns:
        list: Deduplicated list of activities
    """
    seen_urls = set()
    unique_activities = []
    
    for activity in activities:
        url = activity.get('source_url', '')
        # Also check for duplicate titles as fallback
        title = activity.get('title', '')
        key = url if url else title
        
        if key and key not in seen_urls:
            seen_urls.add(key)
            unique_activities.append(activity)
    
    return unique_activities

def fetch_images_from_page(url):
    """
    Fetch images from a target page URL
    
    Args:
        url (str): The URL to fetch images from
        
    Returns:
        list: List of image URLs found on the page
    """
    images = []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        logger.info(f"Fetching images from: {url}")
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Priority 1: Look for images in the main content area (not header/title)
        content_area = soup.find(['article', 'main', 'div'], class_=re.compile(r'(content|article-body|post-content|entry-content|article-content)', re.I))
        
        if content_area:
            # Get images from content, excluding header/title sections
            img_elements = []
            for img in content_area.find_all('img', src=True):
                # Skip images in header/title/nav sections
                parent_classes = ' '.join(img.parent.get('class', []))
                if not re.search(r'(header|title|nav|menu|sidebar|widget)', parent_classes, re.I):
                    img_elements.append(img)
            
            logger.info(f"Found {len(img_elements)} content images")
        else:
            # Priority 2: Look for og:image meta tag
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                og_url = og_image['content']
                if is_valid_image_url(og_url):
                    images.append(og_url)
                    logger.info(f"Found og:image meta tag")
                    return images
            
            # Priority 3: Get images from any article/post, excluding headers
            article = soup.find(['article', 'div'], class_=re.compile(r'(post|article)', re.I))
            if article:
                img_elements = article.find_all('img', src=True)
            else:
                img_elements = []
        
        # Extract image URLs from content images, validating each one
        for img in img_elements:
            if len(images) >= 5:  # Limit to first 5 valid images
                break
                
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if not src:
                continue
            
            # Make absolute URL if relative
            if not src.startswith('http'):
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    from urllib.parse import urljoin
                    src = urljoin(url, src)
            
            # Filter out small images, icons, logos, and header images
            if re.search(r'(icon|logo|button|avatar|thumb|header|banner|nav|placeholder|blank|default)', src, re.I):
                logger.debug(f"Skipping image (pattern match): {src}")
                continue
            
            # Check image dimensions if available
            width = img.get('width')
            height = img.get('height')
            
            # Skip images that are clearly too small (likely icons)
            if width and height:
                try:
                    if int(width) < 200 or int(height) < 200:
                        logger.debug(f"Skipping small image: {src}")
                        continue
                except:
                    pass
            
            # Validate the image URL is not blank/placeholder
            if is_valid_image_url(src):
                images.append(src)
                logger.info(f"Added valid image: {src}")
            else:
                logger.debug(f"Skipping invalid/blank image: {src}")
        
        logger.info(f"Found {len(images)} valid images from {url}")
        
    except Exception as e:
        logger.warning(f"Error fetching images from {url}: {str(e)}")
    
    return images

def is_valid_image_url(image_url):
    """
    Validate that an image URL is not a blank/placeholder image
    
    Args:
        image_url (str): The image URL to validate
        
    Returns:
        bool: True if the image appears valid, False otherwise
    """
    if not image_url:
        return False
    
    # Check for common placeholder/blank image patterns in URL
    invalid_patterns = [
        r'placeholder',
        r'blank',
        r'spacer',
        r'transparent',
        r'1x1',
        r'pixel\.(gif|png|jpg)',
        r'grey\.gif',
        r'gray\.gif',
        r'loading\.(gif|png)',
        r'ajax-loader',
        r'spinner',
        r'no-image',
        r'noimage',
        r'default\.(jpg|png|gif)',
        r'data:image'  # base64 encoded small images
    ]
    
    for pattern in invalid_patterns:
        if re.search(pattern, image_url, re.I):
            return False
    
    # Try to validate the image by checking its headers
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.head(image_url, headers=headers, timeout=3, allow_redirects=True)
        
        # Check if it's actually an image
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            logger.debug(f"Not an image content-type: {content_type}")
            return False
        
        # Check file size - reject very small images (likely placeholders)
        content_length = response.headers.get('content-length')
        if content_length:
            size = int(content_length)
            if size < 1000:  # Less than 1KB is likely a placeholder
                logger.debug(f"Image too small: {size} bytes")
                return False
        
        return True
        
    except Exception as e:
        # If we can't validate, assume it's valid rather than rejecting
        logger.debug(f"Could not validate image {image_url}: {str(e)}")
        return True

def scrape_toronto_com(query, date=None):
    """
    Scrape activities from Toronto.com
    
    Args:
        query (str): Search query
        date (str): Optional date filter
        
    Returns:
        list: List of activity dictionaries
    """
    activities = []
    
    try:
        # Toronto.com search URL
        search_url = "https://www.toronto.com/search/"
        params = {
            'q': query,
            'section': 'things-to-do'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        logger.info(f"Fetching from Toronto.com: {search_url} with query: {query}")
        
        response = requests.get(search_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Parse search results
        # Note: This is a generic parser - actual selectors may need adjustment
        # based on Toronto.com's current HTML structure
        
        # Try to find article or result containers
        result_containers = soup.find_all(['article', 'div'], class_=re.compile(r'(article|result|card|item|post)', re.I))
        
        if not result_containers:
            # Fallback: try to find any links in the content area
            result_containers = soup.find_all('a', href=re.compile(r'/(things-to-do|whats-on|events)/'))
        
        logger.info(f"Found {len(result_containers)} potential results")
        
        for container in result_containers[:10]:  # Limit to first 10 results
            try:
                activity = parse_toronto_com_result(container)
                if activity:
                    activities.append(activity)
            except Exception as e:
                logger.warning(f"Error parsing result: {str(e)}")
                continue
        
        # If no results found, create sample activities for demonstration
        if not activities:
            logger.warning("No results found, creating sample activities")
            activities = create_sample_activities(query)
            
    except requests.RequestException as e:
        logger.error(f"Error fetching from Toronto.com: {str(e)}")
        # Return sample activities on error for demonstration
        activities = create_sample_activities(query)
    except Exception as e:
        logger.error(f"Unexpected error in scrape_toronto_com: {str(e)}", exc_info=True)
        activities = create_sample_activities(query)
    
    return activities

def parse_toronto_com_result(container):
    """
    Parse a single result container from Toronto.com
    
    Args:
        container: BeautifulSoup element containing the result
        
    Returns:
        dict: Activity dictionary or None if parsing fails
    """
    try:
        # Try to find title
        title_elem = container.find(['h2', 'h3', 'h4', 'a'])
        title = title_elem.get_text(strip=True) if title_elem else None
        
        # Try to find link
        link_elem = container.find('a', href=True)
        url = link_elem['href'] if link_elem else None
        if url and not url.startswith('http'):
            url = 'https://www.toronto.com' + url
        
        # Try to find description
        desc_elem = container.find(['p', 'div'], class_=re.compile(r'(description|excerpt|summary)', re.I))
        description = desc_elem.get_text(strip=True)[:200] if desc_elem else "Click to learn more about this activity."
        
        # Try to find image in the search result first
        img_elem = container.find('img', src=True)
        image_url = img_elem['src'] if img_elem else None
        if image_url and not image_url.startswith('http'):
            image_url = 'https://www.toronto.com' + image_url
        
        # If no image found in search result, try to fetch from the actual page
        images = []
        if image_url:
            images = [image_url]
        elif url:
            # Fetch images from the target page
            page_images = fetch_images_from_page(url)
            images = page_images[:3] if page_images else []
        
        if title and url:
            return {
                'id': hash(url),
                'title': title,
                'description': description,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'location': 'Toronto, ON',
                'images': images,
                'source_url': url,
                'source_site': 'Toronto.com'
            }
    except Exception as e:
        logger.warning(f"Error parsing container: {str(e)}")
        return None
    
    return None

def scrape_blogto(query, date=None):
    """
    Scrape activities from BlogTO
    
    Args:
        query (str): Search query
        date (str): Optional date filter
        
    Returns:
        list: List of activity dictionaries
    """
    activities = []
    
    try:
        # BlogTO search URL
        search_url = "https://www.blogto.com/search/"
        params = {
            'q': query
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        logger.info(f"Fetching from BlogTO: {search_url} with query: {query}")
        
        response = requests.get(search_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Parse search results
        result_containers = soup.find_all(['article', 'div'], class_=re.compile(r'(post|article|item|result)', re.I))
        
        logger.info(f"Found {len(result_containers)} potential BlogTO results")
        
        for container in result_containers[:5]:  # Limit to first 5 results
            try:
                activity = parse_blogto_result(container)
                if activity:
                    activities.append(activity)
            except Exception as e:
                logger.warning(f"Error parsing BlogTO result: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error fetching from BlogTO: {str(e)}")
    
    return activities

def parse_blogto_result(container):
    """
    Parse a single result container from BlogTO
    
    Args:
        container: BeautifulSoup element containing the result
        
    Returns:
        dict: Activity dictionary or None if parsing fails
    """
    try:
        # Find title and link
        title_elem = container.find(['h2', 'h3', 'a'])
        title = title_elem.get_text(strip=True) if title_elem else None
        
        link_elem = container.find('a', href=True)
        url = link_elem['href'] if link_elem else None
        if url and not url.startswith('http'):
            url = 'https://www.blogto.com' + url
        
        # Find description
        desc_elem = container.find(['p', 'div'], class_=re.compile(r'(excerpt|description|summary)', re.I))
        description = desc_elem.get_text(strip=True)[:200] if desc_elem else "Discover this activity in Toronto."
        
        # Find image
        img_elem = container.find('img', src=True)
        image_url = img_elem.get('src') or img_elem.get('data-src')
        if image_url and not image_url.startswith('http'):
            image_url = 'https://www.blogto.com' + image_url
        
        if title and url:
            return {
                'id': hash(url),
                'title': title,
                'description': description,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'location': 'Toronto, ON',
                'images': [image_url] if image_url else [],
                'source_url': url,
                'source_site': 'BlogTO'
            }
    except Exception as e:
        logger.warning(f"Error parsing BlogTO container: {str(e)}")
        return None
    
    return None

def scrape_narcity(query, date=None):
    """
    Scrape activities from Narcity Toronto
    
    Args:
        query (str): Search query
        date (str): Optional date filter
        
    Returns:
        list: List of activity dictionaries
    """
    activities = []
    
    try:
        # Narcity search URL
        search_url = "https://www.narcity.com/search"
        params = {
            'q': f"{query} Toronto"
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        logger.info(f"Fetching from Narcity: {search_url} with query: {query}")
        
        response = requests.get(search_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Parse search results
        result_containers = soup.find_all(['article', 'div'], class_=re.compile(r'(post|article|card|item)', re.I))
        
        logger.info(f"Found {len(result_containers)} potential Narcity results")
        
        for container in result_containers[:5]:  # Limit to first 5 results
            try:
                activity = parse_narcity_result(container)
                if activity:
                    activities.append(activity)
            except Exception as e:
                logger.warning(f"Error parsing Narcity result: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error fetching from Narcity: {str(e)}")
    
    return activities

def parse_narcity_result(container):
    """
    Parse a single result container from Narcity
    
    Args:
        container: BeautifulSoup element containing the result
        
    Returns:
        dict: Activity dictionary or None if parsing fails
    """
    try:
        # Find title and link
        title_elem = container.find(['h2', 'h3', 'h4', 'a'])
        title = title_elem.get_text(strip=True) if title_elem else None
        
        link_elem = container.find('a', href=True)
        url = link_elem['href'] if link_elem else None
        if url and not url.startswith('http'):
            url = 'https://www.narcity.com' + url
        
        # Find description
        desc_elem = container.find(['p', 'div'], class_=re.compile(r'(excerpt|description|summary|dek)', re.I))
        description = desc_elem.get_text(strip=True)[:200] if desc_elem else "Check out this Toronto activity."
        
        # Find image
        img_elem = container.find('img', src=True)
        image_url = img_elem.get('src') or img_elem.get('data-src')
        if image_url and not image_url.startswith('http'):
            if image_url.startswith('//'):
                image_url = 'https:' + image_url
            else:
                image_url = 'https://www.narcity.com' + image_url
        
        if title and url:
            return {
                'id': hash(url),
                'title': title,
                'description': description,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'location': 'Toronto, ON',
                'images': [image_url] if image_url else [],
                'source_url': url,
                'source_site': 'Narcity'
            }
    except Exception as e:
        logger.warning(f"Error parsing Narcity container: {str(e)}")
        return None
    
    return None

def create_sample_activities(query):
    """
    Create sample activities for demonstration purposes
    
    Args:
        query (str): Search query
        
    Returns:
        list: List of sample activity dictionaries
    """
    # Capitalize first letter of query
    query_title = query.strip().title() if query else "Activities"
    
    samples = [
        {
            'id': 1,
            'title': f'Explore {query_title} at CN Tower',
            'description': 'Experience breathtaking views from one of Toronto\'s most iconic landmarks. Perfect for tourists and locals alike.',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'location': 'CN Tower, 301 Front St W, Toronto',
            'images': ['https://images.unsplash.com/photo-1517935706615-2717063c2225?w=400'],
            'source_url': 'https://www.toronto.com/things-to-do/cn-tower',
            'source_site': 'Toronto.com'
        },
        {
            'id': 2,
            'title': f'Discover {query_title} at Royal Ontario Museum',
            'description': 'Explore world cultures and natural history at Canada\'s largest museum with over 6 million objects.',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'location': 'Royal Ontario Museum, 100 Queens Park, Toronto',
            'images': ['https://images.unsplash.com/photo-1566127992631-137a642a90f4?w=400'],
            'source_url': 'https://www.toronto.com/things-to-do/royal-ontario-museum',
            'source_site': 'Toronto.com'
        },
        {
            'id': 3,
            'title': f'{query_title} Experience at Harbourfront Centre',
            'description': 'Year-round cultural activities, festivals, and events on Toronto\'s beautiful waterfront.',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'location': 'Harbourfront Centre, 235 Queens Quay W, Toronto',
            'images': ['https://images.unsplash.com/photo-1519003722824-194d4455a60c?w=400'],
            'source_url': 'https://www.toronto.com/things-to-do/harbourfront-centre',
            'source_site': 'Toronto.com'
        },
        {
            'id': 4,
            'title': f'{query_title} at Toronto Islands',
            'description': 'Escape to a peaceful oasis just minutes from downtown with beaches, parks, and stunning skyline views.',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'location': 'Toronto Islands, Toronto',
            'images': ['https://images.unsplash.com/photo-1568643243187-ac6c03700c02?w=400'],
            'source_url': 'https://www.toronto.com/things-to-do/toronto-islands',
            'source_site': 'Toronto.com'
        },
        {
            'id': 5,
            'title': f'Enjoy {query_title} at St. Lawrence Market',
            'description': 'One of the world\'s best food markets with fresh produce, specialty foods, and artisan goods.',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'location': 'St. Lawrence Market, 93 Front St E, Toronto',
            'images': ['https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=400'],
            'source_url': 'https://www.toronto.com/things-to-do/st-lawrence-market',
            'source_site': 'Toronto.com'
        }
    ]
    
    return samples
