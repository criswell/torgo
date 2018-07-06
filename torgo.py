#!/usr/bin/env python

import os
import configparser
import argparse
from pathlib import Path
from colorama import init, Fore, Back, Style
from tinydb import TinyDB, Query

parser = argparse.ArgumentParser(description="Org-file anywhere, managed")
parser.add_argument(
        "-t", "--this",
        help="Use 'this' directory, don't attempt to find org file in parents",
        action="store_true")
args = parser.parse_args()

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


def init_config():
    """ Initializes the config (will wipe-out anything there)"""
    init()

    print(Style.RESET_ALL + Style.BRIGHT +
          "TORGO CONFIGURATION INITIALIZATION\n")
    print(Style.RESET_ALL +
          "Please enter your desired configuration settings,")
    print("defaults are in hard brackets\n")

    print(Style.BRIGHT + Fore.GREEN + "Torgo Org Directory:")
    org_dir = "{0}/.torgo".format(str(Path.home()))
    user_org = input(Style.RESET_ALL +
                     "[" + Style.DIM + org_dir + Style.RESET_ALL + "] ")
    if user_org == '':
        user_org = org_dir

    print("\n" + Style.BRIGHT + Fore.GREEN +
          "The editor to use, blank to use $EDITOR from environment:")
    editor = input(Style.RESET_ALL + "[] ")

    cfg['TORGO'] = {}
    cfg['TORGO']['org_dir'] = user_org
    cfg['TORGO']['editor'] = editor
    with open(torgo_cfg, 'w') as f:
        cfg.write(f)


if must_init:
    init_config()