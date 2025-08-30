import requests

data = {"score": 12}
response = requests.post("http://127.0.0.1:5000/predict", json=data)

print(response.json())