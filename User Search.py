import sqlite3
import re
import ast

#Allows the user to search from the database a particular value
page_rank_importance = 0.5
TDIDF_importance = 0.5

conn = sqlite3.connect('Data.db')

cur = conn.cursor()

cur.execute("SELECT * FROM text")

links = cur.fetchall()

conn.close()
website_data = {}
for link in links:
    website_data[link[1]] = {
        "TFIDF": ast.literal_eval(link[2]),
        "Page Rank": link[3],
        "Title": link[4]
    }
while True:
    query = input("What do you want to search about?").lower()
    query = query.split()
    values = {link: 0 for link in website_data}
    for word in query:
        word = re.sub('[^a-zA-Z]+', '', word)
        for link in website_data:
            if website_data[link]["TFIDF"].get(word):
                score = website_data[link]["TFIDF"].get(word) * TDIDF_importance + website_data[link]["Page Rank"] * page_rank_importance
                values[link] += score
    links = list(values.keys())
    scores = list(values.values())
    links = [link for _,link in sorted(zip(scores,links),reverse=True)][:10]
    for link in links:
        print(f'{website_data[link]["Title"]}:\n{link}')
