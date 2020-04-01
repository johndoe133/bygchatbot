import json

with open('beats.json') as json_file:
    json_obj = json.load(json_file)

json_formatted_str = json.dumps(json_obj, indent=2)

# print(json_obj[0]['segments'][0]['id'])

# print(json_formatted_str)

# print(json_obj[0]['name'])
