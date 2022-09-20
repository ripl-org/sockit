#STANDARD LIBRARIES
import time
from collections import defaultdict
from itertools import chain

#THIRD PARTY LIBRARIES
import chardet
import docx2txt
from html2text import HTML2Text
from PyPDF2 import PdfReader

from sockit.asciitrans import *
from sockit.data import *
from sockit.re import *
from sockit.skillvector import SkillVector

MIN_YEAR = 1940
MAX_YEAR = int(time.strftime("%Y"))

HTML_PARSER = HTML2Text()
HTML_PARSER.ignore_links = True
HTML_PARSER.ignore_anchors = True
HTML_PARSER.ignore_images = True
HTML_PARSER.ignore_emphasis = True
HTML_PARSER.ignore_tables = True


def split_sentences(text):
    """
    Require at least two letters/numbers before a period
    to avoid splitting on acronyms/abbreviations.
    """
    return re_newline.sub("\\1\n", text.strip()).split("\n")


def find_years(text):
    """
    Find all years that fall within the range [MIN_YEAR, MAX_YEAR].
    """
    return sorted(set(
        y for y in map(int, re_year.findall(text))
        if MIN_YEAR <= y and y <= MAX_YEAR
    ))


def find_year_months(text):
    """
    Find all year-months, searching over multiple formats.
    """
    year_months = set()
    for pattern, formatter in re_year_month:
        year_months.update(map(formatter, pattern.findall(text)))
    return sorted(year_months)


def clean(text):
    """
    Convert some puncuation to spaces, and return alpha-numeric
    characters, spaces and periods.
    """
    return re_alphanum.sub("", re_punct.sub(" ", text.lower())).strip()


def decode_ascii(text):
    """
    Automatically detect the encoding of a byte string with chardet,
    decode the string, transliterate non-ASCII characters, and return
    an ASCII string.
    """
    detect = chardet.detect(text)
    encoding = detect["encoding"] if detect["confidence"] > 0.8 else "utf8"
    return text.decode(encoding, errors="ignore").translate(asciitrans)


def pdf_bytes(filename):
    """
    Extract a byte string from a PDF document using the PyPDF library
    """
    reader = PdfReader(filename)
    num_pages = len(reader.pages)
    return bytes(' '.join([
        reader.pages[x].extract_text() for x in range(num_pages)
    ]), 'utf-8')


def html_bytes(filename):
    """
    Extract a byte string from an HTML document using html2text
    """
    text = open(filename).read()
    return bytes(HTML_PARSER.handle(text), "utf-8")


def extract(filename, extension):
    """
    Extract ASCII text from a PDF, doc, docx, or text file
    (based on the extension) and return as a list of lines.
    """
    extension = extension.split(".")[-1]
    if extension == "pdf":
        text = pdf_bytes(filename)
    elif extension == "docx":
        text = docx2txt.process(filename).encode("utf8")
    elif extension == 'html':
        text = html_bytes(filename)
    else:
        with open(filename, "rb") as f:
            text = f.read()
    return decode_ascii(text).splitlines()


def segment(lines):
    """
    Identify resume section headers and segment lines by section.
    """
    load_data('headers')
    segments = defaultdict(list)
    current = "contact"
    for line in lines:
        line = clean(line)
        if line:
            # Test if the line begins with a one or two word section header
            header = line.replace(".", "").split()
            # Ignore lines with more than 2 words
            if len(header) > 2:
                header = []
            # Try two-word phrase first
            if len(header) > 1 and header[0] + " " + header[1] in DATA['headers']:
                current = DATA['headers'][header[0] + " " + header[1]]
                # Keep text that follows the header
                if len(header) > 2:
                    segments[current].append(header[2])
            # Try single words next
            elif header and header[0] in DATA['headers']:
                current = DATA['headers'][header[0]]
                # Keep text that follows the header
                if len(header) > 1:
                    segments[current].append(" ".join(header[1:]))
            # No header found
            else:
                segments[current].append(line)
    return segments


def parse_contact(lines):
    """
    Parse the contact section for zipcodes.
    """
    zipcodes = []
    for line in lines:
        zipcodes += re_zipcode.findall(line)
    return {
        "Zipcode": zipcodes
    }


