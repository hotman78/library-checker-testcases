#!/usr/bin/env python3

import subprocess
import shutil
from pathlib import Path
def main(path):
    name=path.split('/')[-1]
    subprocess.call("library-checker-problems/generate.py --test -p {0}".format(name),shell=True)
    shutil.copytree("library-checker-problems/{0}/in".format(path),"build/{0}/in".format(path))
    shutil.copytree("library-checker-problems/{0}/out".format(path),"build/{0}/out".format(path))
tomls = list(filter(lambda p: not p.match('test/**/info.toml'),
                        Path('.').glob('**/info.toml')))
tomls = sorted(tomls, key=lambda x: x.parent.name)
for x in tomls:
    problem=x.parent
    main(problem.parent.name+"/"+problem.name)
