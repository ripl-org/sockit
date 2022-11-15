import csv
import json 
import numpy as np
from importlib import resources
from sockit.log import Log
from wordtrie import WordTrie


DATA = {}


def get_index(name):
    """
    Lazy-load an index from package data.
    """
    global DATA
    names = frozenset((
        "skill",
        "soc"
    ))
    if name not in names:
        Log(__name__, "get_index").error(f"unknown index '{name}'")
        return None
    key = f"sockit.data.index_{name}"
    if key not in DATA:
        Log(__name__, "get_lookup").debug(f"loading lookup '{name}'")
        DATA[key] = {"id": {}, "value": {}}
        with resources.open_text("sockit.data", f"index_{name}s.csv") as f:
            for row in csv.DictReader(f):
                DATA[key]["id"][int(row[f"{name}_id"])] = row[name]
                DATA[key]["value"][row[name]] = int(row[f"{name}_id"])
    return DATA[key]


def get_lookup(name):
    """
    Lazy-load a lookup table from package data.
    """
    global DATA
    names = frozenset((
        "abbreviations",
        "acronyms",
        "resume_headers",
        "soc_titles"
    ))
    if name not in names:
        Log(__name__, "get_lookup").error(f"unknown lookup '{name}'")
        return None
    key = f"sockit.data.lookup_{name}"
    if key not in DATA:
        Log(__name__, "get_lookup").debug(f"loading lookup '{name}'")
        with resources.open_text("sockit.data", f"lookup_{name}.json") as f:
            DATA[key] = json.load(f)
    return DATA[key]


def get_set(name):
    """
    Lazy-load a set from package data.
    """
    global DATA
    names = frozenset((
        "job_title_nouns"
    ))
    key = f"sockit.data.set_{name}"
    if key not in DATA:
        Log(__name__, "get_set").debug(f"loading set '{name}'")
        with resources.path("sockit.data", f"set_{name}.txt") as f:
            DATA[key] = frozenset(item.strip() for item in open(f).readlines())
    return DATA[key]   


def get_skill(j):
    """
    Get the skill keyword associated with column j in the SOC-skill matrix.
    """
    return get_index("skill")["id"][i]


def get_skill_id(skill):
    """
    Get the column ID associated with `skill` in the SOC-skill matrix.
    """
    return get_index("skill")["value"][skill]


def get_skill_idf_vector():
    """
    Lazy-load the skill IDF vector from package data.
    """
    global DATA
    key = "sockit.data.vector_skill_idf"
    if key not in DATA:
        Log(__name__, "get_skill_idf_vector").debug("loading skill IDF vector")
        with resources.path("sockit.data", "vector_skill_idf.txt") as f:
            DATA[key] = np.loadtxt(f)
    return DATA[key]


def get_soc(i):
    """
    Get the SOC code associated with row i in the SOC-skill matrix.
    """
    return get_index("soc")["id"][i]


def get_soc_id(soc):
    """
    Get the row ID associated with `soc` in the SOC-skill matrix.
    """
    return get_index("soc")["value"][str(soc)]


def get_soc_skill_matrix():
    """
    Lazy-load the SOC-skill matrix from package data.
    """
    global DATA
    key = "sockit.data.matrix_soc_skill"
    if key not in DATA:
        Log(__name__, "get_soc_skill_matrix").debug("loading SOC-skill matrix")
        with resources.path("sockit.data", "matrix_soc_skill.txt") as f:
            DATA[key] = np.loadtxt(f) * 1e-6
    return DATA[key]


def get_soc_title(soc):
    """
    Lazy-load SOC titles and lookup the title for a SOC code.
    """
    return get_lookup("soc_titles")[str(soc)]


def get_trie(name):
    """
    Lazy-load a trie (prefix tree) from package data.
    """
    global DATA
    names = frozenset((
        "alternative_titles",
        "degrees",
        "fields_of_study",
        "job_titles",
        "job_titles_override",
        "nonskills",
        "schools",
        "skills"
    ))
    if name not in names:
        Log(__name__, "get_trie").error(f"unknown trie '{name}'")
        return None
    key = f"sockit.data.trie_{name}"
    if key not in DATA:
        Log(__name__, "get_trie").debug(f"loading trie '{name}'")
        with resources.path("sockit.data", f"trie_{name}.json") as f:
            DATA[key] = WordTrie().from_json(f)
    return DATA[key]
