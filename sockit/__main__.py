import argparse
import csv
import logging
import json
import sockit.log
import sockit.compare
import sockit.parse
import sockit.title
import sys

def perform_resume_comparison(args):
    with open(args.output, 'w') if args.output != '-' else sys.stdout as fout:
        json.dump(
            sockit.compare.compare_resume_and_description(
                args.resume,
                args.resume_ext,
                args.desc,
                args.desc_ext,
                args.distance
            ),
            fout
        )

def parse_resume(args):
    parsed_resume = sockit.parse.parse_resume(args.file,args.ext)
    del parsed_resume['SkillVector']
    with open(args.output, 'w') if args.output != '-' else sys.stdout as fout:
        json.dump(parsed_resume,fout)

def parse_job_description(args):
    parsed_job_desc = sockit.parse.parse_job_posting(args.file, args.ext)
    del parsed_job_desc['SkillVector']
    with open(args.output, 'w') if args.output != '-' else sys.stdout as fout:
        json.dump(parsed_job_desc, fout)


def find_soc_codes(args):
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


mapping_functions = {
    'compare' : perform_resume_comparison,
    'parse_resume' : parse_resume,
    'parse_posting' : parse_job_description,
    'find_soc' : find_soc_codes
}

def main():

    parser = argparse.ArgumentParser(description=sockit.__doc__)

    # Basic arguments
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

    subparsers = parser.add_subparsers()

    title = subparsers.add_parser("title")
    title.set_defaults(action="title")

    # Required arguments
    title.add_argument(
        "-i",
        "--input",
        help="input CSV or JSON file containing the record ID and title fields",
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

    parser.add_argument("--resume")
    parser.add_argument("--resume_ext")
    parser.add_argument("--desc")
    parser.add_argument("--desc_ext")
    parser.add_argument("--distance", default = "manhattan")
    parser.add_argument("--file")
    parser.add_argument("--ext")

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    elif args.quiet:
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.INFO)

    log = sockit.log.Log(__name__, "main")
    if args.action in mapping_functions:
        mapping_functions[args.action](args)
    else:
        log.error(f"{args.action} is an invalid action")

if __name__ == "__main__":
    main()