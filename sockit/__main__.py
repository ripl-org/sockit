import argparse
import csv
import logging
import json
import sockit.log
import sockit.compare
import sockit.parse
import sockit.title
import sys

def infer_extension(filename):
    extensions = {
        '.html' : 'html',
        '.htm' : 'html',
        '.docx' : 'docx',
        '.txt' : 'txt',
        '.pdf' : 'pdf'
    }
    for ext in list(extensions.keys()):
        if filename.endswith(ext):
            return extensions[ext]
    log.error(f'{filename} does not have an appropriate file extension.')
    

def perform_resume_comparison(args, log):
    with open(args.output, 'w') if args.output != '-' else sys.stdout as fout:
        for desc in args.desc:
            for resume in args.resume:
                parsed_contents = sockit.compare.compare_resume_and_description(
                    resume, 
                    infer_extension(resume),
                    desc,
                    infer_extension(desc),
                    args.distance
                )
                json.dump(parsed_contents,fout)
                fout.write('\n')


        for soc in args.soc:
            for resume in args.resume:
                parsed_contents = sockit.compare.compare_resume_and_soc(
                    resume,
                    infer_extension(resume),
                    soc,
                    args.distance
                )
                json.dump(parsed_contents,fout)
                fout.write('\n')



def parse_files(args, log):
    file_paths = args.file.split(',')
    with open(args.output, 'w') if args.output != '-' else sys.stdout as fout:
        for file_path in file_paths:
            if args.type == 'resume':
                parsed_contents = sockit.parse.parse_resume(
                    file_path, infer_extension(file_path)
                )
            else:
                parsed_contents = sockit.parse.parse_job_posting(
                    file_path, infer_extension(file_path)
                )
            del parsed_contents['SkillVector']
            json.dump(parsed_contents, fout)
            fout.write('\n')


def find_soc_codes(args, log):
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
    'parse' : parse_files,
    'title' : find_soc_codes
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

    #CODE FOR TITLE SUBPARSER
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

    #CODE FOR COMPARE SUBPARSER
    compare = subparsers.add_parser("compare")
    compare.set_defaults(action = "compare")

    compare.add_argument(
        "--resume",
        help = "file path or list of file paths to resumes",
        default = [],
        nargs = "*"
    )
    compare.add_argument(
        "--desc",
        help = "file path or list of file paths to job descriptions",
        default = [],
        nargs = "*"
    )
    compare.add_argument(
        "--soc",
        help = "six digit SOC code or list of six digit SOC codes",
        default = [],
        nargs = "*"
    )

    compare.add_argument(
        "--distance",
        default = "manhattan",
        help = "Distance function for comparing resumes with descriptions or SOC codes"
    )
    # Optional arguments
    compare.add_argument(
        "-o",
        "--output",
        default="-",
        help="output file (default: stdout) containing a JSON record per line: {'record_id': ..., 'title': ..., 'clean_title': ..., 'socs': [{'soc': ..., 'prob': ..., 'desc': ...}, ...]}",
    )

    #CODE FOR PARSE SUBPARSER
    parse = subparsers.add_parser("parse")
    parse.set_defaults(action = "parse")

    parse.add_argument(
        "--file",
        help = "The file path or list of file paths you want to parse",
        default = [],
        nargs = "*"
    )

    parse.add_argument(
        "--type",
        default = "resume",
        help = "The type of file you want to parse [resume|job]"
    )
    # Optional arguments
    parse.add_argument(
        "-o",
        "--output",
        default="-",
        help="output file (default: stdout) containing a JSON record per line: {'record_id': ..., 'title': ..., 'clean_title': ..., 'socs': [{'soc': ..., 'prob': ..., 'desc': ...}, ...]}",
    )

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    elif args.quiet:
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.INFO)

    log = sockit.log.Log(__name__, "main")
    if args.action in mapping_functions:
        mapping_functions[args.action](args, log)
    else:
        log.error(f"{args.action} is an invalid action")

if __name__ == "__main__":
    main()