def parse_education(lines):
    """
    Parse the education section for degrees, years, schools, and field of study.
    """
    load_word_trie('degrees')
    load_word_trie('schools')
    load_word_trie('fields_of_study')

    matches = []
    for line in lines:
        matches.append({
            "degrees": SOC_TRIES['degrees'].search(line),
            "years": find_years(line),
            "schools":  SOC_TRIES['schools'].search(re_alpha.sub("", line)),
            "fields_of_study" :  SOC_TRIES['fields_of_study'].search(line)
        })
    # Guess at whether degrees precede years/school, in which case the
    # search for degrees should go in reverse
    if matches and matches[0]["degrees"]:
        matches = matches[::-1]
    # Coalesce sets of degree/year/school, assuming reverse chronological order
    results = []
    template = {"degree": None, "school": None, "years": [], "fields_of_study" : []}
    result = template.copy()
    for match in matches:
        if match["degrees"]:
            result["degree"] = max(match["degrees"])
        if match["fields_of_study"]:
            result["fields_of_study"] = max(match["fields_of_study"])
        if match["years"]:
            result["years"] = match["years"]
        if match["schools"]:
            result["school"] = match["schools"][0]
        if result["degree"]:
            results.insert(0, result)
            result = template.copy()
    return {
        "Education": results
    }


def parse_experience(lines):
    """
    Parse the experience section for job titles and date ranges.
    """
    load_word_trie('socs')

    matches = []
    for line in lines:
        line = line.replace(".", "")
        match = {
            "socs": SOC_TRIES['socs'].search(line, return_nodes=True),
            "years": find_years(line),
            "dates": find_year_months(line)
        }
        if "present" in line or "current" in line:
            # match["years"].append(MAX_YEAR)
            # match["dates"].append(time.strftime("%Y-%m"))
            match["current"] = True
        matches.append(match)
    # Guess at whether job dates precede titles, in which case the
    # search for dates should go in reverse
    if matches and matches[0]["years"]:
        matches = matches[::-1]
    # Coalesce sets of SOCs/titles/years/dates
    results = []
    template = {"socs": [], "raw_titles": [], "titles": [], "years": [], "dates": [], "current": False}
    result = template.copy()
    for match in matches:
        if match["socs"]:
            result["socs"] = sum([x[1] for x in match["socs"]], start=[])
            result["raw_titles"] = [" ".join(x[0]) for x in match["socs"]]
            result["titles"] = [get_soc_title(soc) for soc in result["socs"]]
        if match["years"]:
            result["years"] = match["years"]
        if match["dates"]:
            result["dates"] = match["dates"]
        if match.get("current"):
            result["current"] = True
        if result["socs"] and result["years"]:
            results.insert(0, result)
            result = template.copy()
    return {
        "Experience": results
    }


def parse_skills(experience_lines, skill_lines):
    """
    Parse the experience or skills section for RIPL-edited skills.
    """
    load_word_trie('skills')
    skills = []
    for line in chain(experience_lines, skill_lines):
        line = line.replace(".", "")
        skills += SOC_TRIES['skills'].search(line)
    return {"Skills": skills}


def parse_resume(filename, extension):
    """
    Parse a resume file.
    """
    lines = extract(filename, extension)
    segments = segment(lines)
    matches = {}

    if "contact" in segments:
        matches.update(parse_contact(segments["contact"]))

    if "education" in segments:
        matches.update(parse_education(segments["education"]))

    if "experience" in segments:
        matches.update(parse_experience(segments["experience"]))

    if "experience" in segments or "skills" in segments:
        matches.update(parse_skills(
            segments.get("experience", []),
            segments.get("skills", [])
        ))

    sv = SkillVector(skill_dictionary={}, skill_list=matches.get("Skills", []))
    matches['SkillVector'] = sv
    return matches


def parse_job_posting(filename, extension):
    """
    Parse a job posting description.
    """
    load_word_trie('nonskills')
    load_word_trie('skills')
    results = {
        'NonSkills': [],
        'Skills': {}
    }

    lines = extract(filename, extension)
    if len(lines) == 1:
        lines = split_sentences(lines[0])

    for line in lines:
        line = clean(line.strip())
        nonskills = SOC_TRIES['nonskills'].search(line)
        if nonskills:
            results['NonSkills'] += nonskills
        else:
            for skill in SOC_TRIES['skills'].search(line):
                results["Skills"][skill] = results["Skills"].get(skill, 0) + 1
    results['NonSkills'] = list(sorted(set(results['NonSkills'])))
    sv = SkillVector(skill_dictionary = results['Skills'], skill_list = [])
    results['SkillVector'] = sv
    # Find closest SOC
    results["Occupations"] = [{"soc": soc, "soc_title": get_soc_title(soc)} for soc in sv.rank_socs()[:10]]
    return results
