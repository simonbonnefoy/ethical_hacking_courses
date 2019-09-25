#!/usr/bin/env python
import requests

url = "10.0.2.15"

def request(url):
    try:
        return requests.get("http://" + url)
    except requests.exceptions.ConnectionError: 
        pass

target_url="10.0.2.15"

#with open ("/root/pycharm/ethical_hacking/crawler/subdomains-wodlist.txt","r") as wordlist_file:
with open ("/root/pycharm/ethical_hacking/courses/python_ethical_hacking_from_scratch/web/crawler/files-and-dirs-wordlist.txt","r") as wordlist_file:
    for line in wordlist_file:
        word = line.strip()
        #test_url = word + "." + target_url
        test_url = target_url +"/" + word
        response = request(test_url)
        if response:
            print("[+] Discovered url --> " + test_url)
        if response.status_code != 404:
            print("[/] url --> %s with status code %i"%(test_url,response.status_code))

           # print("[+] Discovered subdomain --> " + test_url)
