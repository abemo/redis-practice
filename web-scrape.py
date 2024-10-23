import requests
from bs4 import BeautifulSoup
import redis
from urllib.parse import urljoin, urlparse
import config

redis_host = config.redis_host
redis_port = config.redis_port
redis_password = config.redis_password

r = redis.StrictRedis(
    host=redis_host,
    port=redis_port,
    password=redis_password,
    decode_responses=True  
)

def scrape_wikipedia(start_url, end_url):
    visited = set()  # Set to track visited URLs
    queue = [start_url]  # Initialize the queue with the start URL
    
    while queue:
        current_url = queue.pop(0)  # Get the next URL to scrape (FIFO)
        
        if current_url in visited:
            continue  # Skip already visited URLs
        
        # Mark the current URL as visited
        visited.add(current_url)
        
        if r.exists(current_url):
            print(f"{current_url} already stored in Redis, skipping.")
            continue  # Skip URLs that are already in Redis

        try:
            # Send a GET request to the current URL
            response = requests.get(current_url)
            response.raise_for_status()  # Check for HTTP errors

            # Store the HTML content in Redis
            html_content = response.text
            r.set(current_url, html_content)
            print(f"Stored {current_url} in Redis.")

            # Check if we've reached the target end URL
            if current_url == end_url:
                print(f"Reached the end URL: {end_url}")
                break
            
            # Parse the HTML to find all internal Wikipedia links
            soup = BeautifulSoup(html_content, 'html.parser')

            # Find all <a> tags and extract hrefs (links)
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Resolve relative URLs and filter for Wikipedia pages
                full_url = urljoin(current_url, href)

                # Ensure we're only following internal Wikipedia links
                if urlparse(full_url).netloc.endswith("wikipedia.org") and full_url not in visited:
                    queue.append(full_url)  # Add the new URL to the queue

        except requests.exceptions.RequestException as e:
            print(f"Error scraping {current_url}: {e}")
        except redis.RedisError as e:
            print(f"Error storing {current_url} in Redis: {e}")

if __name__ == "__main__":
    start_url = "https://en.wikipedia.org/wiki/Web_scraping"  
    end_url = "https://en.wikipedia.org/wiki/Data_mining"     
    scrape_wikipedia(start_url, end_url)
