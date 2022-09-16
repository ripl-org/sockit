"""
Sockit: assign probabilistic Standard Occupational Classification (SOC)
codes to free-text job titles

https://github.com/ripl-org/sockit
"""

import json
import re
from importlib import resources
from .log import Log
from pkg_resources import resource_filename
from wordtrie import WordTrie

__version__ = resources.read_text(__name__, "VERSION").strip()


### Internal data and functions ###

_data = {}

def _aggregate(old, new):
    """
    Aggregate two dictionaries of SOC/value items.
    """
    value = {}
    for soc in new:
        value[soc] = new[soc] + old.get(soc, 0)
    for soc in old:
        if soc not in value:
            value[soc] = old[soc]
    return value


### Exported data and functions ###

# Regular expressions for title cleaning
re_tokenize = re.compile(r"[^a-zA-Z\d\s\,\&/]")
re_alpha = re.compile(r"[^A-Za-z]")
stopwords = frozenset(["pt", "nd", "st", "sr", "jr", "i", "ii", "iii"])
levels = frozenset(['senior', 'associate', 'assistant', 'principal', 'lead'])

def clean(title):
    """
    Remove extraneous text from the title and convert to lowercase
    alphabetical characters without puncuation.
    Reorder around prepositional phrases so that the principal
    noun ends the title, e.g.:
    "Director of Reseach" to "research director"
    "Teacher for Special Needs" to "special needs teacher"
    "Assistant to the CEO" to "the ceo assistant"
    """
    # Split on anything that's not a letter, comma or &
    # Grab the first token
    tokens = re_tokenize.split(title)
            
    # If there's only one word before the split, grab one more token
    if len(tokens[0].split()) == 1:
        title = " ".join(tokens[:2])
    else:
        title = tokens[0]
            
    # Get rid of any non alpha characters
    title = re_alpha.sub(" ", title).lower()
            
    # Remove common misleading words like 'pt'
    title = " ".join([word for word in title.split() if word not in stopwords])
            
    # Reorder prepositional phrases
    suffix, _, prefix = title.partition(" of ")
    title = f"{prefix} {suffix}".strip()
    suffix, _, prefix = title.partition(" for ")
    title = f"{prefix} {suffix}".strip()
    suffix, _, prefix = title.partition(" to ")
    title = f"{prefix} {suffix}".strip()

    # Get rid of levels
    if len(title.split()) > 1:
        if any(item in title.split()[:-1] for item in levels):
            title = " ".join([word for word in title.split()[:-1] if word not in levels] + [title.split()[-1]])

    return title


def get_abbreviations():
    """
    Lazy-load the abbreviations dictionary from package data.
    """
    global _data
    if "abbreviations" not in _data:
        Log(__name__, "get_abbreviations").info("loading abbreviations dictionary")
        with open(resource_filename(__name__, "data/abbreviations.json")) as f:
            _data["abbreviations"] = json.load(f)
    return _data["abbreviations"]


def get_acronyms():
    """
    Lazy-load the acronyms dictionary from package data.
    """
    global _data
    if "acronyms" not in _data:
        Log(__name__, "get_acronyms").info("loading acronyms dictionary")
        with open(resource_filename(__name__, "data/acronyms.json")) as f:
            _data["acronyms"] = json.load(f)
    return _data["acronyms"]


def get_managers():
    """
    Lazy-load the managers dictionary from package data.
    """
    global _data
    if "managers" not in _data:
        Log(__name__, "get_managers").info("loading managers prefix tree")
        _data["managers"] = WordTrie().from_json(
            resource_filename(__name__, "data/managers.trie")
        )
    return _data["managers"]


def get_titles():
    """
    Lazy-load the WordTrie prefix tree from package data.
    """
    global _data
    if "titles" not in _data:
        Log(__name__, "get_wordtrie").info("loading titles prefix tree")
        _data["titles"] = WordTrie().from_json(
            resource_filename(__name__, "data/titles.trie")
        )
    return _data["titles"]


def get_soc_title(soc):
    """
    Lazy-load SOC titles and lookup the title for a SOC code.
    """
    global _data
    if "soc_titles" not in _data:
        Log(__name__, "get_soc_title").info("loading SOC titles")
        with open(resource_filename(__name__, "data/soc_titles.json")) as f:
            _data["soc_titles"] = json.load(f)
    return _data["soc_titles"].get(soc)


def search(title):
    """
    Search the (cleaned) job title against the trie
    for matching titles and assign SOC probabilities.
    """
    debug = Log(__name__, "search").debug
    abbreviations = get_abbreviations()
    acronyms = get_acronyms()
    words = title.split()[::-1]
    for i, word in enumerate(words):
        if word in acronyms:
            debug("found exact acronym match:", word)
            return {acronyms[word]: 1}
        if word in abbreviations:
            words[i] = abbreviations[word]
    # Try manager titles first
    for result in get_managers().search(words, return_nodes=True):
        debug("found exact manager title match:", " ".join(result[0]))
        return result[1]
    for result in get_titles().search(words, return_nodes=True):
        debug("found title match:", " ".join(result[0]))
        return result[1]
    return {}


def sort(counts):
    """
    Sort search results by descending probability and
    add SOC titles. Return a list of dicts.
    """
    norm = 1.0 / sum(counts.values()) if counts else 0
    return [
        {"soc": soc, "prob": norm * counts[soc], "title": get_soc_title(soc)}
        for soc in sorted(counts, key=counts.get, reverse=True)
    ]


def batch_search(titles):
    """
    Search an iterator of (cleaned) job titles against
    the trie and yield SOC probabilities for each one.
    """
    for title in titles:
        yield search(title)
