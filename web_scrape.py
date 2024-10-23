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
    visited = set()  
    queue = [start_url]  
    
    while queue:
        current_url = queue.pop(0)  
        
        if current_url in visited:
            continue  
        
        visited.add(current_url)
        
        if r.exists(current_url):
            print(f"{current_url} already stored in Redis, skipping.")
            continue  

        try:
            response = requests.get(current_url)
            response.raise_for_status()  

            html_content = response.text
            r.set(current_url, html_content)
            print(f"Stored {current_url} in Redis.")

            if current_url == end_url:
                print(f"Reached the end URL: {end_url}")
                break
            
            soup = BeautifulSoup(html_content, 'html.parser')

            for link in soup.find_all('a', href=True):
                href = link['href']
                
                full_url = urljoin(current_url, href)

                if urlparse(full_url).netloc.endswith("wikipedia.org") and full_url not in visited:
                    queue.append(full_url)  

        except requests.exceptions.RequestException as e:
            print(f"Error scraping {current_url}: {e}")
        except redis.RedisError as e:
            print(f"Error storing {current_url} in Redis: {e}")

if __name__ == "__main__":
    start_url = "https://en.wikipedia.org/wiki/Web_scraping"  
    end_url = "https://en.wikipedia.org/wiki/Data_mining"     
    scrape_wikipedia(start_url, end_url)
