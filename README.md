![Sockit](https://github.com/ripl-org/sockit/blob/main/sockit.png)

*Sockit* is a self-contained toolkit for assigning probabilistic Standard Occupational Classification (SOC) codes to free-text job titles. It is developed by [Research Improving People's Lives (RIPL)](https://www.ripl.org).

## Installation

Requires Python 3.8 or later.

To install from PyPI using **pip**:

    pip install sockit

To install a **development version** from the current directory:

    pip install -e .

## Running

There is a single command line script included, `sockit`, that processes existing CSV files containing free-text job titles in one of the columns:

    sockit -h

    usage: sockit [-h] [-v] [-q] [-d] -i INPUT [-o OUTPUT] [--record_id RECORD_ID] [--title TITLE] [--score SCORE SCORE]

    Sockit: assign probabilistic Standard Occupational Classification (SOC) codes to free-text job titles https://github.com/ripl-org/sockit

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      -q, --quiet           suppress all logging messages except for errors
      -d, --debug           show all logging messages, including debugging output
      -i INPUT, --input INPUT
                            input CSV file containing the record ID and title fields
      -o OUTPUT, --output OUTPUT
                            output file (default: stdout) containing a JSON record per line: {'record_id': ..., 'title': ..., 'clean_title': ..., 'socs': [{'soc': ..., 'prob': ..., 'desc': ...}, ...]}
      --record_id RECORD_ID
                            field name corresponding to the record ID [default: 1-based index]
      --title TITLE         field name corresponding to the title [default: 'title']
      --score SCORE SCORE   weight likely SOCs by matches to nodes and nouns [default: 1 2]

Alternatively, you can load the `sockit` package in a python script and process titles one at a time with the `search()` method:

    import sockit
    clean_title = sockit.clean(title)
    counts = sockit.search(clean_title, node_match_weight=0, noun_match_weight=1)
    socs = sockit.sort(counts)

## License

Sockit is freely available for non-commercial use under the license provided in [LICENSE.txt](https://github.com/ripl-org/sockit/blob/main/LICENSE.txt).
Please contact [connect@ripl.org](mailto:connect@ripl.org) to inquire about commercial use.

## Contributors

* Marcelle Goggins
* Ethan Ho
* Nile Dixon
* Mark Howison
* Joe Long
* Karen Shen
