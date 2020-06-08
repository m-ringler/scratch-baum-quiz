#!/usr/bin/python3
# Adapts Quiz-Template so that it uses new images.
# Expects argv1 to be a json file with the following content:
#  {
#      "output": "path/to/quiz.sb3",
#      "background": "path/to/background-4-3-aspect-ratio.jpg", # this is optional
#      "pairs": [
#          [ "path/to/karte1.jpg", "path/to/feld1.png"],
#          [ "path/to/karte2.png", "/another/path/to/f2.jpeg" ]
#      ]
#  }

import hashlib
import json
import shutil
import sys
import tempfile

from pathlib import Path
from PIL import Image
from typing import Tuple, Optional

def md5_sum(fname: str) -> str:
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def load_json_file(path: str) -> dict:
    with open(path, encoding="utf-8") as f_in:
        return json.load(f_in)

def convert_image(input_image_file: str, output_dir: str, size: Optional[Tuple[int, int]] = None) -> Tuple[Path, int, int]:
    im = Image.open(input_image_file)
    if size is None:
        (w, h) = (im.width, im.height)
        scale = 300 / max(w, h)
        w = int(w * scale)
        h = int(h * scale)
    else:
        (w, h) = size

    im = Image.open(input_image_file)
    im = im.resize((w, h))
    input_path = Path(input_image_file)
    out_path = Path(output_dir, input_path.name)
    ext = out_path.suffix.lower()
    if ext == ".gif":
        out_path = out_path.with_suffix(".png")
    elif ext != '.png':
        out_path = out_path.with_suffix(".jpg")
    im.save(out_path)
    return out_path, w, h

def make_costume(f: str, size: Optional[Tuple[int, int]] = None) -> dict:
    # turn image into 300px png or jpg file
    tmpfile, width, height = convert_image(f, tmpdirname, size)
    ext = tmpfile.suffix

    # calculate the md5 of the converted image file
    md5 = md5_sum(tmpfile)
    md5ext = md5 + ext

    # set the name from the file name
    name = Path(f).stem

    # rename the converted image file
    tmpfile.rename(Path(tmpdirname, md5ext))

    # create a costume dictionary for the file
    costume = {
        "rotationCenterX": width / 2,
        "dataFormat": ext[1:],
        "name": name,
        "md5ext": md5ext,
        "bitmapResolution": 2,
        "assetId": md5,
        "rotationCenterY": height / 2
    }

    return costume


# load project.json
project = load_json_file("Quiz-Template/project.json")

# clear costumes
for i in range(1, 3):
    project["targets"][i]["costumes"].clear()

# load config.json
config = load_json_file(sys.argv[1])
pairs = config["pairs"]

# check value and range of "Anzahl Paare"
variable_id = 'M%Oy0BeTNCGc;vJ!l-sA'
n = len(pairs)

variable = project["targets"][0]["variables"][variable_id]
if n < variable[1]:
    variable[1] = n

for monitor in  project["monitors"]:
    if monitor["id"] == variable_id:
        if n < 3:
            monitor["visible"] = False
            monitor["value"] = n
        else:
            for x in [ "value", "sliderMin", "sliderMax" ]:
                if monitor[x] > n:
                    monitor[x] = n
        break

# for each pair in pairs
with tempfile.TemporaryDirectory() as tmpdirname:
    for pair in pairs:
        for i in range(2):
            costume = make_costume(pair[i])

            # append the costume dictionary to the "costumes" list
            project["targets"][i + 1]["costumes"].append(costume)

    # background
    if "background" in config:
        c = project["targets"][0]["costumes"]
        c.clear()

        costume = make_costume(config["background"], (960, 720))
        c.append(costume)

    # copy all files from template
    for f in Path("Quiz-Template").glob("*"):
        shutil.copy(f, tmpdirname)

    # write the project.json file
    with Path(tmpdirname, "project.json").open('w', encoding="utf-8") as fd:
        json.dump(project, fd, indent=4)

    # put everything into a zip file
    archive = shutil.make_archive(config["output"], 'zip', tmpdirname)

    # strip .zip from output name
    Path(archive).rename(config["output"])

print("Created Scratch Project in " + config["output"])

