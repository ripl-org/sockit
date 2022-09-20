import csv
import json 
import numpy as np
from importlib import resources
from sockit.log import Log
from wordtrie import WordTrie

DATA_MODULE = 'sockit.data'

SOC_TRIES = {}
DATA = {}

def create_mapping():
    global DATA
    if 'skill_mapping' in DATA:
        return DATA['skill_mapping']

    Log(__name__, "get_skill_mapping").info("loading skill mapping")
    mapping = {}
    with resources.open_text(DATA_MODULE, 'skills.csv') as f:
        csvfile = csv.DictReader(f)
        for row in csvfile:
            mapping[int(row['skill_id'])] = row['skill']
    DATA['skill_mapping'] = mapping
    return mapping


def create_soc_mapping():
    global DATA
    if 'soc_mapping' not in DATA:
        Log(__name__, "get_soc_mapping").info("loading soc mapping")
        mapping = {}
        with resources.open_text(DATA_MODULE, "socs.csv") as f:
            csvfile = csv.DictReader(f)
            for row in csvfile:
                mapping[row['soc']] = int(row['soc_id'])
        DATA['soc_mapping'] = mapping
    return DATA['soc_mapping']


def create_idf_vector():
    global DATA
    if 'idf_vector' not in DATA:
        Log(__name__, "get_idf_vector").info("loading idf vector")
        with resources.open_text(DATA_MODULE, 'skill_idf_vector.txt') as file:
            DATA['idf_vector'] = np.loadtxt(file) * 1e-3
    return np.array(DATA['idf_vector'])


def create_soc_topic_matrix():
    global DATA
    if 'soc_topic' not in DATA:
        Log(__name__, "get_soc_topic_matrix").info("loading soc topic matrix")
        with resources.path(DATA_MODULE, 'soc_topic_matrix.txt') as file:
            DATA['soc_topic'] = np.loadtxt(file) * 1e-6
    return DATA['soc_topic']


def create_topic_skill_matrix():
    global DATA
    if 'topic_skill' not in DATA:
        Log(__name__, "get_skill_topic_matrix").info("loading topic skill matrix")
        with resources.path(DATA_MODULE, 'topic_skill_matrix.txt') as file:
            DATA['topic_skill'] = np.loadtxt(file) * 1e-6
    return DATA['topic_skill']


def load_word_trie(name):
    global SOC_TRIES
    word_trie_mapping = {
        'degrees' : 'degrees.json',
        'schools' : 'schools.json',
        'socs' : 'socs.json',
        'skills' : 'skills.json',
        'nonskills' : 'nonskills.json',
        'fields_of_study' : 'fields_of_study.json',
        'titles' : 'job_titles.json'
    }
    if name not in SOC_TRIES:
        with resources.path(DATA_MODULE, word_trie_mapping[name]) as file:
            SOC_TRIES[name] = WordTrie().from_json(file)


def load_data(name):
    global DATA
    data_mapping = {
        'headers' : 'resume_headers.json'
    }
    if name not in DATA:
        with open(resources.path(DATA_MODULE, data_mapping[name])) as file:
            DATA[name] = json.load(file)


def get_abbreviations():
    """
    Lazy-load the abbreviations dictionary from package data.
    """
    global DATA
    if "abbreviations" not in DATA:
        Log(__name__, "load_abbreviations").info("loading abbreviations")
        with resources.open_text(DATA_MODULE, 'abbreviations.json') as f:
            DATA['abbreviations'] = json.load(f)
    return DATA['abbreviations']


def get_acronyms():
    """
    Lazy-load the acronyms dictionary from package data.
    """
    global DATA
    if "acronyms" not in DATA:
        Log(__name__, "load_acronyms").info("loading acronyms")
        with resources.open_text(DATA_MODULE, 'acronyms.json') as f:
            DATA['acronyms'] = json.load(f)
    return DATA['acronyms']


def get_managers():
    """
    Lazy-load the managers prefix tree from package data.
    """
    global DATA
    if "managers" not in DATA:
        Log(__name__, "load_managers").info("loading managers")
        with resources.path(DATA_MODULE, 'managers_trie.json') as f:
            DATA['managers'] = WordTrie().from_json(f)
    return DATA['managers']


def get_titles():
    """
    Lazy-load the titles prefix tree from package data.
    """
    global DATA
    if "titles" not in DATA:
        Log(__name__, "load_titles").info("loading titles")
        with resources.path(DATA_MODULE, 'titles_trie.json') as f:
            DATA['titles'] = WordTrie().from_json(f)
    return DATA['titles']


def get_soc(i):
    """
    Get the SOC code associated with index i in the SOC/topic matrix.
    """
    global DATA
    if "socs" not in DATA:
        Log(__name__, "get_soc").info("loading SOC codes")
        with resources.open_text(DATA_MODULE, 'socs.csv') as f:
            DATA["socs"] = [row["soc"] for row in csv.DictReader(f)]
    return DATA["socs"][i]


def get_soc_title(soc):
    """
    Lazy-load SOC titles and lookup the title for a SOC code.
    """
    global DATA
    if "soc_titles" not in DATA:
        Log(__name__, "load_soc_titles").info("loading soc titles")
        with resources.open_text(DATA_MODULE, 'soc_titles.json') as f:
            DATA['soc_titles'] = json.load(f)
    return DATA['soc_titles'][soc]


def get_soc_matrix_row(soc):
    global DATA
    mapping = create_soc_mapping()
    if str(soc) not in mapping.keys():
        raise Exception(f'{soc} is an invalid SOC code')
    
    if 'soc_topic_matrix' not in DATA:
        Log(__name__, "load_soc_matrix").info("loading soc topic matrix")
        with resources.path(DATA_MODULE, "soc_topic_matrix.txt") as f:
            soc_topic = np.loadtxt(f)  * 1e-6
            DATA['soc_topic_matrix'] = soc_topic

    return DATA['soc_topic_matrix'][mapping[str(soc)],:].reshape(1,50)

