#!/usr/bin/env python
import requests

def download(url):
    get_response = requests.get(url)
    file_name = url.split("/")[-1]
    print(get_response.content)
    with open(file_name, "wb") as out_file:
        out_file.write(get_response.content)

download("https://car-images.bauersecure.com/pagefiles/70980/001.jpg")
