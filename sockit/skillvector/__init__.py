import numpy as np 
from sockit.data import *

MAPPING = create_mapping()
IDF_VECTOR = create_idf_vector()
TOPIC_SKILL_VEC = create_skill_topic_vector()

class SkillVector:
    #MAGIC FUNCTIONS
    def __init__(self, skill_dict = {}, skill_list = []):
        self.skill_counter = skill_dict
        if len(skill_list) >= 1:
            for skill in skill_list:
                self += skill

    def __repr__(self):
        return str(self.skill_counter)

    def __str__(self):
        return str(self.skill_counter)

    def __len__(self):
        return len([skill for skill in self.skill_counter.keys() if self.skill_counter[skill] >= 1])

    def __add__(self, skill):
        if type(skill) == int:
            skill = MAPPING.get(skill, None)
        if skill == None:
            raise Exception('Skill does not exist in mapping')
        if skill not in self.skill_counter:
            self.skill_counter[skill] = 0
        self.skill_counter[skill] += 1
        return self

    def __iadd__(self, skill):
        if type(skill) == int:
            skill = MAPPING.get(skill, None)
        if skill == None:
            raise Exception('Skill does not exist in mapping')
        if skill not in self.skill_counter:
            self.skill_counter[skill] = 0
        self.skill_counter[skill] += 1
        return self

    def __getitem__(self, skill):
        if type(skill) == int:
            skill = MAPPING.get(skill, None)
        return self.skill_counter.get(skill, 0)

    def __setitem__(self, skill, value):
        if type(skill) == int:
            skill = MAPPING.get(skill, None)
        if skill == None:
            raise Exception('Skill does not exist in mapping.')
        self.skill_counter[skill] = value

    def __delitem__(self, skill):
        del self.skill_counter[skill]

    def __iter__(self):
        for skill, count in sorted(self.skill_counter.items(), key = lambda x: x[1], reverse = True):
            yield (skill, count)

    def __contains__(self, skill):
        return skill in self.skill_counter

    #NON-MAGIC FUNCTIONS
    def clear(self):
        self.skill_counter = {}

    def copy(self):
        new_dict = {k : v for k, v in self.skill_counter.items()}
        new_skill_vector = SkillVector(skill_dict = new_dict)
        return new_skill_vector

    def get(self, skill, default = None):
        if type(skill) == int:
            skill = MAPPING.get(skill, None)
        return self.skill_counter.get(skill, default)

    def items(self):
        return [(k, v) for k, v in self.skill_counter.items()]

    def keys(self):
        return [k for k in self.skill_counter.keys()]

    def pop(self, skill, default = None):
        if skill in self.skill_counter:
            value = self.skill_counter[skill]
            del self.skill_counter[skill]
            return value
        return default

    def to_array(self):
        return np.array(
            [self.get(x,0) for x in sorted(list(MAPPING.keys()))]
        )

    def to_weighted_vector(self):
        x = self.to_array()
        return np.multiply(x, IDF_VECTOR)


    def scale_to_topic_models(self):
    	x = self.to_weighted_vector().reshape(775,1)
    	return np.matmul(TOPIC_SKILL_VEC, x)