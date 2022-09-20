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

    resume_topic_vec = parsed_resume['SkillVector'].scale_to_topic_models()
    print(resume_topic_vec)
    desc_topic_vec = parsed_desc['SkillVector'].scale_to_topic_models()
    print(desc_topic_vec)

    if distance == 'euclidean':
        distance_calc = spatial.distance.euclidean(resume_topic_vec, desc_topic_vec)
    elif distance == 'manhattan':
        print(resume_topic_vec - desc_topic_vec)
        distance_calc = spatial.distance.cityblock(resume_topic_vec, desc_topic_vec)
    elif distance == 'cosine':
        distance_calc = spatial.distance.cosine(resume_topic_vec, desc_topic_vec)

    del parsed_resume['SkillVector']
    del parsed_desc['SkillVector']

    return {
        'comparison_type' : 'resume_job',
        'distance' : distance_calc,
        'resume' : parsed_resume,
        'job' : parsed_desc
    }


def compare_resume_and_soc(
    resume_filepath,
    resume_ext,
    soc_code,
    distance = 'manhattan'
):
    parsed_resume = parse_resume(resume_filepath, resume_ext)
    print(parsed_resume["SkillVector"])

    resume_topic_vec = parsed_resume['SkillVector'].scale_to_topic_models()
    print(resume_topic_vec)
    soc_topic_vec = get_soc_matrix_row(soc_code)
    print(soc_topic_vec)

    if distance == 'euclidean':
        distance_calc = spatial.distance.euclidean(resume_topic_vec, soc_topic_vec)
    elif distance == 'manhattan':
        distance_calc = spatial.distance.cityblock(resume_topic_vec, soc_topic_vec)
        distance_calc = np.absolute(resume_topic_vec - soc_topic_vec).sum()
    elif distance == 'cosine':
        distance_calc = spatial.distance.cosine(resume_topic_vec, soc_topic_vec)

    del parsed_resume['SkillVector']

    return {
        'comparison_type' : 'resume_soc',
        'distance' : distance_calc,
        'resume' : parsed_resume,
        'soc' : soc_code
    }

def compare_job_and_soc(
    job_filepath,
    job_ext,
    soc_code,
    distance = 'manhattan'
):
    parsed_job = parse_job_posting(job_filepath, job_ext)

    job_topic_vec = parsed_job['SkillVector'].scale_to_topic_models()
    soc_topic_vec = get_soc_matrix_row(soc_code)

    if distance == 'euclidean':
        distance_calc = spatial.distance.euclidean(job_topic_vec, soc_topic_vec)
    elif distance == 'manhattan':
        distance_calc = spatial.distance.cityblock(job_topic_vec, soc_topic_vec)
    elif distance == 'cosine':
        distance_calc = spatial.distance.cosine(job_topic_vec, soc_topic_vec)

    del parsed_resume['SkillVector']

    return {
        'comparison_type' : 'job_soc',
        'distance' : distance_calc,
        'job' : parsed_job,
        'soc' : soc_code
    }
