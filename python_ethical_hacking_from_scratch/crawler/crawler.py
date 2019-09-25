#!/usr/bin/env python
import requests

url = "maillli.google.com"

def request(url):
    try:
        return requests.get("http://" + url)
    except requests.exceptions.ConnectionError: 
        pass

with open ("/root/Downloads/subdomains.list","r") as wordlist_file:

