#!/usr/bin/env python

import os
import sys
import errno
import configparser
import argparse
import textwrap
import subprocess
import pprint
from hashlib import blake2b
from pathlib import Path
from colorama import init, Fore, Style
from tinydb import TinyDB, Query


def get_max_columns():
    max_columns = None
    try:
        max_columns = subprocess.check_output(['tput', 'cols'])
    except (subprocess.CalledProcessError, FileNotFoundError):
        max_columns = os.environ.get('COLUMNS', 70)
    return int(max_columns)


def init_config(cfg, torgo_cfg):
    """ Initializes the config (will wipe-out anything there)"""
    init()

    print(
        Style.RESET_ALL + Style.BRIGHT + "TORGO CONFIGURATION INITIALIZATION\n"
    )
    print(Style.RESET_ALL + "Please enter your desired configuration settings,")
    print("defaults are in hard brackets\n")

    print(Style.BRIGHT + Fore.GREEN + "Torgo Org Directory:")
    org_dir = "{0}/.torgo".format(str(Path.home()))
    user_org = input(
        Style.RESET_ALL + "[" + Style.DIM + org_dir + Style.RESET_ALL + "] "
    )
    if user_org == '':
        user_org = org_dir

    print(
        "\n"
        + Style.BRIGHT
        + Fore.GREEN
        + "The editor to use, blank to use $EDITOR from environment:"
    )
    editor = input(Style.RESET_ALL + "[] ")

    print(
        "\n"
        + Style.BRIGHT
        + Fore.GREEN
        + "The extension to use for the Org files:"
    )
    ext = input(
        Style.RESET_ALL + "[" + Style.DIM + "org" + Style.RESET_ALL + "] "
    )

    if ext == '':
        ext = "org"

    cfg['TORGO'] = {}
    cfg['TORGO']['org_dir'] = user_org
    cfg['TORGO']['editor'] = editor
    cfg['TORGO']['ext'] = ext
    with open(torgo_cfg, 'w') as f:
        cfg.write(f)


def get_hash(p):
    """ Given a path object, get a hash for it. """
    h = blake2b()
    h.update(str(p).encode('utf-8'))
    return h.hexdigest()


def mkdir_p(path):
    """ Equivalent of mkdir -p """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass


def find_org(path):
    """ Given a path, attempt to find an org file already created for
    the path or its parents. Return the hash associated with the org file.
    If no parents have an org file, or if the '-t' arg is passed, then
    we just return the hash associated original path. """
    orig_path = path.resolve()
    org_hash = get_hash(orig_path)
    h = org_hash
    q = Query()

    while not args.this:
        r = db.search(q.hash == h)
        if len(r) > 0:
            return h, path
        else:
            lp = path
            path = path.parent
            if path == lp:
                break
            h = get_hash(path)

    return org_hash, orig_path


# The commands
def cmd_tag():
    """ The tag command function. """
    all_tags = []
    if lookup is None:
        print(
            "Error, no org file here. Please create tags after you have "
            + "actually created an org file (after you first edit it)"
        )
        sys.exit(1)
    if 'tags' in lookup:
        all_tags = lookup['tags']
    if args.param:
        tags = args.param.split(',')
        for t in tags:
            if t.startswith('.'):
                temp_t = t.lstrip('.')
                if temp_t in all_tags:
                    all_tags.remove(temp_t)
            else:
                if t not in all_tags:
                    all_tags.append(t)

        lookup['tags'] = all_tags
        q = Query()
        # FIXME : update or upsert?
        db.update(lookup, q.hash == lookup['hash'])
    else:
        if len(all_tags) > 0:
            print("The tags associated with this org file:")
            for t in all_tags:
                print("\t{0}".format(t))
        else:
            print("No tags associated with this org file.")


def cmd_info():
    """ Prints information about this org file """
    if lookup is None:
        print("There is no org file associated with this directory.")
    else:
        print("The information about this org file is as follows:")
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(lookup)


def print_search_params():
    """ Print the search parameter instructions """
    print("\nPlease include one of the following:")
    print(
        "\ttag=tags\tWhere 'tags' is a comma separated list of tags "
        + "search for."
    )
    print("\tall\tTo list all the org file records.")


def highlight_tags(r, tags):
    """ Given a record, and tags, highlight the tags, returning a string """
    s = Style.RESET_ALL + "["
    th = []
    for t in r['tags']:
        if t in tags:
            th.append(Style.BRIGHT + Fore.YELLOW + t + Style.RESET_ALL)
        else:
            th.append(t)

    return s + ", ".join(th) + "]"


