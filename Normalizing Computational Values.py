import sqlite3
import ast
#This is a file that give page_rank and TFIDF scores in a normalized format
conn = sqlite3.connect('Data.db')

cur = conn.cursor()

cur.execute("SELECT id, TFIDFWords, pageRank FROM text")

links = cur.fetchall()
links = [list(link) for link in links]

page_rank_vals = [link[2] for link in links]
min_pr = min(page_rank_vals)
max_pr = max(page_rank_vals)

normalized_page_rank = {doc: (score - min_pr) / (max_pr - min_pr) for doc, i, score in links}

for num in range(len(links)):
    link = links[num]
    link[1] = ast.literal_eval(link[1])
    values = list(link[1].values())
    min_TFIDF = min(values)
    max_TFIDF = max(values)
    try:
        normalized_TFIDF = {word: (score - min_TFIDF) / (max_TFIDF - min_TFIDF) for word, score in link[1].items()}
    except:
        pass
    link[1] = str(normalized_TFIDF)
    links[num] = link
print(len(links))
for link in links:
    cur.execute("""UPDATE text
                          SET TFIDFWords = ?, pageRank = ?
                          WHERE id = ?""",(link[1],link[2],link[0]))
conn.commit()
cur.close()
conn.close()