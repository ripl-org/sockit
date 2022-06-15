# Compare scores to correct 

import pandas as pd
import json
import os

#  C:\Repos\sockit> python3 sockit -i "C:\Repos\sockit\test\test.json" --score 1 10 -o "C:\Repos\sockit\results\node0_noun10.json"

matching_dir = "C://Users/MarcelleGoggins/Research Improving People's Lives/RIPL All Staff - Documents/Data/Private/NASWA/sockit_testing/matchingscore/"

# test data from Karen with correct SOCs
test_file = "C://Repos/sockit/test/test.json"
f=open(test_file)
test_data = json.load(f)

node1_noun1 = pd.DataFrame()
index = 1
with open(matching_dir+'node1_noun1.json', "r") as ins:
    for line in ins:
        data = {} 
        data = line 
        data_dict = json.loads(data)
        data_dict['sockit_soc'] = (data_dict['socs'][0]['soc'][:2] + "-" + data_dict['socs'][0]['soc'][2:])
        if data_dict['sockit_soc'] in test_data[index-1]['SOC6']:
            data_dict['correct_soc6'] = 1
        else:
            data_dict['correct_soc6'] = 0
        data_dict['sockit_prob'] = data_dict['socs'][0]['prob']
        data_dict['sockit_title'] = data_dict['socs'][0]['title']
        data_dict['type'] = 'node1_noun1'
        del data_dict['socs']
        temp = pd.DataFrame(data_dict,index=[index])
        node1_noun1 = node1_noun1.append(temp)
        index+=1
        

data = [node0_noun1,node1_noun2,node1_noun5,node1_noun1]

## Results 
for df in [node0_noun1,node1_noun2,node1_noun5,node1_noun1]:
    print(f"% of correct SOC6 in {df}:", df.correct_soc6.sum()/107)


sc = 2
dict = {'112022': 53, '111021': 140, '111011': 175, '113031': 100}
new_dict = {}
for k,v in dict.items():
    new_dict[k] = v*sc

