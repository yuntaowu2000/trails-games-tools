import requests
from bs4 import BeautifulSoup
import opencc

converter = opencc.OpenCC('t2s.json')

for i in range(1, 10):
    url = "https://cloudedleopardent.com/game/hajimari/zh/story/3and9/0{}.html".format(i)

    res = requests.get(url)
    bs = BeautifulSoup(res.text,'html.parser')
    paragraphs = bs.find_all('p')

    with open("3and9.txt", "a+", encoding="utf-8") as f:
        for i in range(len(paragraphs)):
            p = converter.convert(paragraphs[i].text)
            f.write(p)
            f.write('\n')
        f.write('\n\n')

url = "https://cloudedleopardent.com/game/hajimari/zh/story/3and9/10.html".format(i)

res = requests.get(url)
bs = BeautifulSoup(res.text,'html.parser')
paragraphs = bs.find_all('p')

with open("3and9.txt", "a+", encoding="utf-8") as f:
    for i in range(len(paragraphs)):
        p = converter.convert(paragraphs[i].text)
        f.write(p)
        f.write('\n')