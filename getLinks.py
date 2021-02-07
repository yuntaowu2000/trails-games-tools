import requests

base_url = "https://trails-game.com/wp-json/wp/v2/search"

result = requests.get(base_url, 
        params={"type":"post", 
        "subtype": "map",
        "per_page": "100"})

id_name_map = {}

responseJson = result.json()

for j in responseJson:
    id_name_map[j["title"]] = j["id"]

print(id_name_map)