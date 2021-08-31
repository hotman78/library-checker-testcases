#!/usr/bin/env python3

from re import A
from jinja2 import Template, Environment, FileSystemLoader
import subprocess
import shutil
from pathlib import Path
import toml

params={'problems':{}}
env = Environment(loader=FileSystemLoader('./', encoding='utf8'))
def make_testcase(category,name):
    path=category+"/"+name
    subprocess.call("library-checker-problems/generate.py --test -p {0}".format(name),shell=True)
    shutil.copytree("library-checker-problems/{0}/in".format(path),"build/{0}/in".format(path))
    shutil.copytree("library-checker-problems/{0}/out".format(path),"build/{0}/out".format(path))
    params['problems'].setdefault(category,[])
    params['problems'][category].append(name)
    make_problem_page(category,name)

def make_problem_page(category,name):
    path=category+"/"+name
    problem_params={"dir":"{0}".format(name),"testcases":[]}
    params=toml.load("library-checker-problems/{0}/info.toml".format(path))
    for cases in params["tests"]:
        casename='.'.join(cases["name"].split('.')[:-1])
        for i in range(0,int(cases["number"])):
            problem_params["testcases"].append("{:s}_{:02d}".format(casename,i))
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