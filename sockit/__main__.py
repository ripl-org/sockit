import argparse
import csv
import logging
import json
import sockit.compare
import sockit.parse
import sockit.title
import sys
from itertools import combinations
from sockit.log import Log


def run_compare(args):
    items = (
        [{"source": job,    "type": "job"   } for job    in args.job   ] +
        [{"source": resume, "type": "resume"} for resume in args.resume] +
        [{"source": soc,    "type": "soc"   } for soc    in args.soc   ]
    )
    with open(args.output, "w") if args.output != "-" else sys.stdout as fout:
        for item1, item2 in combinations(items, 2):
            json.dump(
                sockit.compare.compare(
                    item1["source"], 
                    item1["type"],
                    item2["source"],
                    item2["type"],
                    args.similarity
                ),
                fout,
                indent=2
            )
            fout.write("\n")


def run_parse(args):
    with open(args.output, "w") if args.output != "-" else sys.stdout as fout:
        for filepath in args.input:
            if args.type == "resume":
                result = sockit.parse.parse_resume(filepath)
            elif args.type == "job":
                result = sockit.parse.parse_job_posting(filepath)
            else:
                Log(__name__, "run_parse").error(f"unknown type '{args.type}'")
                return
            del result["SkillVector"]
            json.dump(result, fout, indent=2)
            fout.write("\n")


def run_title(args):
    log = Log(__name__, "run_title")
    with open(args.input, "r") as fin:
        if args.input.endswith(".json"):
            reader = json.load(fin)
        else:
            reader = csv.DictReader(fin)
        with open(args.output, "w") if args.output != "-" else sys.stdout as fout:
            for n, record in enumerate(reader, start=1):
                # Validate input record
                if args.record_id is not None:
                    if args.record_id in record:
                        record_id = record[args.record_id]
                    else:
                        log.error(
                            f"record {n} is missing record_id field '{args.record_id}'"
                        )
                        sys.exit(-1)
                else:
                    record_id = n
                if args.title in record:
                    title = record[args.title]
                else:
                    log.error(f"record {n} is missing title field '{args.title}'")
                    sys.exit(-1)
                
                # Search
                clean_title = sockit.title.clean(title)
                counts = sockit.title.search(clean_title)
                socs = sockit.title.sort(counts)
                # Write output record
                json.dump(
                    {
                        "record_id": record_id,
                        "title": title,
                        "clean_title": clean_title,
                        "socs": socs,
                    },
                    fout,
                )
                fout.write("\n")

    # Print summary stats
    log.info("processed {:d} records".format(n))


def main():

    parser = argparse.ArgumentParser(description=sockit.__doc__)
    subparsers = parser.add_subparsers()

    # Shared arguments
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="sockit {}".format(sockit.__version__),
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="suppress all logging messages except for errors",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="show all logging messages, including debugging output",
    )


    ### Compare Module ###

    compare = subparsers.add_parser("compare")
    compare.set_defaults(run=run_compare)

    compare.add_argument(
        "--resume",
        help="resumes",
        default=[],
        nargs="*"
    )
    compare.add_argument(
        "--job",
        help="job descriptions",
        default=[],
        nargs="*"
    )
    compare.add_argument(
        "--soc",
        help="six digit SOC codes",
        default=[],
        nargs="*"
    )

    compare.add_argument(
        "--similarity",
        default="cosine",
        help="similarity metric [default: 'cosine', 'euclidean', 'manhattan', 'kl']"
    )
    # Optional arguments
    compare.add_argument(
        "-o",
        "--output",
        default="-",
        help="output file (default: stdout) containing a JSON record per line",
    )


    ### Parse Module ###

    parse = subparsers.add_parser("parse")
    parse.set_defaults(run=run_parse)

    # Required arguments
    parse.add_argument(
        "-i",
        "--input",
        help="input HTML, PDF, DOCX, or TXT files to parse",
        nargs="+"
    )
    parse.add_argument(
        "-t",
        "--type",
        help="type of description to parse ['resume', 'job']"
    )

    # Optional arguments
    parse.add_argument(
        "-o",
        "--output",
        default="-",
        help="output file (default: stdout) containing a JSON record per line",
    )


    ### Title Module ###

    title = subparsers.add_parser("title")
    title.set_defaults(run=run_title)

    # Required arguments
    title.add_argument(
        "-i",
        "--input",
        help="input CSV or JSON file containing the record ID and title fields"
    )

    # Optional arguments
    title.add_argument(
        "-o",
        "--output",
        default="-",
        help="output file (default: stdout) containing a JSON record per line: {'record_id': ..., 'title': ..., 'clean_title': ..., 'socs': [{'soc': ..., 'prob': ..., 'desc': ...}, ...]}",
    )
    title.add_argument(
        "--record_id",
        default=None,
        help="field name corresponding to the record ID [default: 1-based index]",
    )
    title.add_argument(
        "--title",
        default="title",
        help="field name corresponding to the title [default: 'title']",
    )


    # Parse arguments and run module

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    elif args.quiet:
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.INFO)

    args.run(args)


if __name__ == "__main__":
    main()
