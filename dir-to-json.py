#!/usr/bin/python3
# USAGE: dir-to-json.py path/to/dir [ /path/to/background.jpg ]

import json
import shutil
import sys

from pathlib import Path

p = Path(sys.argv[1])
files = sorted([ str(f) for f in p.glob('*') ])

config = {}
pairs = []
for i in range(0, len(files), 2):
    pair = [ files[i], files[i+1] ]
    pairs.append(pair)

config["output"] = p.name + ".sb3"
config["pairs"] = pairs

if len(sys.argv) > 2:
    config["background"] = sys.argv[2]

print(json.dumps(config, indent=4))