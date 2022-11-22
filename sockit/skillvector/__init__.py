import numpy as np
from scipy import spatial
from sockit.data import (
    get_index, get_skill_idf_vector,
    get_soc, get_soc4, get_soc4_model, get_soc_skill_matrix,
    get_soc_title, get_soc4_title)


class SkillVector:

    def __init__(self, skill_dictionary={}, skill_list=[]):
        self.index = get_index("skill")["id"]
        self.skill_counter = {}
        if len(skill_list) >= 1:
            for skill in skill_list:
                self += skill 
        else:
            self.skill_counter = skill_dictionary
        if len(self.skill_counter) == 0:
            raise Exception("SkillVector cannot be empty")

    def __repr__(self):
        return str(self.skill_counter)

    def __str__(self):
        return str(self.skill_counter)

    def __len__(self):
        return len([skill for skill in self.skill_counter.keys() if self.skill_counter[skill] >= 1])

    def __add__(self, skill):
        if type(skill) == int:
            skill = self.index.get(skill, None)
        if skill == None:
            raise Exception('Skill does not exist in mapping')
        if skill not in self.skill_counter:
            self.skill_counter[skill] = 0
        self.skill_counter[skill] += 1
        return self

    def __iadd__(self, skill):
        if type(skill) == int:
            skill = self.index.get(skill, None)
        if skill == None:
            raise Exception('Skill does not exist in mapping')
        if skill not in self.skill_counter:
            self.skill_counter[skill] = 0
        self.skill_counter[skill] += 1
        return self

    def __getitem__(self, skill):
        if type(skill) == int:
            skill = self.index.get(skill, None)
        return self.skill_counter.get(skill, 0)

    def __setitem__(self, skill, value):
        if type(skill) == int:
            skill = self.index.get(skill, None)
        if skill == None:
            raise Exception('Skill does not exist in mapping.')
        self.skill_counter[skill] = value

    def __delitem__(self, skill):
        del self.skill_counter[skill]

    def __iter__(self):
        for skill, count in sorted(self.skill_counter.items(), key=lambda x: x[1], reverse=True):
            yield (skill, count)

    def __contains__(self, skill):
        return skill in self.skill_counter

    def clear(self):
        self.skill_counter = {}

    def copy(self):
        return SkillVector(skill_dict={k : v for k, v in self.skill_counter.items()})

    def get(self, skill, default=None):
        if type(skill) == int:
            skill = self.index.get(skill, None)
        return self.skill_counter.get(skill, default)

    def items(self):
        return [(k, v) for k, v in self.skill_counter.items()]

    def keys(self):
        return [k for k in self.skill_counter.keys()]

    def pop(self, skill, default=None):
        if skill in self.skill_counter:
            value = self.skill_counter[skill]
            del self.skill_counter[skill]
            return value
        return default

    def to_array(self):
        return np.array(
            [self.get(x, 0) for x in sorted(list(self.index.keys()))]
        )

    def to_tfidf_array(self):
        x = self.to_array()
        return np.multiply(x, get_skill_idf_vector()) / x.sum()

    def rank_socs(self, n=1):
        x = self.to_tfidf_array()
        X = get_soc_skill_matrix()
        d = [spatial.distance.cosine(X[i,:], x) for i in range(X.shape[0])]
        return [
            {
                "soc"               : get_soc(i),
                "soc_title"         : get_soc_title(get_soc(i)),
                "similarity_method" : "cosine",
                "similarity_score"  : 1 - d[i]
            }
            for i in np.argsort(d)[:n]
        ]

    def predict_socs(self, n=1):
        x = self.to_array()
        model = get_soc4_model()
        p = model.predict(x.reshape(1, len(x)), num_iteration=model.best_iteration)[0]
        return [
            {
                "soc4"        : get_soc4(i),
                "soc4_title"  : get_soc4_title(get_soc4(i)),
                "probability" : p[i]
            }
            for i in np.argsort(p)[::-1][:n]
        ]
