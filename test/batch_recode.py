import json
from sockit.title import clean, sort, search
import csv

input_file = csv.reader(open('test/hardcode.csv', encoding='utf-8-sig'))
next(input_file)

in_trie = 'sockit/data/titles_trie_old.json'
with open(in_trie) as f:
    titles = json.load(f)

in_trie = 'sockit/data/managers_trie_old.json'
with open(in_trie) as f:
    mgr = json.load(f)

for item in input_file:       
    title = item[0]
    new_soc = item[1]
    print(new_soc)
    clean_title = clean(title).split()[::-1]
    if clean_title[0] in ['manager']:
        subtrie_string = "mgr"
        for manager in ['manager', 'supervisor', 'coordinator', 'director', 'vp', 'president']:
            clean_title[0] = manager
            for i in range(len(clean_title)):
                subtrie_string = subtrie_string + f'[clean_title[{i}]]'
            try:
                exec(subtrie_string + "= {'#': {f'{new_soc}':1}}")
            except:
                pass
    else:
        subtrie_string = "titles"
        for i in range(len(clean_title)):
            subtrie_string = subtrie_string + f'[clean_title[{i}]]'
        exec(subtrie_string + "= {'#': {f'{new_soc}':1}}")

out_trie = 'sockit/data/titles_trie.json'
with open(out_trie, 'w') as f:
    json.dump(titles, f)

out_trie = 'sockit/data/managers_trie.json'
with open(out_trie, 'w') as f:
    json.dump(mgr, f)