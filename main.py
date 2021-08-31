#!/usr/bin/env python3

from re import A
from jinja2 import Template, Environment, FileSystemLoader
import json
import subprocess
import shutil
from pathlib import Path

params={'problems':{}}
env = Environment(loader=FileSystemLoader('./', encoding='utf8'))
def make_testcase(category,name):
    path=category+"/"+name
    subprocess.call("library-checker-problems/generate.py --test -p {0}".format(name),shell=True)
    shutil.copytree("library-checker-problems/{0}/in".format(path),"build/{0}/in".format(path))
    shutil.copytree("library-checker-problems/{0}/out".format(path),"build/{0}/out".format(path))
    params['problems'].setdefault(category,[])
    params['problems'][category].append(name)
    make_problem_page(path)

def make_problem_page(path):
    problem_params={"dir":"{0}".format(path),"testcases":[]}
    for case in list(Path("build/{0}/in".format(path)).glob("*")):
        problem_params["testcases"].append(case.name[:-3])
    tmpl = env.get_template('templates/problem.html')
    with open('build/{0}.html'.format(path), 'w') as f:
        f.write(tmpl.render(problem_params))

def make_toppage():
    tmpl = env.get_template('templates/index.html')
    with open('build/index.html', 'w') as f:
        f.write(tmpl.render(params))

def main():
    tomls = list(filter(lambda p: not p.match('test/**/info.toml'),
                            Path('.').glob('**/info.toml')))
    tomls = sorted(tomls, key=lambda x: x.parent.name)
    for x in tomls:
        problem=x.parent
        make_testcase(problem.parent.name,problem.name)
    make_toppage()
if __name__ == '__main__':
    # main()
    make_testcase("datastructure","unionfind")
    make_toppage()