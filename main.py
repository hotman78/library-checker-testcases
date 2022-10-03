#!/usr/bin/env python3

from re import A
from jinja2 import Template, Environment, FileSystemLoader
import subprocess
import shutil
from pathlib import Path
import toml
import json
import sys
import os

params = {'problems':{}}
env = Environment(loader=FileSystemLoader('./', encoding='utf8'))
version_hash = subprocess.run("git rev-parse HEAD",shell=True,cwd="./library-checker-problems",stdout=subprocess.PIPE).stdout.decode()
is_local = "--local" in sys.argv
with open('.cache.json') as f:
    hashlist = json.load(f)

def make_testcase(category,name):
    path=category+"/"+name
    tmp=path+('.local' if is_local else '.remote')
    if ( tmp in hashlist ) and hashlist[tmp].rstrip('\n') == "ignored":
        print("{} is ignored.".format(tmp))
        return False
    if ( tmp in hashlist ) and no_diff(hashlist[tmp].rstrip('\n'),version_hash.rstrip('\n'),path) :
        print("{} is cached.".format(tmp))
        return False
    hashlist[tmp]=version_hash
    if Path('build/{}'.format(path)).exists():
        shutil.rmtree('build/{}'.format(path))
    subprocess.call("library-checker-problems/generate.py --test -p {0}".format(name),shell=True)
    shutil.copytree("library-checker-problems/{0}/in".format(path),"build/{0}/in".format(path))
    shutil.copytree("library-checker-problems/{0}/out".format(path),"build/{0}/out".format(path))
    for name in Path("build/{0}/in".format(path)).glob('*.in'):
        shutil.move("build/{}/in/{}".format(path,name.name),'.'.join("build/{}/in/{}".format(path,name.name).split('.')[:-1])+".txt")
    for name in Path("build/{0}/out".format(path)).glob('*.out'):
        shutil.move("build/{}/out/{}".format(path,name.name),'.'.join("build/{}/out/{}".format(path,name.name).split('.')[:-1])+".txt")
    return True

def make_problem_page(category,name):
    params['problems'].setdefault(category,[])
    params['problems'][category].append(name)
    path=category+"/"+name
    problem_params={"dir":"{0}".format(name),"testcases":[]}
    tomls=toml.load("library-checker-problems/{0}/info.toml".format(path))
    for cases in tomls["tests"]:
        casename='.'.join(cases["name"].split('.')[:-1])
        for i in range(0,int(cases["number"])):
            problem_params["testcases"].append("{:s}_{:02d}".format(casename,i))
    tmpl = env.get_template('templates/problem.html')
    if not Path("build/{}".format(category)).exists():
        os.makedirs("build/{}".format(category))
    with open('build/{0}.html'.format(path), 'w') as f:
        f.write(tmpl.render(problem_params))

def make_toppage():
    tmpl = env.get_template('templates/index.html')
    with open('build/index.html', 'w') as f:
        f.write(tmpl.render(params))

def dump_hashlist():
    with open('.cache.json','w') as f:
        json.dump(hashlist, f, indent=4)

def no_diff(preSHA,SHA,path):
    res=subprocess.run("git diff {} {} --name-only  --relative={}".format(preSHA,SHA,path),shell=True,cwd="./library-checker-problems",stdout=subprocess.PIPE).stdout.decode()
    return res==''

def test():
    make_testcase("graph","tree_diameter")
    make_testcase("datastructure","unionfind")
    make_testcase("datastructure","associative_array")
    make_problem_page("graph","tree_diameter")
    make_problem_page("datastructure","unionfind")
    make_problem_page("datastructure","associative_array")
    make_toppage()
    dump_hashlist()

def main():
    tomls = list(filter(lambda p: not p.match('test/**/info.toml'),
                            Path('.').glob('**/info.toml')))
    tomls = sorted(tomls, key=lambda x: x.parent.name)
    for x in tomls:
        problem=x.parent
        changed=make_testcase(problem.parent.name,problem.name)
        make_problem_page(problem.parent.name,problem.name)
        if changed:
            break
    make_toppage()
    dump_hashlist()

if __name__ == '__main__':
    if is_local:test()
    else:main()
