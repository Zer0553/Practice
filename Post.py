import requests
import json

data = {"Name": "Магнит", "City": "Самара", "Street": "Рабочая", "House": 45, "Open_Time": 800, "Close_Time": 2200}

Shop = json.dumps(data)

response = requests.post("http://127.0.0.1:8000/shop", data=Shop)
print(response.text)