def cmd_search():
    """ Searches the data base (and org files?) for something """
    if args.param:
        qs = Query()
        try:
            (stype, sparm) = args.param.split("=")
        except ValueError as exc:
            # Hopefully a single search type
            stype = args.param
            sparm = None
        if stype == 'tag':
            if sparm is None:
                print("No tags to sarch with!")
                print_search_params()
                sys.exit(1)
            tags = set(sparm.split(','))
            recs = db.search(qs.tags.any(tags))
            if len(recs) > 0:
                print(
                    "Found {0} record(s) with the following tag(s):".format(
                        len(recs)
                    )
                )
                for t in tags:
                    print("\t{0}".format(t))
                print()
                for r in recs:
                    print(
                        "Path: {0} | {1}".format(
                            r['path'], highlight_tags(r, tags)
                        )
                    )
            else:
                print("Found 0 records...")
        elif stype == 'all':
            # This may suck if the thing is huge...
            print("There are {0} org files being managed.\n".format(len(db)))
            for r in db.all():
                print("Path: {0}".format(r['path']))
        else:
            print("Unknown search type '{0}'".format(stype))
            print_search_params()
            sys.exit(1)
    else:
        print("No search parameter found!")
        print_search_params()
        sys.exit(1)


def main():
    commands = {
        'tag': {
            'method': cmd_tag,
            'desc': 'Sets or unsets a tag for the given org file. The '
            + 'parameters are a comma separated list of tags to set '
            + 'or unset. If called with no options, will list the '
            + 'tags. If tag is prefixed with a ".", it will unset tag.',
        },
        'info': {
            'method': cmd_info,
            'desc': 'Prints the information for the given org file.',
        },
        'search': {
            'method': cmd_search,
            'desc': 'Search functionality. Use "tag=" followed by a comma '
            + 'separated list of tags to search. Use "all" to list '
            + 'all known org files.',
        },
    }

    parser = argparse.ArgumentParser(description="Org-file anywhere, managed")
    parser.add_argument("command", help="The command to run", nargs='?')
    parser.add_argument(
        "param",
        help="Optional param for commands, see "
        + "commands list for more information",
        nargs='?',
    )
    parser.add_argument(
        "-l", "--list", help="List the commands available", action="store_true"
    )
    parser.add_argument(
        "-t",
        "--this",
        help="Use 'this' directory, don't attempt to find org file in parents",
        action="store_true",
    )
    parser.add_argument(
        "-i",
        "--init",
        help="Force a re-init of the configuration",
        action="store_true",
    )
    parser.add_argument(
        "-p",
        "--prune",
        help="Prune the current org file (delete it)",
        action="store_true",
    )
    args = parser.parse_args()

    if args.list:
        key_len = len(max(commands.keys(), key=len))
        desc_len = get_max_columns() - 5 - key_len
        for cmd in sorted(commands.keys()):
            desc = textwrap.wrap(commands[cmd]['desc'], desc_len)
            print('  {0} : {1}'.format(cmd.rjust(key_len), desc[0]))
            for i in range(1, len(desc)):
                print(' ' * (5 + key_len) + '{0}'.format(desc[i]))
        sys.exit(0)

    # Attempt to load the configuration
    torgo_cfg = '{0}/.torgo.cfg'.format(str(Path.home()))
    if 'TORGO_CFG' in os.environ:
        torgo_cfg = os.environ['TORGO_CFG']

    cfg = configparser.ConfigParser()
    must_init = False

    if os.path.isfile(torgo_cfg):
        cfg.read(torgo_cfg)
    else:
        must_init = True

    if must_init or args.init:
        init_config(cfg, torgo_cfg)

    editor = cfg['TORGO']['editor']
    if editor == '':
        if 'EDITOR' in os.environ:
            editor = os.environ['EDITOR']
        else:
            print(
                Style.RESET_ALL
                + Style.BRIGHT
                + Fore.RED
                + "ERROR, NO EDITOR FOUND!"
                + Style.RESET_ALL
            )
            print(
                "\nPlease set your editor either in the config "
                + "file '{0}' or".format(torgo_cfg)
            )
            print("in the environment variable $EDITOR.")
            print("\nYou can re-run torgo with '-i' to force re-initialization")
            sys.exit(1)

    mkdir_p(cfg['TORGO']['org_dir'])

    db = TinyDB('{0}/org_lookup_db.json'.format(cfg['TORGO']['org_dir']))

    org, path = find_org(Path.cwd())

    qh = Query()
    lookup = db.get(qh.hash == org)

    if args.command in commands:
        commands[args.command]['method']()
    else:
        if args.prune:
            if lookup:
                org_file = Path(cfg['TORGO']['org_dir'])
                org_file = org_file / lookup['org_file']
            else:
                print(
                    "No org file associated with this directory, nothing to "
                    + "prune."
                )
                sys.exit()

            while True:
                yn = input("Prune this org file? (yes/NO): ")
                if yn.lower() == "yes":
                    break
                else:
                    print("Prune cancelled...")
                    sys.exit()
            try:
                os.remove(org_file)
            except FileNotFoundError:
                # This could happen if they fired up torgo, then didn't edit
                # or save the org file. So it shouldn't be anything more than a
                # warning.
                print(
                    "WARN: Tried to remove the org file, but it wasn't found."
                )
            db.remove(qh.hash == org)
            print("Pruned this org file")
        else:
            if lookup is None:
                lookup = {
                    'hash': org,
                    'path': str(path),
                    'org_file': '{0}.{1}'.format(org, cfg['TORGO']['ext']),
                }
                db.insert(lookup)
            org_file = Path(cfg['TORGO']['org_dir'])
            org_file = org_file / lookup['org_file']
            sys.exit(os.system('{0} {1}'.format(editor, str(org_file))))
