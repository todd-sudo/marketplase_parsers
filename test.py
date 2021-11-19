import json


with open("/home/todd/big.json") as file:
    objects = json.load(file)

print(len(objects))
