import requests
from bs4 import BeautifulSoup
import opencc
import sys

suburl = sys.argv[1]
url = "https://cloudedleopardent.com/game/hajimari/zh/story/{}.html".format(suburl)
converter = opencc.OpenCC('t2s.json')

res = requests.get(url)
bs = BeautifulSoup(res.text,'html.parser')
serif = bs.find_all('div', attrs={'class':'serif'})
name = bs.find_all('div', attrs={'class':'name'})
cv = bs.find_all('div', attrs={'class':'cv'})
intro = bs.find_all('div', attrs={'class':'description'})


with open(suburl +".txt", "a+", encoding="utf-8") as f:
    for i in range(len(serif)):
        serif_s = converter.convert(serif[i].text)
        name_s = converter.convert(name[i].text)
        cv_s = converter.convert(cv[i].text)
        intro_s = converter.convert(intro[i].text)
        f.write('name： '+ name_s)
        f.write(cv_s+'\n')
        f.write('serif: ' + serif_s+'\n')
        f.write('intro: '+ intro_s)
        f.write('\n\n')
    
    f.write("非人物介绍： \n")
    for i in range(len(serif), len(intro)):
        intro_s = converter.convert(intro[i].text)
        f.write(intro_s)
        f.write('\n\n')