"""
Compare Module

Compares occupational similarity among pairs of job postings,
resumes, and/or Standard Occupational Classification (SOC) codes.
"""

import numpy as np
from scipy import spatial
from sockit.data import get_soc_id, get_soc_skill_matrix, get_soc_title
from sockit.log import Log
from sockit.parse import parse_job_posting, parse_resume
from sockit.skillvector import SkillVector


def _kl(p, q):
    return np.sum(p * np.nan_to_num(np.log(p / q), True, 0, 0, 0))


def compare(source1, type1, source2, type2, similarity="cosine"):
    """ 
    Calculate a similarity score between two sources of type "job", "resume", or "soc".
    """
    error = Log(__name__, "compare").error

    # Parse source 1
    if type1 == "job":
        parsed1 = parse_job_posting(source1)
        v1 = parsed1["SkillVector"].to_tfidf_array()
        del parsed1["SkillVector"]
    elif type1 == "resume":
        parsed1 = parse_resume(source1)
        v1 = parsed1["SkillVector"].to_tfidf_array()
        del parsed1["SkillVector"]
    elif type1 == "soc":
        parsed1 = {
            "soc": source1,
            "soc_title": get_soc_title(source1)
        }
        v1 = get_soc_skill_matrix()[get_soc_id(source1),:]
    else:
        error(f"unknown type1 value '{type1}'")
        return {}

    # Parse source 2
    if type2 == "job":
        parsed2 = parse_job_posting(source2)
        v2 = parsed2["SkillVector"].to_tfidf_array()
        del parsed2["SkillVector"]
    elif type2 == "resume":
        parsed2 = parse_resume(source2)
        v2 = parsed2["SkillVector"].to_tfidf_array()
        del parsed2["SkillVector"]
    elif type2 == "soc":
        parsed2 = {
            "soc": source2,
            "soc_title": get_soc_title(source2)
        }
        v2 = get_soc_skill_matrix()[get_soc_id(source2),:]
    else:
        error(f"unknown type2 value '{type2}'")
        return {}

    # Calculate similarity score
    if similarity == "cosine":
        d = spatial.distance.cosine(v1, v2)
    elif similarity == "euclidean":
        d = spatial.distance.euclidean(v1, v2)
    elif similarity == "manhattan":
        d = spatial.distance.cityblock(v1, v2)
    elif similarity == "kl":
        d = _kl(v1, v2)
    else:
        error(f"unknown similarity measure '{similarity}'")
        return {}

    return {
        "comparison_type"   : f"{type1}-{type2}",
        "similarity_method" : similarity,
        "similarity_score"  : 1 - d,
        "source1"           : parsed1,
        "source2"           : parsed2
    }
