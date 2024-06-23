import requests
from bs4 import BeautifulSoup
import json
import sys
import datetime
import urllib

def get_search_results(phrase, proxy_url=None):
    # Membuat URL pencarian
    filtered_phrase = get_modified_phrase(phrase) #In case the phrase consist of more than 1 word
    search_url = f"https://en.wikipedia.org/wiki/{filtered_phrase}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None

    response = requests.get(search_url, headers=headers, proxies=proxies)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    # print(soup)
    
    # Get all the necessary data
    content = []
    for paragraph in soup.find_all('p'):
        content.append(paragraph.get_text())

    results = []
    for item in soup.find_all(class_='mw-page-title-main'):
        title = item.get_text()

    link = search_url
    date, category = None, None
    results.append({"title": title, "link": link, "content": content, "date": date, "category":category})
    
    return results

def get_modified_phrase(phrase):
    split_phrase = phrase.split(" ")
    filtered_phrase = ''
    for i in range(len(split_phrase)):
        phr = split_phrase[i]
        filtered_phrase += phr
        if (i != len(split_phrase)-1):
            filtered_phrase += "_"
    return filtered_phrase

def save_results_to_json(results, phrase):
    # Agar tidak tertimpa untuk phrase yang sama
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{phrase.replace(' ', '_')}_{timestamp}.json"
    
    # JSON file
    with open(filename, 'w') as file:
        json.dump(results, file, indent=4)
    
    print(f"Results saved to {filename}")

if __name__ == "__main__":
    phrase = sys.argv[1]
    proxy_url = sys.argv[2] if len(sys.argv) > 2 else None
    
    results = get_search_results(phrase, proxy_url)
    save_results_to_json(results, phrase)
