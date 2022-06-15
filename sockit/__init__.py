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
re_paren = re.compile(r"\([^()]*\)")
re_punct = re.compile(r"[\-+/]")
re_alpha = re.compile(r"[^A-Za-z0-9 ]*")

def clean(title):
    """
    Remove text in parentheses, convert some puncuation to spaces,
    and return lowercase alpha-numeric characters and spaces.
    """
    # Remove text after hyphen
    title = title.split(" - ")[0].strip()
    return re_alpha.sub("", re_punct.sub(" ", re_paren.sub("", title))).strip().lower()


def get_wordtrie():
    """
    Lazy-load the WordTrie prefix tree from package data.
    """
    global _data
    if "wordtrie" not in _data:
        Log(__name__, "get_wordtrie").info("loading prefix tree")
        _data["wordtrie"] = WordTrie().from_json(
            resource_filename(__name__, "data/wordtrie.json")
        )
    return _data["wordtrie"]


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


def get_noun_list():
    """
    Lazy-load noun list for matching score.
    """
    global _data
    if "noun_list" not in _data:
        Log(__name__, "get_noun_list").info("loading noun list")
        with open(resource_filename(__name__, "data/noun_list.txt")) as f:
            _data["noun_list"] = f.read()
    return _data["noun_list"]


def search(title,node_match_weight,noun_match_weight):
    """
    Search the (cleaned) job title against the trie
    for matching titles and assign SOC probabilities.
    """
    debug = Log(__name__, "search").debug
    nodes = []
    counts = {}
    for result in get_wordtrie().search(title, return_nodes=True):
        # Keep results that are at least as long as the
        # longest result.
        max_length = 0 if not nodes else nodes[0].count(" ") + 1
        result_length = len(result[0])
        if result_length > max_length:
            nodes = [" ".join(result[0])]
            counts = score(nodes, node_match_weight, noun_match_weight, counts=result[1])
            # counts = result[1]
            counts = result[1]
        elif result_length == max_length:
            # If the length is the same as the longest result,
            # aggregate the results.
            nodes.append(" ".join(result[0]))
            score_adjusted_counts = score(nodes, node_match_weight, noun_match_weight, counts=result[1])
            # counts = _aggregate(counts, result[1])
            counts = _aggregate(counts,score_adjusted_counts)
    debug("found matches:", nodes)
    return counts


# noun_list = frozenset(map(str.strip, open("./sockit/data/noun_list.txt")))
# nodes = ["first", "shift", "data", "engineer"]

def score(nodes, node_match_weight, noun_match_weight, counts):
    """
    Score each node for whether it is in the
    noun list or not.
    """
    score = 0
    for word in nodes:
        if word in get_noun_list():
            score += noun_match_weight
        else:
            score += node_match_weight
    
    score_adjusted_counts = dict()
    for key,value in counts.items():
        score_adjusted_counts[key] = value*score
    return score_adjusted_counts


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
