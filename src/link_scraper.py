from scraper import *
import urllib
import os
import signal

def get_artikel_terkait(url): # Mendapatkan semua url dari artikel terkait
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    html_content = response.content
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    see_also_links = []
    see_also_section = soup.find('span', id='See_also')
    if see_also_section:
        ul = see_also_section.find_next('ul')
        if ul:
            for li in ul.find_all('li'):
                a = li.find('a')
                if a and 'href' in a.attrs:
                    link = urllib.parse.urljoin(url, a['href'])
                    see_also_links.append(link)
    
    return see_also_links

def get_info(url, proxy_url=None): # Mendapatkan semua informasi dari artikel
    search_url = url
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None

    response = requests.get(search_url, headers=headers, proxies=proxies)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Get all the necessary data
    content = []
    for paragraph in soup.find_all('p'):
        content.append(paragraph.get_text())

    results = []
    title = ''
    for item in soup.find_all(class_='mw-page-title-main'):
        title = item.get_text()

    related = get_artikel_terkait(url)
    date = get_create(title)
    results.append({"title": title, "content": content, "related article": related, "createdAt": date})
    
    return results

def get_create(title): # Mendapatkan tanggal pembuatan artikel pertama kali
    encoded_title = get_modified_phrase(title)
    history_url = f"https://en.wikipedia.org/w/index.php?title={encoded_title}&action=history&dir=prev"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(history_url, headers=headers)
    html_content = response.content
    
    soup = BeautifulSoup(html_content, 'html.parser')
    first_revision = soup.find('a', class_='mw-changeslist-date')
    creation_date = first_revision.get_text() if first_revision else 'Unknown'
    try:
        creation_date_obj = datetime.datetime.strptime(creation_date, '%H:%M, %d %B %Y')
        creation_date_formatted = creation_date_obj.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    except ValueError:
        creation_date_formatted = 'Unknown'
    
    return creation_date_formatted
    
def get_result(url, result, visited_links): # Fungsi rekursif untuk memperoleh semua data
    if url in visited_links:
        return result, visited_links

    visited_links.add(url)
    result.append(get_info(url))
    
    related_articles = get_artikel_terkait(url)
    for article in related_articles:
        print(article)
        if article not in visited_links:
            get_result(article, result, visited_links)
    
    return result, visited_links

def parse_links_from_file(file_path): # Parser
    links = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                link = line.strip()
                if link:
                    links.append(link)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return links

def termination_handler(sig, frame): # Interrupt handler
    print('Process interrupted! Saving results...')
    save_to_json(result,"result")
    os._exit(0)

if __name__ == "__main__":
    file = sys.argv[1]
    signal.signal(signal.SIGINT, termination_handler) #Menangani interrupt
    result = []
    visited_links = set()
    urls = parse_links_from_file(file)
    for url in urls:
        try:
            result, visited_links = get_result(url, result, visited_links)
        finally:
            save_to_json(result,"result")
