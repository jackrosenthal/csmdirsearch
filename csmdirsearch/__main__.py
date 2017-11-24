import sys
from csmdirsearch.dirsearch import search, search_by_name, search_by_partial
from argparse import ArgumentParser

def format_mutt(results):
    print('Searching dirsearch ...', end='')
    entries = 0
    for result in results:
        if not hasattr(result, "business_email"):
            continue
        entries += 1
        if entries == 1:
            print()
        print("{}\t{}\t{}".format(
            result.business_email,
            result.name.strfname("{pfirst} {last}"),
            result.desc,
        ))
    if not entries:
        print(" no results found!")
        sys.exit(1)

def format_pretty(results):
    for result in results:
        print(result.name)
        if result.desc:
            print(result.desc)
        for attr in result.__dict__.keys():
            if attr in {"name", "classification", "department", "department_url"}:
                continue
            print("{}: {}".format(attr.replace("_", " ").title(), getattr(result, attr)))
        print()

def main():
    parser = ArgumentParser()
    parser.add_argument("--format", type=str, default="pretty", help="Format for output (mutt, or default: pretty)")
    parser.add_argument("--input", type=str, default="all", help="If set to name or partial, will use search_by_name or search_by_partial")
    parser.add_argument("query", type=str, help="Search Query")
    args = parser.parse_args()

    fmt = globals()["format_" + args.format]
    func = {
        "all": search,
        "name": search_by_name,
        "partial": search_by_partial,
    }[args.input]

    fmt(func(args.query))

if __name__ == '__main__':
    main()
