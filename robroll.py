import pandas as pd
import random
import json
import threading
import requests
import os

SEARCH_URL = "https://trails-game.com/wp-json/wp/v2/search"
BASE_URL = "https://trails-game.com/?p="

def search_for_link(name, new_node):
    retval = BASE_URL + "1355"

    result = requests.get(SEARCH_URL, 
        params={"type":"post", 
        "subtype": "dt_team", 
        "per_page":"1",
        "search": name})

    if result is None:
        response_json = result.json()
        if len(response_json) > 0:
            retval = response_json[0]["url"]
    
    new_node["url"] = retval

def parse_json(sheet, output, names, thread_list):
    values = sheet["角色"].to_dict(orient="records")

    for v in values:
        if v["type"] == "Char" and not v["name"] in names:
            names.add(v["name"])

            star_val = random.randint(0, 6)
            new_node = {"name": v["name"], "star": star_val}

            if (str(v["postid"]) != "nan"):
                new_node["url"] = BASE_URL + str(int(v["postid"]))
            else: 
                t = threading.Thread(target=search_for_link, args=(v["name"], new_node))
                thread_list.append(t)
                t.start()

            output.append(new_node)

def write_outputs(output):
    target_file = os.path.join(os.getcwd(), "data.json")
    with open(target_file, "w") as f:
        output = json.dumps(output, sort_keys=True, indent=4, ensure_ascii=False)
        print(output)
        f.write(output)
        f.flush()

def run():
    file = os.path.join(os.getcwd(), "relation.xlsx")

    names = set()
    output = []
    thread_list = []

    sheet = pd.read_excel(file, None)

    parse_json(sheet, output, names, thread_list)

    for t in thread_list:
        t.join()
    write_outputs(output)

if __name__ == "__main__":
    run()