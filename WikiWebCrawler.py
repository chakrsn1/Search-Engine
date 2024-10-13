from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin
import SearchingFunctions
from langdetect import detect
import sqlite3
import re
import math
import time

# Initialize Chrome driver, service, database, amount of links stored in database, seed, and loop specific variables
service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
connection = sqlite3.connect("Data.db")
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS text (id INTEGER PRIMARY KEY, url TEXT,TFIDFWords TEXT, pageRank REAL,pageTitle TEXT)")
link_count = 1500
seed = 'https://en.wikipedia.org/'
lang = "en"
queue = [seed]
url_count = 0
link_reference = []
url_to_id = {}
id_to_url = {}
website_data = {}
wordsinLinks = {}
all_links = set()

#Gets all of the data needed for database (outside of pageRank and TFIDF)
while queue:

    #Gets content of page and makes sure it is English
    time.sleep(0.1)
    current_url = queue.pop(0)
    driver.get(current_url)
    text = driver.page_source
    soup = BeautifulSoup(text, 'html.parser')
    try:
        language = detect(soup.text)
    except:
        language = lang + "NOT"
    if language == lang:
        links = []
        for link in soup.find_all('a', href=True):
            #Finds all referenced links to add to queue
            reference_link = link.get('href')
            full_url = urljoin(current_url, reference_link)
            links.append(full_url)
            if full_url not in all_links and "wiki" in full_url.lower():#Second part is only for this demo so that I can safely scrape the data
                queue.append(full_url)
                all_links.add(full_url)

        # Find frequency of words for TFIDF
        word_frequency = {}
        words = 0
        for line in soup.text.split("\n"):
            if line:
                for word in line.lower().split():
                    word = re.sub('[^a-zA-Z]+', '', word)
                    if word_frequency.get(word):
                        word_frequency[word] += 1
                    else:
                        word_frequency[word] = 1
                    words += 1
        for word in word_frequency:
            word_frequency[word] /= words
            if wordsinLinks.get(word):
                wordsinLinks[word] += 1
            else:
                wordsinLinks[word] = 1
        try:
            page_title = soup.find('title').string
        except:
            page_title = "No Page Title"
        print(page_title)
        website_data[url_count] = {
            "url": current_url,
            "Word Frequency": word_frequency,
            "Title": page_title
        }

        #Gets link references for PageRank
        link_reference.append(links)
        url_to_id[current_url] = url_count
        id_to_url[url_count] = current_url

        url_count += 1
        if url_count == link_count:
            break

#Makes the PageRank and TFIDF values for database
all_link_references = []
for links in link_reference:
    link_references = []
    for link in links:
        if url_to_id.get(link):
            link_references.append(url_to_id.get(link))
    all_link_references.append(link_references)
for word in wordsinLinks:
    wordsinLinks[word] = math.log(link_count/wordsinLinks[word])
pageRank = SearchingFunctions.PageRank(all_link_references)
for num in range(link_count):
    for word in website_data[num]["Word Frequency"]:
        website_data[num]["Word Frequency"][word] *= wordsinLinks[word]
    cursor.execute('''
    INSERT INTO text (id, url, TFIDFWords, pageRank, pageTitle)
    VALUES (?, ?, ?, ?, ?)
    ''', (num,id_to_url[num],str(website_data[num]["Word Frequency"]),pageRank[num],website_data[num]["Title"]))


driver.quit()
connection.commit()
connection.close()
