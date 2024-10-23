import web_scrape
import redis
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import tkinter as tk


def visualize_internal_links():
    keys = web_scrape.r.keys()
    page_url_counts = []

    for key in keys:
        soup = BeautifulSoup(web_scrape.r.get(key), 'html.parser')
        tags = soup('a')
        page_url_counts.append((key, len(tags)))
    
    page_url_counts.sort(key=lambda x: x[1], reverse=True)    
    return page_url_counts

def printAll():
    keys = web_scrape.r.keys()
    for key in keys:
        print(web_scrape.r.get(key))

def update_url(key):
    original_html = web_scrape.r.get(key)
    only_urls = []
    
    soup = BeautifulSoup(original_html, 'html.parser')
    tags = soup('a')
    for tag in tags:
        only_urls.append(tag.get('href'))
        
    web_scrape.r.set(key, str(only_urls))

def update_all_urls():
    keys = web_scrape.r.keys()
    for key in keys:
        update_url(key)

def clear_db():
    web_scrape.r.flushdb()
    
def clear_key(key):
    web_scrape.r.delete(key)

def main():
    start_url = "https://en.wikipedia.org/wiki/Web_scraping"  
    end_url = "https://en.wikipedia.org/wiki/Data_mining"  
    
    web_scrape.scrape_wikipedia(start_url, end_url)
    # print(web_scrape.r.get("https://en.wikipedia.org/wiki/Web_scraping"))
    # print(visualize_internal_links()[:5])
    # update_all_urls()
    # printAll()
    # clear_db()
    # printAll()
    

    
    
if __name__ == "__main__":
    main()

    