#!/usr/bin/env python
import requests
import re
import urlparse

target_url="http://10.0.2.15/mutillidae/"
target_links = []

def extract_links_from(url):
    response = requests.get(target_url)
    return re.findall('(?:href=")(.*?)"',response.content)



def craw(url):
    href_links = extract_links_from(url)
    for link in href_links:
        link = urlparse.urljoin(url, link)
        
        if "#" in link:
            link = link.split("#")[0]
    
        if url in link and link not in target_links:
            target_links.append(link)
            print(link)
            craw(link)

craw(target_url)
