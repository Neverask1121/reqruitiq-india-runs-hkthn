import json

file_path = "../../dataset/candidates.jsonl"

with open(file_path, "r", encoding="utf-8") as file:
    first_candidate = json.loads(file.readline())

print(type(first_candidate))
for key in first_candidate:
    print(key, type(first_candidate[key]))

print("\nProfile Fields\n")

for key in first_candidate["profile"]:
    print("-", key)

print("\nRedRob Signals\n")

for key in first_candidate["redrob_signals"]:
    print("-", key)

print(first_candidate["skills"][0])


for key in first_candidate["career_history"][0]:
    print(key)