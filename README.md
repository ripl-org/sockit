![Sockit](https://github.com/ripl-org/sockit/blob/main/sockit.png)

*Sockit* is a natural-language processing toolkit for modeling structured
occupation information and Standard Occupational Classification (SOC) codes
in unstructured text from job titles, job postings, and resumes.

It is developed by [Research Improving People's Lives](https://www.ripl.org)
(RIPL) and is deployed in production in the following applications:
* [Hawai'i Career Acceleration Navigator](https://hican.hawaii.gov)
* [Career Compass RI](https://recommendations.backtoworkri.com)

You can test out sockit (without installing it) using a web-hosted version at
[https://research.ripl.org/#/sockit](https://research.ripl.org/#/sockit).

## Installation

Requires Python 3.8 or later.

To install the latest **production version** from PyPI using **pip**:

    pip install sockit

To install a **development version** from the current directory of the git
repository:

    pip install -e .

## Features

### Inferring SOC codes from job titles

Sockit includes an empirical model of the associations between job titles and
SOC codes, based on analysis of over 40 million U.S. job postings in the
National Labor Exchange (NLx) [Research Hub](https://nlxresearchhub.org/)
from the years 2019 and 2021. An efficient prefix tree structure matches
cleaned titles to this model and returns the empirical frequencies of
associated SOC codes, which can be converted to probabilities.

#### Python API

The `sockit.title` module provides functions for cleaning job titles,
searching for SOC code frequencies, and sorting and formatting the results
with probabilities:

    >>> import json
    >>> from sockit.title import clean, search, sort
    >>> title = clean("Paper Products Sales Rep - Dunder Mifflin - Scranton, PA - Onsite (Ask for Dwight)")
    >>> title
    'paper products sales rep'
    >>> socs = search(title)
    >>> socs
    {'414012': 9}
    >>> print(json.dumps(sort(socs), indent=2))
    [
      {
        "soc": "414012",
        "prob": 1.0,
        "title": "Wholesales and Manufacturing Sales Representative (Non-Technical Products)"
      }
    ]
    >>> title = clean("Banana Stand Attendant at Bluth's Original Frozen Banana Stand, Part-time")
    >>> title
    'banana stand attendant at bluth'
    >>> socs = search(title)
    >>> socs
    {'393091': 2, '353023': 68}
    >>> print(json.dumps(sort(socs), indent=2))
    [
      {
        "soc": "353023",
        "prob": 0.9714285714285714,
        "title": "Fast Food or Counter Worker"
      },
      {
        "soc": "393091",
        "prob": 0.02857142857142857,
        "title": "Amusement/Recreation Attendant"
      }
    ]

#### Batch processing via the command line

The `sockit title` command accepts an input CSV file or JSON file and outputs
processed results with a JSON object per input record:

    $ sockit title -h
    usage: sockit title [-h] [-i INPUT] [-o OUTPUT] [--record_id RECORD_ID] [--title TITLE]
     
    options:
      -h, --help            show this help message and exit
      -i INPUT, --input INPUT
                            input CSV or JSON file containing the record ID and title fields
      -o OUTPUT, --output OUTPUT
                            output file (default: stdout) containing a JSON record per line: {'record_id': ..., 'title': ..., 'clean_title': ..., 'socs': [{'soc': ..., 'prob': ..., 'desc': ...}, ...]}
      --record_id RECORD_ID
                            field name corresponding to the record ID [default: 1-based index]
      --title TITLE         field name corresponding to the title [default: 'title']
     
    $ cat test/title/job_titles.json
    [
      {"title": "outpatient registered nurse"},
      {"title": "licensed practical nurse"}
    ]
    $ sockit title -i test/title/job_titles.json -o test/title/job_titles_sockit.txt
    INFO:sockit.data:load_abbreviations: loading abbreviations
    INFO:sockit.data:load_acronyms: loading acronyms
    INFO:sockit.data:load_managers: loading managers
    INFO:sockit.data:load_titles: loading titles
    INFO:sockit.data:load_soc_titles: loading soc titles
    INFO:sockit.__main__:main: processed 2 records
    $ cat test/title/job_titles_sockit.txt
    {"record_id": 1, "title": "outpatient registered nurse", "clean_title": "outpatient registered nurse", "socs": [{"soc": "291141", "prob": 1.0, "title": "Registered Nurse"}]}
    {"record_id": 2, "title": "licensed practical nurse", "clean_title": "licensed practical nurse", "socs": [{"soc": "292061", "prob": 0.9999999999999999, "title": "Licensed Practical or Licensed Vocational Nurse"}]}

You can specify which columns or keys in the input file correspond to the
record ID and job title fields:

    $ cat test/title/employees.csv
    EmployeeId,JobTitle,Salary
    10042,CDL Delivery Driver,43000
    10289,Parts Delivery Driver,3980
    $ sockit title -i test/title/employees.csv -o test/title/employees_sockit.txt --record_id EmployeeId --title JobTitle
    INFO:sockit.data:load_abbreviations: loading abbreviations
    INFO:sockit.data:load_acronyms: loading acronyms
    INFO:sockit.data:load_managers: loading managers
    INFO:sockit.data:load_titles: loading titles
    INFO:sockit.data:load_soc_titles: loading soc titles
    INFO:sockit.__main__:main: processed 2 records
    $ cat test/title/employees_sockit.txt
    {"record_id": "10042", "title": "CDL Delivery Driver", "clean_title": "cdl delivery driver", "socs": [{"soc": "533032", "prob": 0.7986262878551359, "title": "Heavy and Tractor-Trailer Truck Driver"}, {"soc": "533052", "prob": 0.20137371214486421, "title": "Transit and Intercity Bus Driver"}]}
    {"record_id": "10289", "title": "Parts Delivery Driver", "clean_title": "parts delivery driver", "socs": [{"soc": "533033", "prob": 0.9739384407998203, "title": "Light Truck Driver"}, {"soc": "533032", "prob": 0.026061559200179735, "title": "Heavy and Tractor-Trailer Truck Driver"}]}

### Parsing job postings and resumes

The `sockit parse` command parses skills and other relevant occupational
information from job postings or resumes.

#### Job postings

Job postings are parsed by line and lines that contain non-skill information
such as benefits or EEO language are surpressed, while all remaining lines
are scanned with a prefix tree for skill keywords. The resulting skills
vector is used to determine the SOC codes of the closest 10 occupations.
The `test` directory contains three sample job postings (in a variety of
input formats) that illustrate this, shown below.

##### Job posting example #1: teacher

    $ sockit parse --type job --input test/job/teacher.txt
    INFO:sockit.data:get_soc: loading SOC codes
    INFO:sockit.data:load_soc_titles: loading soc titles
    {
      "NonSkills": [
        "Benefits",
        "Dental Insurance",
        "EEO",
        "Family Leave",
        "PTO",
        "Retirement"
      ],
      "Skills": {
        "Elementary Education": 1,
        "Teaching": 9,
        "Budgeting": 1,
        "Management": 1,
        "Strategy": 1,
        "Planning": 2,
        "Organization Skills": 1,
        "Rapport Building": 1,
        "Communication": 2,
        "Verbal Communication": 1,
        "Flexibility": 1,
        "Leadership": 1,
        "Recruiting": 1,
        "Memorization": 1
      },
      "Occupations": [
        {
          "soc": "252012",
          "soc_title": "Kindergarten Teacher",
          "z_score": 6.1340739033104175
        },
        {
          "soc": "252021",
          "soc_title": "Elementary School Teacher",
          "z_score": 6.123124685454242
        },
        {
          "soc": "253099",
          "soc_title": "Teacher/Instructor",
          "z_score": 5.930223278432139
        },
        {
          "soc": "253031",
          "soc_title": "Substitute Teacher",
          "z_score": 5.930223278432139
        },
        {
          "soc": "252011",
          "soc_title": "Preschool Teacher",
          "z_score": 5.8361803617909755
        },
        {
          "soc": "252022",
          "soc_title": "Middle School Teacher",
          "z_score": 5.690205772683181
        },
        {
          "soc": "252023",
          "soc_title": "Career/Technical Middle School Teacher",
          "z_score": 5.489350883088146
        },
        {
          "soc": "252058",
          "soc_title": "Special Education Teacher (Secondary School)",
          "z_score": 5.230804954926826
        },
        {
          "soc": "252031",
          "soc_title": "Secondary School Teacher",
          "z_score": 5.225045938796079
        },
        {
          "soc": "252057",
          "soc_title": "Special Education Teacher (Middle School)",
          "z_score": 4.916999315432507
        }
      ]
    }

##### Job posting example #2: production supervisor

    $ sockit parse --type job --input test/job/supervisor.html
    INFO:sockit.data:get_soc: loading SOC codes
    INFO:sockit.data:load_soc_titles: loading soc titles
    {
      "NonSkills": [],
      "Skills": {
        "Production": 7,
        "Supervision": 2,
        "Communication": 1,
        "Manufacturing": 2,
        "Leadership": 2,
        "Safety": 3,
        "Scheduling": 1,
        "Impact": 1,
        "Performance Management": 1,
        "Coaching": 1,
        "Continuous Improvement": 1,
        "Management": 1,
        "Problem Solving": 1,
        "Digital Literacy": 1,
        "Engineering": 2,
        "Innovative": 1
      },
      "Occupations": [
        {
          "soc": "514021",
          "soc_title": "Extruding and Drawing Machine Operator",
          "z_score": 4.01253858216756
        },
        {
          "soc": "519011",
          "soc_title": "Chemical Equipment Operator",
          "z_score": 3.917867944983724
        },
        {
          "soc": "519196",
          "soc_title": "Paper Goods Machine Operator",
          "z_score": 3.639472527698138
        },
        {
          "soc": "513091",
          "soc_title": "Food Roasting, Baking, and Drying Machine Operator",
          "z_score": 3.61731607643985
        },
        {
          "soc": "516031",
          "soc_title": "Sewing Machine Operator",
          "z_score": 3.5641886213590275
        },
        {
          "soc": "516062",
          "soc_title": "Textile Cutting Machine Operator",
          "z_score": 3.546025880661149
        },
        {
          "soc": "514022",
          "soc_title": "Forging Machine Operator",
          "z_score": 3.4569922320604425
        },
        {
          "soc": "514072",
          "soc_title": "Molding, Coremaking, and Casting Machine Operator",
          "z_score": 3.3011492419708905
        },
        {
          "soc": "519191",
          "soc_title": "Adhesive Bonding Machine Operator",
          "z_score": 3.282434975425132
        },
        {
          "soc": "519161",
          "soc_title": "Computer Numerically Controlled Tool Operator",
          "z_score": 3.276427835476489
        }
      ]
    }

##### Job posting example #3: paralegal

    $ sockit parse --type job --input test/job/paralegal.pdf
    INFO:sockit.data:get_soc: loading SOC codes
    INFO:sockit.data:load_soc_titles: loading soc titles
    {
      "NonSkills": [
        "401(k)",
        "Benefits",
        "Dental Insurance",
        "Family Leave",
        "Health Insurance",
        "Retirement",
        "Vision Insurance"
      ],
      "Skills": {
        "Law": 8,
        "Supervision": 1,
        "Communication": 1,
        "Work Ethic": 1,
        "Initiative": 1,
        "Accuracy": 1,
        "Digital Literacy": 2,
        "Microsoft Excel": 1,
        "Management": 1,
        "Software": 1,
        "Scheduling": 2,
        "Insurance": 1
      },
      "Occupations": [
        {
          "soc": "231012",
          "soc_title": "Judicial Law Clerk",
          "z_score": 14.074118595454268
        },
        {
          "soc": "231023",
          "soc_title": "Judge/Magistrate Judge/Magistrate",
          "z_score": 10.874543405453768
        },
        {
          "soc": "231011",
          "soc_title": "Lawyer",
          "z_score": 9.76905319807106
        },
        {
          "soc": "333011",
          "soc_title": "Bailiff",
          "z_score": 9.501943897149564
        },
        {
          "soc": "273092",
          "soc_title": "Court Reporter or Simultaneous Captioner",
          "z_score": 8.483960747022026
        },
        {
          "soc": "436012",
          "soc_title": "Legal Secretary or Administrative Assistant",
          "z_score": 7.036503182579855
        },
        {
          "soc": "232011",
          "soc_title": "Paralegal or Legal Assistant",
          "z_score": 5.852005777147664
        },
        {
          "soc": "434031",
          "soc_title": "Court/Municipal/License Clerk",
          "z_score": 5.172055060522774
        },
        {
          "soc": "211092",
          "soc_title": "Probation Officer or Correctional Treatment Specialist",
          "z_score": 3.913295887771758
        },
        {
          "soc": "231021",
          "soc_title": "Administrative Law Judge/Adjudicator/Hearing Officer",
          "z_score": 3.8467094391681456
        }
      ]
    }

#### Resumes

Resumes are segmented into groups of lines that occur after predefined
section headers, which come from a manually curated list in
`sockit/data/resume_headers.json`. Zipcodes are parsed from 5-digit
numbers in the contact section; post-secondary school names, degree
types, and fields of study are parsed from the education section;
skill keywords, job titles, SOC codes, month/year ranges, and total
years of experience are parsed from the experience section; and
skill keywords are parsed from the skills section. The ordering
of the parsed skill keywords is retained in the results, since it
may contain information about recency or importance of skills.

The `test` directory contains three sample resumes (in a variety of
input formats) that illustrate this, shown below, which also
correspond to the job posting examples from above.

##### Resume example #1: teacher

    $ sockit parse --type resume --input test/resume/teacher.txt
    INFO:sockit.data:load_soc_titles: loading soc titles
    {
      "Zipcode": [],
      "Education": [
        {
          "degree": 17,
          "school": "Rutgers University-New Brunswick",
          "years": [
            2015
          ],
          "fields_of_study": "Reading|360116"
        },
        {
          "degree": 16,
          "school": "Rutgers University-New Brunswick",
          "years": [
            2013
          ],
          "fields_of_study": "Curriculum and Instruction|130301"
        }
      ],
      "Experience": [
        {
          "socs": [
            "252021"
          ],
          "raw_titles": [
            "elementary teacher"
          ],
          "titles": [
            "Elementary School Teacher"
          ],
          "years": [
            2015,
            2017
          ],
          "dates": [
            "2015-07",
            "2017-07"
          ],
          "current": false
        },
        {
          "socs": [
            "252021"
          ],
          "raw_titles": [
            "elementary teacher"
          ],
          "titles": [
            "Elementary School Teacher"
          ],
          "years": [
            2017,
            2019
          ],
          "dates": [
            "2017-08",
            "2019-09"
          ],
          "current": false
        }
      ],
      "Skills": [
        "Teaching",
        "Teaching",
        "Strategy",
        "Teaching",
        "Teaching",
        "Teamwork",
        "Accuracy",
        "Teaching",
        "Teaching",
        "Supervision"
      ]
    }

##### Resume example #2: production supervisor

    $ sockit parse --type resume --input test/resume/supervisor.pdf
    INFO:sockit.data:load_soc_titles: loading soc titles
    {
      "Zipcode": [],
      "Education": [],
      "Experience": [
        {
          "socs": [
            "331011",
            "331012",
            "391013",
            "411011"
          ],
          "raw_titles": [
            "shift supervisor"
          ],
          "titles": [
            "Supervisor of Correctional Officers",
            "Supervisor of Police and Detectives",
            "Supervisor of Gambling Services Worker",
            "Supervisor of Retail Sales Worker"
          ],
          "years": [
            2009,
            2012
          ],
          "dates": [
            "2009-06",
            "2012-09"
          ],
          "current": false
        },
        {
          "socs": [
            "511011"
          ],
          "raw_titles": [
            "production supervisor"
          ],
          "titles": [
            "Supervisor of Production and Operating Workers"
          ],
          "years": [
            2013
          ],
          "dates": [
            "2013-03"
          ],
          "current": true
        }
      ],
      "Skills": [
        "Production",
        "Supervision",
        "Safety",
        "Quality Assurance",
        "Teamwork",
        "Human Resources",
        "Employee Relations",
        "Evaluating",
        "Onboarding",
        "Leadership",
        "Supply Chain",
        "Management",
        "Decision Making",
        "Problem Solving",
        "Budgeting",
        "Active Listening"
      ]
    }

##### Resume example #3: paralegal

    $ sockit parse --type resume --input test/resume/paralegal.docx
    INFO:sockit.data:load_soc_titles: loading soc titles
    {
      "Zipcode": [
        "07928"
      ],
      "Education": [
        {
          "degree": 14,
          "school": "Essex County College",
          "years": [],
          "fields_of_study": []
        }
      ],
      "Experience": [
        {
          "socs": [
            "232011"
          ],
          "raw_titles": [
            "paralegal"
          ],
          "titles": [
            "Paralegal or Legal Assistant"
          ],
          "years": [
            2009
          ],
          "dates": [],
          "current": true
        },
        {
          "socs": [
            "111021",
            "431011"
          ],
          "raw_titles": [
            "office manager"
          ],
          "titles": [
            "Operations Manager",
            "Supervisor of Office and Administrative Support Workers"
          ],
          "years": [
            2016
          ],
          "dates": [],
          "current": false
        },
        {
          "socs": [
            "232011"
          ],
          "raw_titles": [
            "paralegal"
          ],
          "titles": [
            "Paralegal or Legal Assistant"
          ],
          "years": [
            2007,
            2009
          ],
          "dates": [],
          "current": true
        },
        {
          "socs": [
            "436014",
            "436014"
          ],
          "raw_titles": [
            "secretary",
            "administrative assistant"
          ],
          "titles": [
            "Secretary or Administrative Assistant",
            "Secretary or Administrative Assistant"
          ],
          "years": [
            2000,
            2007
          ],
          "dates": [],
          "current": false
        }
      ],
      "Skills": [
        "Law",
        "Law",
        "Administration",
        "Law",
        "Human Resources",
        "Scheduling",
        "Writing",
        "Clerical",
        "Law",
        "Invoicing",
        "Teamwork",
        "Collections",
        "Law",
        "Law",
        "Law",
        "Law",
        "Management",
        "Law",
        "Prioritization",
        "Administration"
      ]
    }

### Comparing job postings, resumes and SOC codes

## License

Sockit is freely available for non-commercial use under the license provided in
[LICENSE.txt](https://github.com/ripl-org/sockit/blob/main/LICENSE.txt).
Please contact [connect@ripl.org](mailto:connect@ripl.org) to inquire about
commercial use.

## Contributors

* Marcelle Goggins
* Ethan Ho
* Nile Dixon
* [Mark Howison](https://mark.howison.org)
* Joe Long
* Karen Shen
