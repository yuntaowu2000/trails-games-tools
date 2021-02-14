import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://trails-game.com/characters_sen/"

res = requests.get(url)
bs = BeautifulSoup(res.text,'html.parser')

refs = bs.find_all("a")

name_to_link = {}

for r in refs:
    keys = r.attrs.keys()
    if "title" in keys:
        link = r.attrs['href']
        title = r.attrs['title']
        name_to_link[title] = link


file="relation.xls"

sheet = pd.read_excel(file, None)

#name sheet processing
values = sheet["角色"].to_dict(orient="records")

name_as_keys = name_to_link.keys()
for v in values:
    if (v["name"] in name_as_keys and str(v["wikiPage"]) == "nan"):
        v["wikiPage"] = name_to_link[v["name"]]



