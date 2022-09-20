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
SOC codes, based on analysis of over 40 million job postings in the National
Labor Exchange. An efficient prefix tree structure matches cleaned titles to
this model and returns the empirical frequencies of associated SOC codes,
which can be converted to probabilities.

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
