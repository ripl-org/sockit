#THIRD PARTY LIBRARIES
from scipy import spatial

#CUSTOM FILES
from sockit.asciitrans import *
from sockit.re import *
from sockit.data import *
from sockit.parse import *
from sockit.skillvector import SkillVector

def compare_resume_and_description(
    resume_filepath,
    resume_ext,
    description_filepath,
    description_ext,
    distance = 'manhattan'
):
    """ 
    Find the similarity score between two SOC codes
    """
    parsed_resume = parse_resume(resume_filepath, resume_ext)
    parsed_desc = parse_job_posting(description_filepath, description_ext)

    resume_tfidf = parsed_resume['SkillVector'].to_weighted_vector()
    desc_tfidf = parsed_desc['SkillVector'].to_weighted_vector()

    resume_topic_vec = parsed_resume['SkillVector'].scale_to_topic_models().reshape(1,50)
    desc_topic_vec = parsed_desc['SkillVector'].scale_to_topic_models().reshape(1,50)

    if distance == 'euclidean':
        distance_calc = spatial.distance.euclidean(resume_topic_vec, desc_topic_vec)
    elif distance == 'manhattan':
        distance_calc = spatial.distance.cityblock(resume_topic_vec, desc_topic_vec)
    elif distance == 'cosine':
        distance_calc = spatial.distance.cosine(resume_topic_vec, desc_topic_vec)

    del parsed_resume['SkillVector']
    del parsed_desc['SkillVector']

    return {
        'comparison_type' : 'job_description',
        'distance' : distance_calc,
        'resume' : parsed_resume,
        'job_description' : parsed_desc
    }


def compare_resume_and_soc(
    resume_filepath,
    resume_ext,
    soc_code,
    distance = 'manhattan'
):
    parsed_resume = parse_resume(resume_filepath, resume_ext)
    

    resume_topic_vec = parsed_resume['SkillVector'].scale_to_topic_models().reshape(1,50)
    soc_topic_vec = get_soc_matrix_row(soc_code)

    if distance == 'euclidean':
        distance_calc = spatial.distance.euclidean(resume_topic_vec, soc_topic_vec)
    elif distance == 'manhattan':
        distance_calc = spatial.distance.cityblock(resume_topic_vec, soc_topic_vec)
    elif distance == 'cosine':
        distance_calc = spatial.distance.cosine(resume_topic_vec, soc_topic_vec)

    del parsed_resume['SkillVector']

    return {
        'comparison_type' : 'soc_code',
        'distance' : distance_calc,
        'resume' : parsed_resume,
        'soc_code' : soc_code
    }
