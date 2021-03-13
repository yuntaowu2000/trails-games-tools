import pandas as pd
import random
import json
import os

def parse_json(sheet, output, names):
    values = sheet["抽卡"].to_dict(orient="records")

    for v in values:
        if not str(v["url"]) == "nan" and not v["name"] in names:
            names.add(v["name"])

            star_val = random.randint(0, 5)
            #new_node = {"url": v["url"],"name": v["name"], "star": star_val}
            new_node = {"url": v["url"],"name": v["name"], "star": v["stars"]}

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
    run()