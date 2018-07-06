#!/usr/bin/env python

import sys
import configparser
import argparse
from tinydb import TinyDB, Query

parser = argparse.ArgumentParser(description="Org-file anywhere, managed")
parser.add_argument(
        "-t", "--this",
        help="Use 'this' directory, don't attempt to find org file in parents",
        action="store_true")
args = parser.parse_args()
