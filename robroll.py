import pandas as pd
import requests
import threading
import json
import os

def request_header(v, failed_links):
    result = requests.head(str(v["url"]))
    if result.status_code != 200:
        failed_links[v["name"]] = str(v["url"])

def test_header(sheet, failed_links):
    values = sheet["抽卡"].to_dict(orient="records")
    thread_list = []
    for v in values:
        if str(v["url"]) == "nan":
            failed_links[v["name"]] = str(v["url"])
            continue
        t = threading.Thread(target=lambda:request_header(v, failed_links))
        thread_list.append(t)
        t.start()

    for t in thread_list:
        t.join()
    print(failed_links)


def parse_json(sheet, output, names):
    values = sheet["抽卡"].to_dict(orient="records")

    for v in values:
        if not str(v["url"]) == "nan" and not v["name"] in names:
            names.add(v["name"])

            # star_val = random.randint(0, 5)
            # new_node = {"url": v["url"],"name": v["name"], "star": star_val}
            new_node = {"url": v["url"],"name": v["name"], "star": v["star"]}

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

    parse_json(sheet, output, names)

    for t in thread_list:
        t.join()
    write_outputs(output)

if __name__ == "__main__":
    #failed_links = {}
    #file = os.path.join(os.getcwd(), "relation.xlsx")
    #sheet = pd.read_excel(file, None)

    #test_header(sheet, failed_links)
    run()